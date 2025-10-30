from decimal import Decimal
from typing import Optional
from datetime import datetime, date
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, desc, func, extract

from app.core.deps import get_current_user, get_current_non_demo_user, get_db
from app.models.user import User
from app.models.budget import Budget
from app.models.category import Category
from app.models.transaction import Transaction, TransactionType
from app.schemas.budget import BudgetCreate, BudgetUpdate, BudgetResponse, BudgetListResponse

router = APIRouter()


def _budget_query(db: Session, current_user: User):
    return db.query(Budget).filter(
        Budget.user_id == current_user.id,
        Budget.is_demo_data.is_(current_user.is_demo),
    )


def _category_query(db: Session, current_user: User):
    return db.query(Category).filter(
        Category.user_id == current_user.id,
        Category.is_demo_data.is_(current_user.is_demo),
    )


def _transaction_query(db: Session, current_user: User):
    return db.query(Transaction).filter(
        Transaction.user_id == current_user.id,
        Transaction.is_demo_data.is_(current_user.is_demo),
    )

@router.get("/", response_model=BudgetListResponse)
async def list_budgets(
    skip: int = 0,
    limit: int = 100,
    categoria_id: Optional[str] = None,
    year: Optional[int] = None,
    month: Optional[int] = None,
    status: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Listar orçamentos do usuário com filtros opcionais"""
    query = _budget_query(db, current_user).options(
        joinedload(Budget.category)
    )
    
    # Aplicar filtros
    if categoria_id:
        query = query.filter(Budget.category_id == categoria_id)
    
    if year:
        query = query.filter(Budget.ano == year)
    
    if month:
        query = query.filter(Budget.mes == month)
    
    if status:
        # Calcular status baseado no gasto atual vs planejado
        # Isso seria melhor implementado como uma view ou computed field
        pass
    
    # Contar total
    total = query.count()
    
    # Aplicar paginação e ordenação
    budgets = query.order_by(desc(Budget.ano), desc(Budget.mes), Budget.category_id).offset(skip).limit(limit).all()
    
    # Atualizar valor realizado dinamicamente (sem persistir)
    for budget in budgets:
        gasto_realizado = (
            _transaction_query(db, current_user)
            .with_entities(func.coalesce(func.sum(Transaction.valor), 0))
            .filter(
                and_(
                    Transaction.category_id == budget.category_id,
                    Transaction.tipo == TransactionType.EXPENSE,
                    extract('year', Transaction.data_lancamento) == budget.ano,
                    extract('month', Transaction.data_lancamento) == budget.mes,
                )
            )
            .scalar()
        )

        realizado = Decimal(gasto_realizado or 0)
        if realizado < 0:
            realizado = realizado.copy_abs()

        budget.valor_realizado = realizado
    
    return BudgetListResponse(
        budgets=budgets,
        total=total,
        skip=skip,
        limit=limit
    )

@router.post("/", response_model=BudgetResponse, status_code=status.HTTP_201_CREATED)
async def create_budget(
    budget_data: BudgetCreate,
    current_user: User = Depends(get_current_non_demo_user),
    db: Session = Depends(get_db)
):
    """Criar novo orçamento"""
    # Verificar se categoria existe
    categoria = (
        _category_query(db, current_user)
        .filter(Category.id == budget_data.category_id)
        .first()
    )
    
    if not categoria:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Categoria não encontrada"
        )
    
    # Verificar se já existe orçamento para esta categoria no período
    existing = (
        _budget_query(db, current_user)
        .filter(
            and_(
                Budget.category_id == budget_data.category_id,
                Budget.ano == budget_data.ano,
                Budget.mes == budget_data.mes,
            )
        )
        .first()
    )
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Já existe um orçamento para esta categoria no período especificado"
        )
    
    # Criar orçamento
    budget = Budget(
        **budget_data.model_dump(),
        user_id=current_user.id,
        is_demo_data=current_user.is_demo
    )
    
    db.add(budget)
    db.commit()
    db.refresh(budget)
    
    return budget

@router.get("/{budget_id}", response_model=BudgetResponse)
async def get_budget(
    budget_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obter orçamento específico"""
    budget = (
        _budget_query(db, current_user)
        .options(joinedload(Budget.category))
        .filter(Budget.id == budget_id)
        .first()
    )
    
    if not budget:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Orçamento não encontrado"
        )
    
    # Calcular gasto realizado
    gasto_realizado = (
        _transaction_query(db, current_user)
        .with_entities(func.sum(Transaction.valor))
        .filter(
            Transaction.category_id == budget.category_id,
            Transaction.tipo == TransactionType.EXPENSE,
            extract('year', Transaction.data_lancamento) == budget.ano,
            extract('month', Transaction.data_lancamento) == budget.mes,
        )
        .scalar()
        or 0
    )
    
    budget.gasto_realizado = float(abs(gasto_realizado))
    budget.percentual_utilizado = (budget.gasto_realizado / budget.valor_planejado * 100) if budget.valor_planejado > 0 else 0
    
    return budget

