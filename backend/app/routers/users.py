"""
Router de usuários
"""

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.deps import get_db, get_current_user, get_current_non_demo_user
from app.core.security import get_password_hash, verify_password
from app.models.user import User
from app.schemas.user import (
    UserCreate, UserUpdate, UserChangePassword, 
    UserResponse, UserProfile, UserStats
)


router = APIRouter()


@router.get("", include_in_schema=False, response_model=list[UserResponse])
@router.get("/", response_model=list[UserResponse])
def list_users(
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Listar usuários disponíveis (apenas o usuário autenticado).
    """
    return [UserResponse.model_validate(current_user)]


@router.post("", include_in_schema=False, response_model=UserResponse, status_code=status.HTTP_201_CREATED)
@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(
    user_data: UserCreate,
    db: Session = Depends(get_db)
) -> Any:
    """
    Criar novo usuário
    
    Args:
        user_data: Dados do usuário
        db: Sessão do banco de dados
        
    Returns:
        UserResponse: Usuário criado
        
    Raises:
        HTTPException: Se email já existe
    """
    # Verificar se email já existe
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Criar usuário
    user = User(
        nome=user_data.nome,
        email=user_data.email,
        senha_hash=get_password_hash(user_data.senha),
        telefone=user_data.telefone,
        timezone=user_data.timezone,
        moeda_padrao=user_data.moeda_padrao,
        formato_data=user_data.formato_data
    )
    
    db.add(user)
    db.commit()
    db.refresh(user)
    
    return UserResponse.model_validate(user)


@router.get("/me", response_model=UserProfile)
def get_user_profile(
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Obter perfil completo do usuário atual
    
    Args:
        current_user: Usuário autenticado
        
    Returns:
        UserProfile: Perfil do usuário
    """
    return UserProfile.model_validate(current_user)


@router.put("/me", response_model=UserResponse)
def update_user_profile(
    user_data: UserUpdate,
    current_user: User = Depends(get_current_non_demo_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Atualizar perfil do usuário atual
    
    Args:
        user_data: Dados para atualização
        current_user: Usuário autenticado
        db: Sessão do banco de dados
        
    Returns:
        UserResponse: Usuário atualizado
    """
    # Atualizar campos fornecidos
    update_data = user_data.model_dump(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(current_user, field, value)
    
    db.commit()
    db.refresh(current_user)
    
    return UserResponse.model_validate(current_user)


@router.post("/me/change-password")
def change_password(
    password_data: UserChangePassword,
    current_user: User = Depends(get_current_non_demo_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Alterar senha do usuário atual
    
    Args:
        password_data: Senha atual e nova senha
        current_user: Usuário autenticado
        db: Sessão do banco de dados
        
    Returns:
        dict: Mensagem de confirmação
        
    Raises:
        HTTPException: Se senha atual incorreta
    """
    # Verificar senha atual
    if not verify_password(password_data.senha_atual, current_user.senha_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect current password"
        )
    
    # Atualizar senha
    current_user.senha_hash = get_password_hash(password_data.senha_nova)
    db.commit()
    
    return {"message": "Password updated successfully"}


@router.get("/me/stats", response_model=UserStats)
def get_user_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Obter estatísticas do usuário
    
    Args:
        current_user: Usuário autenticado
        db: Sessão do banco de dados
        
    Returns:
        UserStats: Estatísticas do usuário
    """
    from sqlalchemy import func
    from app.models.account import Account
    from app.models.category import Category
    from app.models.transaction import Transaction
    from app.models.budget import Budget
    
    # Contar registros
    total_contas = db.query(func.count(Account.id)).filter(
        Account.user_id == current_user.id,
        Account.is_demo_data.is_(current_user.is_demo)
    ).scalar() or 0

    total_categorias = db.query(func.count(Category.id)).filter(
        Category.user_id == current_user.id,
        Category.is_demo_data.is_(current_user.is_demo)
    ).scalar() or 0

    total_transacoes = db.query(func.count(Transaction.id)).filter(
        Transaction.user_id == current_user.id,
        Transaction.is_demo_data.is_(current_user.is_demo)
    ).scalar() or 0

    total_orcamentos = db.query(func.count(Budget.id)).filter(
        Budget.user_id == current_user.id,
        Budget.is_demo_data.is_(current_user.is_demo)
    ).scalar() or 0
    
    # Calcular saldo total (simplificado)
    saldo_total = db.query(func.sum(Account.saldo_inicial)).filter(
        Account.user_id == current_user.id,
        Account.ativo == True,
        Account.is_demo_data.is_(current_user.is_demo)
    ).scalar() or 0
    
    return UserStats(
        total_contas=total_contas,
        total_categorias=total_categorias,
        total_transacoes=total_transacoes,
        total_orcamentos=total_orcamentos,
        saldo_total=float(saldo_total)
    )


@router.delete("/me")
def delete_user_account(
    current_user: User = Depends(get_current_non_demo_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Excluir conta do usuário atual
    
    Args:
        current_user: Usuário autenticado
        db: Sessão do banco de dados
        
    Returns:
        dict: Mensagem de confirmação
    """
    # Marcar usuário como inativo ao invés de excluir
    current_user.ativo = False
    db.commit()
    
    return {"message": "Account deactivated successfully"}
