"""
Utilitários para preparar dados de demonstração.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal

from sqlalchemy import inspect, text
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session

from app.core.security import get_password_hash
from app.models import (
    User,
    Account,
    AccountType,
    Category,
    CategoryType,
    Transaction,
    TransactionType,
    TransactionStatus,
    PaymentMethod,
)
from app.models.budget import Budget


DEMO_EMAIL = "admin@demo.com"
DEMO_PASSWORD = "admin123"


def ensure_demo_user(session: Session) -> None:
    """
    Garante que o usuário de demonstração exista com um conjunto básico de dados.

    Executado durante o startup. Caso o usuário já possua dados, nada é alterado.
    """
    _ensure_is_demo_column(session)
    _ensure_demo_data_columns(session)

    demo_user = session.query(User).filter(User.email == DEMO_EMAIL).first()

    if demo_user is None:
        demo_user = User(
            nome="Administrador Demo",
            email=DEMO_EMAIL,
            senha_hash=get_password_hash(DEMO_PASSWORD),
            telefone="(11) 99999-9999",
            ativo=True,
            email_verificado=True,
            is_demo=True,
            timezone="America/Sao_Paulo",
            moeda_padrao="BRL",
            formato_data="DD/MM/YYYY",
        )
        session.add(demo_user)
        session.commit()
        session.refresh(demo_user)
    elif not demo_user.is_demo:
        demo_user.is_demo = True
        session.commit()
        session.refresh(demo_user)

    _mark_demo_rows(session, demo_user.id)

    # Se já existem contas, assumimos que os dados foram populados.
    has_accounts = (
        session.query(Account)
        .filter(
            Account.user_id == demo_user.id,
            Account.is_demo_data.is_(True),
        )
        .count()
        > 0
    )
    if has_accounts:
        return

    # Gerar contas básicas
    accounts = [
        Account(
            user_id=demo_user.id,
            nome="Conta Corrente",
            tipo=AccountType.CHECKING,
            saldo_inicial=Decimal("4800.00"),
            descricao="Conta principal para movimentação",
            cor="#3b82f6",
            is_demo_data=True,
        ),
        Account(
            user_id=demo_user.id,
            nome="Poupança",
            tipo=AccountType.SAVINGS,
            saldo_inicial=Decimal("15000.00"),
            descricao="Reserva de emergência",
            cor="#10b981",
            is_demo_data=True,
        ),
        Account(
            user_id=demo_user.id,
            nome="Cartão de Crédito",
            tipo=AccountType.CREDIT,
            saldo_inicial=Decimal("-1250.00"),
            descricao="Cartão principal",
            cor="#8b5cf6",
            limite_credito=Decimal("5000.00"),
            dia_vencimento="15",
            dia_fechamento="10",
            is_demo_data=True,
        ),
    ]
    session.add_all(accounts)
    session.commit()

    # Categorias
    income_categories = [
        Category(
            user_id=demo_user.id,
            nome="Salário",
            tipo=CategoryType.INCOME,
            descricao="Receita mensal",
            cor="#16a34a",
            is_demo_data=True,
        ),
        Category(
            user_id=demo_user.id,
            nome="Freelance",
            tipo=CategoryType.INCOME,
            descricao="Trabalhos pontuais",
            cor="#0ea5e9",
            is_demo_data=True,
        ),
    ]
    session.add_all(income_categories)
    session.commit()

    expense_categories = []
    alimentos = Category(
        user_id=demo_user.id,
        nome="Alimentação",
        tipo=CategoryType.EXPENSE,
        descricao="Gastos com comida",
        cor="#ef4444",
        is_demo_data=True,
    )
    session.add(alimentos)
    session.commit()

    for name in ["Supermercado", "Restaurantes", "Delivery"]:
        expense_categories.append(
            Category(
                user_id=demo_user.id,
                nome=name,
                tipo=CategoryType.EXPENSE,
                parent_id=alimentos.id,
            )
        )

    moradia = Category(
        user_id=demo_user.id,
        nome="Moradia",
        tipo=CategoryType.EXPENSE,
        descricao="Custos da casa",
        cor="#f97316",
    )
    session.add(moradia)
    session.commit()

    expense_categories.extend(
        [
            Category(
                user_id=demo_user.id,
                nome="Aluguel",
                tipo=CategoryType.EXPENSE,
                parent_id=moradia.id,
            ),
            Category(
                user_id=demo_user.id,
                nome="Energia",
                tipo=CategoryType.EXPENSE,
                parent_id=moradia.id,
            ),
            Category(
                user_id=demo_user.id,
                nome="Internet",
                tipo=CategoryType.EXPENSE,
                parent_id=moradia.id,
            ),
        ]
    )
    session.add_all(expense_categories)
    session.commit()

    # Transações de exemplo
    account_map = {
        account.nome: account for account in session.query(Account).filter(Account.user_id == demo_user.id)
    }
    category_map = {
        category.nome: category
        for category in session.query(Category).filter(Category.user_id == demo_user.id)
    }

    transactions = [
        Transaction(
            user_id=demo_user.id,
            account_id=account_map["Conta Corrente"].id,
            category_id=category_map["Salário"].id,
            tipo=TransactionType.INCOME,
            valor=Decimal("5000.00"),
            moeda="BRL",
            data_lancamento=date(2024, 1, 5),
            descricao="Salário Janeiro",
            status=TransactionStatus.CLEARED,
            payment_method=PaymentMethod.TRANSFER,
            is_demo_data=True,
        ),
        Transaction(
            user_id=demo_user.id,
            account_id=account_map["Cartão de Crédito"].id,
            category_id=category_map["Supermercado"].id,
            tipo=TransactionType.EXPENSE,
            valor=Decimal("185.50"),
            moeda="BRL",
            data_lancamento=date(2024, 1, 12),
            descricao="Compras Supermercado",
            status=TransactionStatus.CLEARED,
            payment_method=PaymentMethod.CREDIT,
            is_demo_data=True,
        ),
        Transaction(
            user_id=demo_user.id,
            account_id=account_map["Conta Corrente"].id,
            category_id=category_map["Aluguel"].id,
            tipo=TransactionType.EXPENSE,
            valor=Decimal("1200.00"),
            moeda="BRL",
            data_lancamento=date(2024, 1, 10),
            descricao="Aluguel Janeiro",
            status=TransactionStatus.CLEARED,
            payment_method=PaymentMethod.TRANSFER,
            is_demo_data=True,
        ),
        Transaction(
            user_id=demo_user.id,
            account_id=account_map["Conta Corrente"].id,
            category_id=category_map["Energia"].id,
            tipo=TransactionType.EXPENSE,
            valor=Decimal("230.80"),
            moeda="BRL",
            data_lancamento=date(2024, 1, 18),
            descricao="Conta de Energia",
            status=TransactionStatus.PENDING,
            payment_method=PaymentMethod.DEBIT,
            is_demo_data=True,
        ),
    ]
    session.add_all(transactions)
    session.commit()

    # Orçamentos
    budgets = [
        Budget(
            user_id=demo_user.id,
            category_id=category_map["Alimentação"].id,
            ano=2024,
            mes=1,
            valor_planejado=Decimal("800.00"),
            valor_realizado=Decimal("650.00"),
            ativo=True,
            incluir_subcategorias=True,
            alerta_percentual=80,
            is_demo_data=True,
        ),
        Budget(
            user_id=demo_user.id,
            category_id=category_map["Moradia"].id,
            ano=2024,
            mes=1,
            valor_planejado=Decimal("1500.00"),
            valor_realizado=Decimal("1200.00"),
            ativo=True,
            incluir_subcategorias=True,
            alerta_percentual=85,
            is_demo_data=True,
        ),
    ]
    session.add_all(budgets)
    session.commit()



def _ensure_is_demo_column(session: Session) -> None:
    # Garante que a coluna is_demo exista no banco (necessario para bases antigas).
    bind = session.bind
    dialect_name = bind.dialect.name if bind is not None else ""

    if dialect_name != "sqlite":
        try:
            session.execute(
                text(
                    "ALTER TABLE IF EXISTS users "
                    "ADD COLUMN IF NOT EXISTS is_demo BOOLEAN NOT NULL DEFAULT FALSE"
                )
            )
            session.commit()
        except OperationalError:
            session.rollback()
            raise
        return

    inspector = inspect(bind)
    columns = {column["name"] for column in inspector.get_columns("users")}
    if "is_demo" in columns:
        return

    try:
        session.execute(
            text("ALTER TABLE users ADD COLUMN is_demo BOOLEAN NOT NULL DEFAULT FALSE")
        )
        session.commit()
    except OperationalError:
        session.rollback()
        raise


def _ensure_demo_data_columns(session: Session) -> None:
    # Garante que as colunas is_demo_data existam nas tabelas relacionadas.
    bind = session.bind
    dialect_name = bind.dialect.name if bind is not None else ""

    tables = ["accounts", "categories", "transactions", "budgets", "recurring_rules"]
    if dialect_name != "sqlite":
        try:
            for table in tables:
                session.execute(
                    text(
                        "ALTER TABLE IF EXISTS "
                        f"{table} ADD COLUMN IF NOT EXISTS "
                        "is_demo_data BOOLEAN NOT NULL DEFAULT FALSE"
                    )
                )
            session.commit()
        except OperationalError:
            session.rollback()
            raise
        return

    inspector = inspect(bind)
    for table in tables:
        columns = {column["name"] for column in inspector.get_columns(table)}
        if "is_demo_data" in columns:
            continue
        try:
            session.execute(
                text(
                    f"ALTER TABLE {table} ADD COLUMN is_demo_data BOOLEAN NOT NULL DEFAULT FALSE"
                )
            )
            session.commit()
        except OperationalError:
            session.rollback()
            raise


def _mark_demo_rows(session: Session, demo_user_id) -> None:
    """Marca linhas existentes do usuário demo como dados de demonstração."""
    if not demo_user_id:
        return

    for table in ["accounts", "categories", "transactions", "budgets", "recurring_rules"]:
        session.execute(
            text(f"UPDATE {table} SET is_demo_data = TRUE WHERE user_id = :user_id"),
            {"user_id": str(demo_user_id)},
        )
    session.commit()
