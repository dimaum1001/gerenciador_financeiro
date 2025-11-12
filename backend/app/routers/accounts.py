from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import and_, desc, or_
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, get_current_non_demo_user, get_db
from app.models.account import Account, AccountType
from app.models.user import User
from app.schemas.account import (
    AccountCreate,
    AccountListResponse,
    AccountResponse,
    AccountUpdate,
)
from app.utils.locale_mapper import account_type_mapper

router = APIRouter()


def _account_query(db: Session, current_user: User):
    return db.query(Account).filter(
        Account.user_id == current_user.id,
        Account.is_demo_data.is_(current_user.is_demo),
    )


@router.get("/", response_model=AccountListResponse)
async def list_accounts(
    skip: int = 0,
    limit: int = 100,
    tipo: Optional[str] = None,
    ativo: Optional[bool] = None,
    search: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Listar contas do usuário com filtros opcionais"""
    query = _account_query(db, current_user)

    # Aplicar filtros
    if tipo:
        try:
            tipo_enum = account_type_mapper.to_enum(tipo)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Tipo de conta inválido",
            )
        query = query.filter(Account.tipo == tipo_enum)

    if ativo is not None:
        query = query.filter(Account.ativo == ativo)

    if search:
        like_pattern = f"%{search}%"
        query = query.filter(
            or_(
                Account.nome.ilike(like_pattern),
                Account.banco.ilike(like_pattern),
                Account.descricao.ilike(like_pattern),
            )
        )

    # Contar total
    total = query.count()

    # Aplicar paginação e ordenação
    accounts = (
        query.order_by(desc(Account.atualizado_em)).offset(skip).limit(limit).all()
    )

    return AccountListResponse(
        accounts=accounts,
        total=total,
        skip=skip,
        limit=limit,
    )


@router.post("/", response_model=AccountResponse, status_code=status.HTTP_201_CREATED)
async def create_account(
    account_data: AccountCreate,
    current_user: User = Depends(get_current_non_demo_user),
    db: Session = Depends(get_db),
):
    """Criar nova conta"""
    # Verificar se já existe conta com mesmo nome
    existing = (
        _account_query(db, current_user)
        .filter(Account.nome == account_data.nome)
        .first()
    )

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Já existe uma conta com este nome",
        )

    # Criar conta
    account = Account(
        **account_data.model_dump(),
        user_id=current_user.id,
        is_demo_data=current_user.is_demo,
    )

    db.add(account)
    db.commit()
    db.refresh(account)

    return account


@router.get("/{account_id}", response_model=AccountResponse)
async def get_account(
    account_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Obter conta específica"""
    account = _account_query(db, current_user).filter(Account.id == account_id).first()

    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conta não encontrada",
        )

    return account


@router.put("/{account_id}", response_model=AccountResponse)
async def update_account(
    account_id: str,
    account_data: AccountUpdate,
    current_user: User = Depends(get_current_non_demo_user),
    db: Session = Depends(get_db),
):
    """Atualizar conta"""
    account = _account_query(db, current_user).filter(Account.id == account_id).first()

    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conta não encontrada",
        )

    # Verificar nome duplicado (se alterado)
    if account_data.nome and account_data.nome != account.nome:
        existing = (
        _account_query(db, current_user)
        .filter(
            and_(
                Account.nome == account_data.nome,
                Account.id != account_id,
            )
        )
        .first()
    )

        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Já existe uma conta com este nome",
            )

    # Atualizar campos
    update_data = account_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(account, field, value)

    db.commit()
    db.refresh(account)

    return account


@router.delete("/{account_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_account(
    account_id: str,
    current_user: User = Depends(get_current_non_demo_user),
    db: Session = Depends(get_db),
):
    """Excluir conta (soft delete)"""
    account = _account_query(db, current_user).filter(Account.id == account_id).first()

    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conta não encontrada",
        )

    # Verificar se há transações vinculadas
    from app.models.transaction import Transaction

    has_transactions = (
        db.query(Transaction)
        .filter(
            or_(
                Transaction.account_id == account_id,
                Transaction.transfer_account_id == account_id,
            )
        )
        .first()
    )

    if has_transactions:
        # Soft delete - apenas desativar
        account.ativo = False
        db.commit()
    else:
        # Hard delete se não há transações
        db.delete(account)
        db.commit()


@router.get("/{account_id}/balance")
async def get_account_balance(
    account_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Obter saldo atual da conta"""
    account = _account_query(db, current_user).filter(Account.id == account_id).first()

    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conta não encontrada",
        )

    return {
        "account_id": account_id,
        "account_name": account.nome,
        "balance": account.saldo_atual,
        "currency": account.moeda,
        "last_updated": account.atualizado_em,
    }
