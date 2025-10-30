from typing import Optional
from datetime import datetime, date
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_, desc, func, extract

from app.core.deps import get_current_user, get_current_non_demo_user, get_db
from app.models.user import User
from decimal import Decimal

from app.models.transaction import Transaction, TransactionType, TransactionStatus
from app.models.account import Account
from app.models.category import Category
from app.schemas.transaction import (
    TransactionCreate, TransactionUpdate, TransactionResponse, 
    TransactionListResponse, TransactionSummary
)

router = APIRouter()


def _transaction_query(db: Session, current_user: User):
    return db.query(Transaction).filter(
        Transaction.user_id == current_user.id,
        Transaction.is_demo_data.is_(current_user.is_demo),
    )


def _account_query(db: Session, current_user: User):
    return db.query(Account).filter(
        Account.user_id == current_user.id,
        Account.is_demo_data.is_(current_user.is_demo),
    )


def _category_query(db: Session, current_user: User):
    return db.query(Category).filter(
        Category.user_id == current_user.id,
        Category.is_demo_data.is_(current_user.is_demo),
    )

@router.get("/", response_model=TransactionListResponse)
async def list_transactions(
    skip: int = 0,
    limit: int = 50,
    tipo: Optional[str] = None,
    categoria_id: Optional[str] = None,
    conta_origem_id: Optional[str] = None,
    conta_destino_id: Optional[str] = None,
    status: Optional[str] = None,
    data_inicio: Optional[date] = None,
    data_fim: Optional[date] = None,
    valor_min: Optional[float] = None,
    valor_max: Optional[float] = None,
    search: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Listar transações do usuário com filtros avançados"""
    query = _transaction_query(db, current_user).options(
        joinedload(Transaction.category),
        joinedload(Transaction.account),
        joinedload(Transaction.transfer_account)
    )
    
    # Aplicar filtros
    if tipo:
        try:
            tipo_enum = TransactionType(tipo)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Tipo de transação inválido",
            )
        query = query.filter(Transaction.tipo == tipo_enum)
    
    if categoria_id:
        query = query.filter(Transaction.category_id == categoria_id)
    
    if conta_origem_id:
        query = query.filter(Transaction.account_id == conta_origem_id)
    
    if conta_destino_id:
        query = query.filter(Transaction.transfer_account_id == conta_destino_id)
    
    if status:
        try:
            status_enum = TransactionStatus(status)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Status de transação inválido",
            )
        query = query.filter(Transaction.status == status_enum)
    
    if data_inicio:
        query = query.filter(Transaction.data_lancamento >= data_inicio)
    
    if data_fim:
        query = query.filter(Transaction.data_lancamento <= data_fim)
    
    if valor_min is not None:
        query = query.filter(Transaction.valor >= Decimal(str(valor_min)))
    
    if valor_max is not None:
        query = query.filter(Transaction.valor <= Decimal(str(valor_max)))
    
    if search:
        query = query.filter(
            or_(
                Transaction.descricao.ilike(f"%{search}%"),
                Transaction.observacoes.ilike(f"%{search}%")
            )
        )
    
    # Contar total
    total = query.count()
    
    # Aplicar paginação e ordenação
    transactions = query.order_by(desc(Transaction.data_lancamento), desc(Transaction.criado_em)).offset(skip).limit(limit).all()
    
    return TransactionListResponse(
        transactions=transactions,
        total=total,
        skip=skip,
        limit=limit
    )

@router.post("/", response_model=TransactionResponse, status_code=status.HTTP_201_CREATED)
async def create_transaction(
    transaction_data: TransactionCreate,
    current_user: User = Depends(get_current_non_demo_user),
    db: Session = Depends(get_db)
):
    """Criar nova transação"""
    # Validar contas
    if transaction_data.account_id:
        conta_origem = (
            _account_query(db, current_user)
            .filter(Account.id == transaction_data.account_id)
            .first()
        )
        if not conta_origem:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Conta de origem não encontrada"
            )
    
    if transaction_data.transfer_account_id:
        conta_destino = (
            _account_query(db, current_user)
            .filter(Account.id == transaction_data.transfer_account_id)
            .first()
        )
        if not conta_destino:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Conta de destino não encontrada"
            )
    
    # Validar categoria
    if transaction_data.category_id:
        categoria = (
            _category_query(db, current_user)
            .filter(Category.id == transaction_data.category_id)
            .first()
        )
        if not categoria:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Categoria não encontrada"
            )
    
    # Criar transação
    transaction = Transaction(
        **transaction_data.model_dump(),
        user_id=current_user.id,
        is_demo_data=current_user.is_demo
    )
    
    db.add(transaction)
    db.commit()
    db.refresh(transaction)
    
    # Atualizar saldos das contas
    await _update_account_balances(transaction, db)
    
    return transaction

@router.get("/{transaction_id}", response_model=TransactionResponse)
async def get_transaction(
    transaction_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obter transação específica"""
    transaction = (
        _transaction_query(db, current_user)
        .options(
            joinedload(Transaction.category),
            joinedload(Transaction.account),
            joinedload(Transaction.transfer_account)
        )
        .filter(Transaction.id == transaction_id)
        .first()
    )
    
    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transação não encontrada"
        )
    
    return transaction