@router.put("/{budget_id}", response_model=BudgetResponse)
async def update_budget(
    budget_id: str,
    budget_data: BudgetUpdate,
    current_user: User = Depends(get_current_non_demo_user),
    db: Session = Depends(get_db)
):
    """Atualizar orçamento"""
    budget = _budget_query(db, current_user).filter(Budget.id == budget_id).first()
    
    if not budget:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Orçamento não encontrado"
        )
    
    # Atualizar campos
    update_data = budget_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(budget, field, value)
    
    db.commit()
    db.refresh(budget)
    
    return budget

@router.delete("/{budget_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_budget(
    budget_id: str,
    current_user: User = Depends(get_current_non_demo_user),
    db: Session = Depends(get_db)
):
    """Excluir orçamento"""
    budget = _budget_query(db, current_user).filter(Budget.id == budget_id).first()
    
    if not budget:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Orçamento não encontrado"
        )
    
    db.delete(budget)
    db.commit()

@router.get("/summary/{year}/{month}")
async def get_budget_summary(
    year: int,
    month: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obter resumo de orçamentos para um período"""
    # Buscar todos os orçamentos do período
    budgets = (
        _budget_query(db, current_user)
        .options(joinedload(Budget.category))
        .filter(
            and_(
                Budget.ano == year,
                Budget.mes == month,
            )
        )
        .all()
    )
    
    total_planejado = Decimal("0")
    total_realizado = Decimal("0")
    orcamentos_detalhados = []
    
    for budget in budgets:
        gasto_realizado = (
            _transaction_query(db, current_user)
            .with_entities(func.coalesce(func.sum(Transaction.valor), 0))
            .filter(
                and_(
                    Transaction.category_id == budget.category_id,
                    Transaction.tipo == TransactionType.EXPENSE,
                    extract('year', Transaction.data_lancamento) == year,
                    extract('month', Transaction.data_lancamento) == month,
                )
            )
            .scalar()
        )

        realizado = Decimal(gasto_realizado or 0)
        if realizado < 0:
            realizado = realizado.copy_abs()

        planejado = Decimal(budget.valor_planejado or 0)
        percentual = float((realizado / planejado * 100) if planejado > 0 else 0.0)

        if percentual >= 100:
            status = "exceeded"
        elif percentual >= 80:
            status = "warning"
        else:
            status = "good"

        orcamentos_detalhados.append(
            {
                "id": str(budget.id),
                "categoria": budget.category.nome if budget.category else None,
                "categoria_cor": budget.category.cor if budget.category else None,
                "valor_planejado": float(planejado),
                "gasto_realizado": float(realizado),
                "percentual_utilizado": percentual,
                "valor_restante": float(planejado - realizado),
                "status": status,
            }
        )

        total_planejado += planejado
        total_realizado += realizado
    
    percentual_geral = float(
        (total_realizado / total_planejado * 100) if total_planejado > 0 else 0.0
    )
    
    # Contar status
    status_counts = {
        'good': len([o for o in orcamentos_detalhados if o['status'] == 'good']),
        'warning': len([o for o in orcamentos_detalhados if o['status'] == 'warning']),
        'exceeded': len([o for o in orcamentos_detalhados if o['status'] == 'exceeded'])
    }
    
    return {
        "year": year,
        "month": month,
        "total_planejado": total_planejado,
        "total_realizado": total_realizado,
        "percentual_geral": percentual_geral,
        "valor_restante": total_planejado - total_realizado,
        "status_counts": status_counts,
        "orcamentos": orcamentos_detalhados
    }

@router.post("/copy/{year}/{month}")
async def copy_budgets_from_previous_month(
    year: int,
    month: int,
    current_user: User = Depends(get_current_non_demo_user),
    db: Session = Depends(get_db)
):
    """Copiar orçamentos do mês anterior"""
    # Calcular mês anterior
    if month == 1:
        prev_year = year - 1
        prev_month = 12
    else:
        prev_year = year
        prev_month = month - 1
    
    # Buscar orçamentos do mês anterior
    prev_budgets = (
        _budget_query(db, current_user)
        .filter(
            and_(
                Budget.ano == prev_year,
                Budget.mes == prev_month,
            )
        )
        .all()
    )
    
    if not prev_budgets:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Nenhum orçamento encontrado no mês anterior"
        )
    
    # Verificar se já existem orçamentos no mês atual
    existing_budgets = (
        _budget_query(db, current_user)
        .filter(
            and_(
                Budget.ano == year,
                Budget.mes == month,
            )
        )
        .count()
    )
    
    if existing_budgets > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Já existem orçamentos para este período"
        )
    
    # Copiar orçamentos
    copied_count = 0
    for prev_budget in prev_budgets:
        new_budget = Budget(
            user_id=current_user.id,
            category_id=prev_budget.category_id,
            ano=year,
            mes=month,
            valor_planejado=prev_budget.valor_planejado,
            ativo=prev_budget.ativo,
            incluir_subcategorias=prev_budget.incluir_subcategorias,
            alerta_percentual=prev_budget.alerta_percentual,
            descricao=prev_budget.descricao,
            observacoes=prev_budget.observacoes,
            is_demo_data=current_user.is_demo,
        )
        db.add(new_budget)
        copied_count += 1
    
    db.commit()
    
    return {
        "message": f"{copied_count} orçamentos copiados com sucesso",
        "copied_count": copied_count,
        "target_year": year,
        "target_month": month
    }
