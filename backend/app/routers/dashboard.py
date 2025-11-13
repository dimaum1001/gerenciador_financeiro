from typing import List, Optional
from datetime import datetime, date, timedelta
import calendar
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, func, extract, text

from app.core.deps import get_current_user, get_db
from app.models.user import User
from decimal import Decimal

from app.models.transaction import Transaction, TransactionType
from app.models.account import Account
from app.models.category import Category
from app.models.budget import Budget
from app.schemas.dashboard import (
    DashboardSummary,
    MonthlyFlow,
    CategorySummary,
    UpcomingExpense,
    BudgetStatusSummary,
    BudgetStatusItem,
)
from app.utils.locale_mapper import transaction_type_mapper

router = APIRouter()


def _account_query(db: Session, current_user: User):
    return db.query(Account).filter(
        Account.user_id == current_user.id,
        Account.is_demo_data.is_(current_user.is_demo),
    )


def _transaction_query(db: Session, current_user: User):
    return db.query(Transaction).filter(
        Transaction.user_id == current_user.id,
        Transaction.is_demo_data.is_(current_user.is_demo),
    )


def _category_query(db: Session, current_user: User):
    return db.query(Category).filter(
        Category.user_id == current_user.id,
        Category.is_demo_data.is_(current_user.is_demo),
    )


def _budget_query(db: Session, current_user: User):
    return db.query(Budget).filter(
        Budget.user_id == current_user.id,
        Budget.is_demo_data.is_(current_user.is_demo),
    )


