"""
Router de autenticação
"""

from datetime import datetime, timedelta
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import (
    create_access_token, verify_password, get_password_hash,
    generate_password_reset_token, verify_password_reset_token
)
from app.core.deps import get_db, get_current_user
from app.models.user import User
from app.schemas.auth import (
    LoginRequest, LoginResponse, PasswordResetRequest, 
    PasswordResetConfirm, ApiKeyResponse
)
from app.schemas.user import UserResponse


router = APIRouter()


@router.post("/login", response_model=LoginResponse)
def login(
    login_data: LoginRequest,
    db: Session = Depends(get_db)
) -> Any:
    """
    Login de usuário com email e senha
    
    Args:
        login_data: Dados de login (email e senha)
        db: Sessão do banco de dados
        
    Returns:
        LoginResponse: Token de acesso e dados do usuário
        
    Raises:
        HTTPException: Se credenciais inválidas
    """
    # Buscar usuário por email
    user = db.query(User).filter(User.email == login_data.email).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    # Verificar senha
    if not verify_password(login_data.senha, user.senha_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    # Verificar se usuário está ativo
    if not user.ativo:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )
    
    # Criar token de acesso
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        subject=str(user.id),
        expires_delta=access_token_expires
    )
    
    # Atualizar último login
    user.ultimo_login = datetime.utcnow()
    db.commit()
    
    return LoginResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=settings.access_token_expire_minutes * 60,  # em segundos
        user=UserResponse.model_validate(user)
    )


@router.post("/login/oauth", response_model=LoginResponse)
def login_oauth(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
) -> Any:
    """
    Login compatível com OAuth2 (para documentação Swagger)
    
    Args:
        form_data: Dados do formulário OAuth2
        db: Sessão do banco de dados
        
    Returns:
        LoginResponse: Token de acesso e dados do usuário
    """
    # Reutilizar lógica do login normal
    login_data = LoginRequest(email=form_data.username, senha=form_data.password)
    return login(login_data, db)


@router.get("/me", response_model=UserResponse)
def get_current_user_info(
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Obter informações do usuário atual
    
    Args:
        current_user: Usuário autenticado
        
    Returns:
        UserResponse: Dados do usuário atual
    """
    return UserResponse.model_validate(current_user)


@router.post("/password-reset")
def request_password_reset(
    reset_data: PasswordResetRequest,
    db: Session = Depends(get_db)
) -> Any:
    """
    Solicitar reset de senha
    
    Args:
        reset_data: Email para reset
        db: Sessão do banco de dados
        
    Returns:
        dict: Mensagem de confirmação
    """
    user = db.query(User).filter(User.email == reset_data.email).first()
    
    if not user or user.is_demo:
        # Por seguranca, sempre retorna sucesso mesmo se email nao existe ou se for conta demo
        return {"message": "Password reset email sent if account exists"}
    
    if not user.ativo:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )
    
    # Gerar token de reset
    reset_token = generate_password_reset_token(user.email)
    
    # TODO: Enviar email com token de reset
    # Por enquanto, apenas log do token (remover em produção)
    print(f"Password reset token for {user.email}: {reset_token}")
    
    return {"message": "Password reset email sent if account exists"}


@router.post("/password-reset/confirm")
def confirm_password_reset(
    reset_data: PasswordResetConfirm,
    db: Session = Depends(get_db)
) -> Any:
    """
    Confirmar reset de senha
    
    Args:
        reset_data: Token e nova senha
        db: Sessão do banco de dados
        
    Returns:
        dict: Mensagem de confirmação
        
    Raises:
        HTTPException: Se token inválido
    """
    email = verify_password_reset_token(reset_data.token)
    
    if not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired token"
        )
    
    user = db.query(User).filter(User.email == email).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    if user.is_demo:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuario de demonstracao nao permite reset de senha"
        )

    
    if not user.ativo:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )
    
    # Atualizar senha
    user.senha_hash = get_password_hash(reset_data.nova_senha)
    db.commit()
    
    return {"message": "Password updated successfully"}


@router.post("/refresh")
def refresh_token(
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Renovar token de acesso
    
    Args:
        current_user: Usuário autenticado
        
    Returns:
        LoginResponse: Novo token de acesso
    """
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        subject=str(current_user.id),
        expires_delta=access_token_expires
    )
    
    return LoginResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=settings.access_token_expire_minutes * 60,
        user=UserResponse.model_validate(current_user)
    )


@router.post("/logout")
def logout(
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Logout do usuário
    
    Note: Com JWT stateless, o logout é apenas informativo.
    O cliente deve descartar o token.
    
    Args:
        current_user: Usuário autenticado
        
    Returns:
        dict: Mensagem de confirmação
    """
    return {"message": "Successfully logged out"}


@router.post("/api-key", response_model=ApiKeyResponse)
def generate_api_key(
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Gerar chave de API para o usuário
    
    Args:
        current_user: Usuário autenticado
        
    Returns:
        ApiKeyResponse: Chave de API gerada
    """
    from app.core.security import create_api_key
    
    api_key = create_api_key()
    
    # TODO: Salvar API key no banco de dados com expiração
    # Por enquanto, apenas retorna a chave gerada
    
    return ApiKeyResponse(
        api_key=api_key,
        created_at=datetime.utcnow().isoformat(),
        expires_at=None  # Sem expiração por enquanto
    )