@router.put("/{transaction_id}", response_model=TransactionResponse)
async def update_transaction(
    transaction_id: str,
    transaction_data: TransactionUpdate,
    current_user: User = Depends(get_current_non_demo_user),
    db: Session = Depends(get_db)
):
    """Atualizar transação"""
    transaction = _transaction_query(db, current_user).filter(Transaction.id == transaction_id).first()
    
    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transação não encontrada"
        )
    
    # Reverter saldos antigos
    await _revert_account_balances(transaction, db)
    
    # Atualizar campos
    update_data = transaction_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(transaction, field, value)
    
    db.commit()
    db.refresh(transaction)
    
    # Aplicar novos saldos
    await _update_account_balances(transaction, db)
    
    return transaction

@router.delete("/{transaction_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_transaction(
    transaction_id: str,
    current_user: User = Depends(get_current_non_demo_user),
    db: Session = Depends(get_db)
):
    """Excluir transação"""
    transaction = _transaction_query(db, current_user).filter(Transaction.id == transaction_id).first()
    
    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transação não encontrada"
        )
    
    # Reverter saldos
    await _revert_account_balances(transaction, db)
    
    # Excluir transação
    db.delete(transaction)
    db.commit()

@router.get("/summary/monthly")
async def get_monthly_summary(
    year: int = Query(default=datetime.now().year),
    month: int = Query(default=datetime.now().month),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obter resumo mensal de transações"""
    demo_condition = Transaction.is_demo_data.is_(current_user.is_demo)
    # Receitas
    receitas = db.query(func.sum(Transaction.valor)).filter(
        and_(
            Transaction.user_id == current_user.id,
            demo_condition,
            Transaction.tipo == 'income',
            extract('year', Transaction.data_lancamento) == year,
            extract('month', Transaction.data_lancamento) == month
        )
    ).scalar() or 0
    
    # Despesas
    despesas = db.query(func.sum(Transaction.valor)).filter(
        and_(
            Transaction.user_id == current_user.id,
            demo_condition,
            Transaction.tipo == 'expense',
            extract('year', Transaction.data_lancamento) == year,
            extract('month', Transaction.data_lancamento) == month
        )
    ).scalar() or 0
    
    # Transferências
    transferencias = db.query(func.sum(Transaction.valor)).filter(
        and_(
            Transaction.user_id == current_user.id,
            demo_condition,
            Transaction.tipo == 'transfer',
            extract('year', Transaction.data_lancamento) == year,
            extract('month', Transaction.data_lancamento) == month
        )
    ).scalar() or 0
    
    return {
        "year": year,
        "month": month,
        "receitas": float(receitas),
        "despesas": float(abs(despesas)),
        "transferencias": float(transferencias),
        "saldo": float(receitas + despesas),  # despesas já são negativas
        "economia": float(receitas + despesas) if receitas > 0 else 0
    }

@router.get("/summary/by-category")
async def get_summary_by_category(
    tipo: str = Query(..., regex="^(income|expense)$"),
    year: int = Query(default=datetime.now().year),
    month: Optional[int] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obter resumo por categoria"""
    demo_condition = Transaction.is_demo_data.is_(current_user.is_demo)
    query = db.query(
        Category.nome.label('categoria'),
        Category.cor.label('cor'),
        func.sum(Transaction.valor).label('total'),
        func.count(Transaction.id).label('quantidade')
    ).join(
        Transaction, Transaction.category_id == Category.id
    ).filter(
        and_(
            Transaction.user_id == current_user.id,
            demo_condition,
            Transaction.tipo == tipo,
            extract('year', Transaction.data_lancamento) == year
        )
    ).filter(Category.is_demo_data.is_(current_user.is_demo))
    
    if month:
        query = query.filter(extract('month', Transaction.data_lancamento) == month)
    
    results = query.group_by(Category.id, Category.nome, Category.cor).all()
    
    total_geral = sum(float(r.total) for r in results)
    
    return [
        {
            "categoria": r.categoria,
            "cor": r.cor,
            "valor": float(abs(r.total)),
            "quantidade": r.quantidade,
            "percentual": (float(abs(r.total)) / total_geral * 100) if total_geral > 0 else 0
        }
        for r in results
    ]

def _apply_account_balances(transaction: Transaction, db: Session, multiplier: int) -> None:
    """Aplica variação de saldo nas contas envolvidas.

    Atualmente os saldos são calculados dinamicamente a partir das transações.
    Portanto esta função é um no-op mantido apenas para compatibilidade.
    """
    return None


async def _update_account_balances(transaction: Transaction, db: Session) -> None:
    """Aplica o efeito da transação nas contas."""
    _apply_account_balances(transaction, db, multiplier=1)


async def _revert_account_balances(transaction: Transaction, db: Session) -> None:
    """Reverte o efeito da transação nas contas."""
    _apply_account_balances(transaction, db, multiplier=-1)