@router.get("/summary", response_model=DashboardSummary)
async def get_dashboard_summary(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    now = datetime.now()
    current_month = now.month
    current_year = now.year

    total_balance = (
        _account_query(db, current_user)
        .with_entities(func.sum(Account.saldo_atual))
        .filter(Account.ativo.is_(True))
        .scalar()
        or 0
    )

    demo_condition = Transaction.is_demo_data.is_(current_user.is_demo)

    monthly_income = db.query(func.sum(Transaction.valor)).filter(
        and_(
            Transaction.user_id == current_user.id,
            demo_condition,
            Transaction.tipo == TransactionType.INCOME,
            extract("year", Transaction.data_lancamento) == current_year,
            extract("month", Transaction.data_lancamento) == current_month,
        )
    ).scalar() or Decimal("0")

    monthly_expenses = db.query(func.sum(Transaction.valor)).filter(
        and_(
            Transaction.user_id == current_user.id,
            demo_condition,
            Transaction.tipo == TransactionType.EXPENSE,
            extract("year", Transaction.data_lancamento) == current_year,
            extract("month", Transaction.data_lancamento) == current_month,
        )
    ).scalar() or Decimal("0")

    monthly_income = float(monthly_income)
    monthly_expenses = float(monthly_expenses)
    monthly_savings = monthly_income + monthly_expenses

    prev_month = current_month - 1 if current_month > 1 else 12
    prev_year = current_year if current_month > 1 else current_year - 1

    prev_income = db.query(func.sum(Transaction.valor)).filter(
        and_(
            Transaction.user_id == current_user.id,
            demo_condition,
            Transaction.tipo == TransactionType.INCOME,
            extract("year", Transaction.data_lancamento) == prev_year,
            extract("month", Transaction.data_lancamento) == prev_month,
        )
    ).scalar() or Decimal("0")

    prev_expenses = db.query(func.sum(Transaction.valor)).filter(
        and_(
            Transaction.user_id == current_user.id,
            demo_condition,
            Transaction.tipo == TransactionType.EXPENSE,
            extract("year", Transaction.data_lancamento) == prev_year,
            extract("month", Transaction.data_lancamento) == prev_month,
        )
    ).scalar() or Decimal("0")

    prev_income = float(prev_income)
    prev_expenses = float(prev_expenses)

    income_change = ((monthly_income - prev_income) / prev_income * 100) if prev_income != 0 else 0
    expenses_change = ((abs(monthly_expenses) - abs(prev_expenses)) / abs(prev_expenses) * 100) if prev_expenses != 0 else 0

    return DashboardSummary(
        total_balance=float(total_balance),
        monthly_income=monthly_income,
        monthly_expenses=float(abs(monthly_expenses)),
        monthly_savings=float(monthly_savings),
        income_change=float(income_change),
        expenses_change=float(expenses_change),
        current_month=current_month,
        current_year=current_year,
    )


@router.get("/cash-flow", response_model=List[MonthlyFlow])
async def get_cash_flow(
    months: int = Query(default=6, ge=1, le=24),
    year: Optional[int] = Query(default=None, ge=2000, le=2100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    now = datetime.now()
    flows: List[MonthlyFlow] = []

    if year:
        for month in range(1, 13):
            income = (
                _transaction_query(db, current_user)
                .with_entities(func.sum(Transaction.valor))
                .filter(
                    Transaction.tipo == TransactionType.INCOME,
                    extract("year", Transaction.data_lancamento) == year,
                    extract("month", Transaction.data_lancamento) == month,
                )
                .scalar()
                or Decimal("0")
            )

            expenses = (
                _transaction_query(db, current_user)
                .with_entities(func.sum(Transaction.valor))
                .filter(
                    Transaction.tipo == TransactionType.EXPENSE,
                    extract("year", Transaction.data_lancamento) == year,
                    extract("month", Transaction.data_lancamento) == month,
                )
                .scalar()
                or Decimal("0")
            )

            flows.append(
                MonthlyFlow(
                    month=month,
                    year=year,
                    month_name=datetime(year, month, 1).strftime("%b"),
                    income=float(income),
                    expenses=float(abs(expenses)),
                    balance=float(income + expenses),
                )
            )
        return flows

    for i in range(months):
        target_date = now - timedelta(days=30 * i)
        month = target_date.month
        year_value = target_date.year

        income = (
            _transaction_query(db, current_user)
            .with_entities(func.sum(Transaction.valor))
            .filter(
                Transaction.tipo == TransactionType.INCOME,
                extract("year", Transaction.data_lancamento) == year_value,
                extract("month", Transaction.data_lancamento) == month,
            )
            .scalar()
            or Decimal("0")
        )

        expenses = (
            _transaction_query(db, current_user)
            .with_entities(func.sum(Transaction.valor))
            .filter(
                Transaction.tipo == TransactionType.EXPENSE,
                extract("year", Transaction.data_lancamento) == year_value,
                extract("month", Transaction.data_lancamento) == month,
            )
            .scalar()
            or Decimal("0")
        )

        flows.append(
            MonthlyFlow(
                month=month,
                year=year_value,
                month_name=datetime(year_value, month, 1).strftime("%b"),
                income=float(income),
                expenses=float(abs(expenses)),
                balance=float(income + expenses),
            )
        )

    return list(reversed(flows))


# Categories summary

@router.get("/categories-summary", response_model=List[CategorySummary])
async def get_categories_summary(
    tipo: str = Query(..., regex="^(receita|despesa|income|expense)$"),
    year: int = Query(default=datetime.now().year),
    months: Optional[int] = Query(default=None, ge=1, le=60),
    month: Optional[int] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    tipo_enum = transaction_type_mapper.to_enum(tipo)

    query = (
        db.query(
            Category.nome.label("categoria"),
            Category.cor.label("cor"),
            func.sum(Transaction.valor).label("total"),
            func.count(Transaction.id).label("quantidade"),
        )
        .join(Transaction, Transaction.category_id == Category.id)
        .filter(
            Transaction.user_id == current_user.id,
            Transaction.is_demo_data.is_(current_user.is_demo),
            Transaction.tipo == tipo_enum,
            Category.is_demo_data.is_(current_user.is_demo),
        )
    )

    if months:
        now = datetime.now()
        start_year = now.year
        start_month = now.month - (months - 1)
        while start_month <= 0:
            start_month += 12
            start_year -= 1
        start_date = date(start_year, start_month, 1)
        last_day = calendar.monthrange(now.year, now.month)[1]
        end_date = date(now.year, now.month, last_day)
        query = query.filter(
            Transaction.data_lancamento >= start_date,
            Transaction.data_lancamento <= end_date,
        )
    else:
        query = query.filter(extract("year", Transaction.data_lancamento) == year)
        if month:
            query = query.filter(extract("month", Transaction.data_lancamento) == month)

    results = query.group_by(Category.id, Category.nome, Category.cor).all()
    total_value = sum(float(abs(row.total or 0)) for row in results)

    summaries = []
    for row in results:
        value = float(abs(row.total or 0))
        percentage = (value / total_value * 100) if total_value > 0 else 0
        summaries.append(
            CategorySummary(
                category=row.categoria,
                color=row.cor,
                value=value,
                quantity=int(row.quantidade or 0),
                percentage=float(percentage),
            )
        )

    return summaries


@router.get("/accounts-balance")
async def get_accounts_balance(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    accounts = _account_query(db, current_user).filter(Account.ativo.is_(True)).all()
    accounts_sorted = sorted(accounts, key=lambda acc: float(acc.saldo_atual or 0), reverse=True)
    total_balance = sum(float(acc.saldo_atual or 0) for acc in accounts_sorted)

    return [
        {
            "id": str(acc.id),
            "name": acc.nome,
            "type": acc.tipo,
            "balance": float(acc.saldo_atual or 0),
            "color": acc.cor,
            "percentage": (float(acc.saldo_atual or 0) / total_balance * 100) if total_balance > 0 else 0,
        }
        for acc in accounts_sorted
    ]


@router.get("/upcoming-bills", response_model=List[UpcomingExpense])
async def get_upcoming_bills(
    days: int = Query(default=30, ge=1, le=90),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    now = datetime.now()
    ninety_days_ago = now - timedelta(days=90)

    recurring_expenses = (
        _transaction_query(db, current_user)
        .with_entities(
            Transaction.descricao,
            Transaction.valor,
            Category.nome.label("categoria"),
            func.extract("day", Transaction.data_lancamento).label("dia_mes"),
        )
        .join(Category, Transaction.category_id == Category.id)
        .filter(
            Transaction.tipo == TransactionType.EXPENSE,
            Transaction.data_lancamento >= ninety_days_ago.date(),
            Category.is_demo_data.is_(current_user.is_demo),
        )
        .group_by(
            Transaction.descricao,
            Transaction.valor,
            Category.nome,
            func.extract("day", Transaction.data_lancamento),
        )
        .having(func.count(Transaction.id) >= 2)
        .all()
    )

    upcoming: List[UpcomingExpense] = []
    for expense in recurring_expenses:
        next_month = now.month + 1 if now.month < 12 else 1
        next_year = now.year if now.month < 12 else now.year + 1

        try:
            next_date = datetime(next_year, next_month, int(expense.dia_mes))
        except ValueError:
            continue

        days_until = (next_date - now).days
        if 0 <= days_until <= days:
            status = "pendente" if days_until >= 0 else "vencido"
            upcoming.append(
                UpcomingExpense(
                    description=expense.descricao,
                    amount=float(abs(expense.valor or 0)),
                    category=expense.categoria,
                    due_date=next_date.date(),
                    days_until=days_until,
                    status=status,
                )
            )

    upcoming.sort(key=lambda item: item.days_until)
    return upcoming


@router.get("/budget-status", response_model=BudgetStatusSummary)
async def get_budget_status(
    year: int = Query(default=datetime.now().year),
    month: int = Query(default=datetime.now().month),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    budgets = (
        _budget_query(db, current_user)
        .filter(Budget.ano == year, Budget.mes == month)
        .all()
    )

    if not budgets:
        return BudgetStatusSummary(
            total_planned=0.0,
            total_spent=0.0,
            percentage=0.0,
            remaining=0.0,
            status_counts={"good": 0, "warning": 0, "exceeded": 0},
            budgets=[],
        )

    total_planned = 0.0
    total_spent = 0.0
    status_counts = {"good": 0, "warning": 0, "exceeded": 0}
    budget_items: List[BudgetStatusItem] = []

    for budget in budgets:
        spent = (
            _transaction_query(db, current_user)
            .with_entities(func.sum(Transaction.valor))
            .filter(
                Transaction.category_id == budget.category_id,
                Transaction.tipo == TransactionType.EXPENSE,
                extract("year", Transaction.data_lancamento) == year,
                extract("month", Transaction.data_lancamento) == month,
            )
            .scalar()
            or Decimal("0")
        )

        spent_value = float(abs(spent))
        planned_value = float(budget.valor_planejado or 0)
        percentage = (spent_value / planned_value * 100) if planned_value > 0 else 0

        if percentage >= 100:
            status_label = "exceeded"
        elif percentage >= 80:
            status_label = "warning"
        else:
            status_label = "good"

        status_counts[status_label] += 1
        total_planned += planned_value
        total_spent += spent_value

        category = _category_query(db, current_user).filter(Category.id == budget.category_id).first()

        budget_items.append(
            BudgetStatusItem(
                id=budget.id,
                category=category.nome if category else "Categoria nao encontrada",
                category_color=category.cor if category else "#999999",
                planned=planned_value,
                spent=spent_value,
                percentage=float(percentage),
                remaining=planned_value - spent_value,
                status=status_label,
            )
        )

    overall_percentage = (total_spent / total_planned * 100) if total_planned > 0 else 0

    return BudgetStatusSummary(
        total_planned=total_planned,
        total_spent=total_spent,
        percentage=float(overall_percentage),
        remaining=total_planned - total_spent,
        status_counts=status_counts,
        budgets=budget_items,
    )
