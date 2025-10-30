#!/usr/bin/env python3
"""
Script para popular o banco de dados com dados de exemplo realistas
"""

import os
import sys
import uuid
from datetime import datetime, date, timedelta
from decimal import Decimal
import random

# Adicionar o diretório raiz ao path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from sqlalchemy.orm import Session
from app.core.security import get_password_hash
from app.db.session import get_db_context
from app.models import (
    User, Account, Category, Transaction, Budget, RecurringRule,
    AccountType, CategoryType, TransactionType, TransactionStatus, 
    PaymentMethod, RecurrenceFrequency, RecurrenceStatus
)


def create_demo_user(db: Session) -> User:
    """Criar usuário de demonstração"""
    print("Criando usuário de demonstração...")
    
    # Verificar se já existe
    existing_user = db.query(User).filter(User.email == "admin@demo.com").first()
    if existing_user:
        print("Usuário de demonstração já existe")
        return existing_user
    
    user = User(
        nome="Administrador Demo",
        email="admin@demo.com",
        senha_hash=get_password_hash("admin123"),
        telefone="(11) 99999-9999",
        ativo=True,
        email_verificado=True,
        is_demo=True,
        timezone="America/Sao_Paulo",
        moeda_padrao="BRL",
        formato_data="DD/MM/YYYY"
    )
    
    db.add(user)
    db.commit()
    db.refresh(user)
    
    print(f"Usuário criado: {user.email}")
    return user


def create_demo_accounts(db: Session, user: User) -> list[Account]:
    """Criar contas de demonstração"""
    print("Criando contas de demonstração...")
    
    accounts_data = [
        {
            "nome": "Carteira",
            "tipo": AccountType.CASH,
            "saldo_inicial": Decimal("500.00"),
            "cor": "#10b981",
            "icone": "wallet",
            "descricao": "Dinheiro em especie",
            "is_demo_data": True,
        },
        {
            "nome": "Conta Corrente Banco do Brasil",
            "tipo": AccountType.CHECKING,
            "saldo_inicial": Decimal("8500.00"),
            "cor": "#3b82f6",
            "icone": "building-bank",
            "descricao": "Conta principal para movimentacao",
            "banco": "Banco do Brasil",
            "agencia": "1234-5",
            "conta": "12345-6",
            "is_demo_data": True,
        },
        {
            "nome": "Poupanca Caixa",
            "tipo": AccountType.SAVINGS,
            "saldo_inicial": Decimal("15000.00"),
            "cor": "#059669",
            "icone": "piggy-bank",
            "descricao": "Reserva de emergencia",
            "banco": "Caixa Economica Federal",
            "agencia": "0987",
            "conta": "98765-4",
            "is_demo_data": True,
        },
        {
            "nome": "Cartao Nubank",
            "tipo": AccountType.CREDIT,
            "saldo_inicial": Decimal("0.00"),
            "cor": "#8b5cf6",
            "icone": "credit-card",
            "descricao": "Cartao de credito principal",
            "banco": "Nubank",
            "limite_credito": Decimal("5000.00"),
            "dia_vencimento": "15",
            "dia_fechamento": "10",
            "is_demo_data": True,
        },
        {
            "nome": "Investimentos XP",
            "tipo": AccountType.INVESTMENT,
            "saldo_inicial": Decimal("25000.00"),
            "cor": "#f59e0b",
            "icone": "trending-up",
            "descricao": "Carteira de investimentos",
            "banco": "XP Investimentos",
            "is_demo_data": True,
        },
    ]
    accounts = []
    for account_data in accounts_data:
        account = Account(
            user_id=user.id,
            **account_data
        )
        db.add(account)
        accounts.append(account)
    
    db.commit()
    
    for account in accounts:
        db.refresh(account)
        print(f"Conta criada: {account.nome}")
    
    return accounts


def create_demo_categories(db: Session, user: User) -> list[Category]:
    """Criar categorias de demonstração"""
    print("Criando categorias de demonstração...")
    
    # Categorias de receita
    income_categories = [
        {
            "nome": "Salário",
            "tipo": CategoryType.INCOME,
            "cor": "#10b981",
            "icone": "banknote",
            "descricao": "Salário mensal"
        },
        {
            "nome": "Freelance",
            "tipo": CategoryType.INCOME,
            "cor": "#059669",
            "icone": "briefcase",
            "descricao": "Trabalhos freelance"
        },
        {
            "nome": "Investimentos",
            "tipo": CategoryType.INCOME,
            "cor": "#0d9488",
            "icone": "trending-up",
            "descricao": "Rendimentos de investimentos"
        },
        {
            "nome": "Outros",
            "tipo": CategoryType.INCOME,
            "cor": "#14b8a6",
            "icone": "plus-circle",
            "descricao": "Outras receitas"
        }
    ]
    
    # Categorias de despesa
    expense_categories = [
        {
            "nome": "Alimentação",
            "tipo": CategoryType.EXPENSE,
            "cor": "#ef4444",
            "icone": "utensils",
            "descricao": "Gastos com alimentação",
            "subcategorias": [
                {"nome": "Supermercado", "cor": "#dc2626", "icone": "shopping-cart"},
                {"nome": "Restaurantes", "cor": "#b91c1c", "icone": "chef-hat"},
                {"nome": "Delivery", "cor": "#991b1b", "icone": "truck"}
            ]
        },
        {
            "nome": "Moradia",
            "tipo": CategoryType.EXPENSE,
            "cor": "#f97316",
            "icone": "home",
            "descricao": "Gastos com moradia",
            "subcategorias": [
                {"nome": "Aluguel", "cor": "#ea580c", "icone": "key"},
                {"nome": "Condomínio", "cor": "#dc2626", "icone": "building"},
                {"nome": "Energia", "cor": "#c2410c", "icone": "zap"},
                {"nome": "Água", "cor": "#9a3412", "icone": "droplets"},
                {"nome": "Internet", "cor": "#7c2d12", "icone": "wifi"}
            ]
        },
        {
            "nome": "Transporte",
            "tipo": CategoryType.EXPENSE,
            "cor": "#3b82f6",
            "icone": "car",
            "descricao": "Gastos com transporte",
            "subcategorias": [
                {"nome": "Combustível", "cor": "#2563eb", "icone": "fuel"},
                {"nome": "Uber/Taxi", "cor": "#1d4ed8", "icone": "car"},
                {"nome": "Transporte Público", "cor": "#1e40af", "icone": "bus"},
                {"nome": "Manutenção", "cor": "#1e3a8a", "icone": "wrench"}
            ]
        },
        {
            "nome": "Saúde",
            "tipo": CategoryType.EXPENSE,
            "cor": "#06b6d4",
            "icone": "heart",
            "descricao": "Gastos com saúde",
            "subcategorias": [
                {"nome": "Plano de Saúde", "cor": "#0891b2", "icone": "shield"},
                {"nome": "Medicamentos", "cor": "#0e7490", "icone": "pill"},
                {"nome": "Consultas", "cor": "#155e75", "icone": "stethoscope"}
            ]
        },
        {
            "nome": "Lazer",
            "tipo": CategoryType.EXPENSE,
            "cor": "#8b5cf6",
            "icone": "gamepad-2",
            "descricao": "Gastos com entretenimento",
            "subcategorias": [
                {"nome": "Cinema", "cor": "#7c3aed", "icone": "film"},
                {"nome": "Streaming", "cor": "#6d28d9", "icone": "play"},
                {"nome": "Viagens", "cor": "#5b21b6", "icone": "plane"},
                {"nome": "Hobbies", "cor": "#4c1d95", "icone": "palette"}
            ]
        },
        {
            "nome": "Educação",
            "tipo": CategoryType.EXPENSE,
            "cor": "#ec4899",
            "icone": "graduation-cap",
            "descricao": "Gastos com educação",
            "subcategorias": [
                {"nome": "Cursos", "cor": "#db2777", "icone": "book"},
                {"nome": "Livros", "cor": "#be185d", "icone": "book-open"}
            ]
        },
        {
            "nome": "Vestuário",
            "tipo": CategoryType.EXPENSE,
            "cor": "#f59e0b",
            "icone": "shirt",
            "descricao": "Gastos com roupas e acessórios"
        },
        {
            "nome": "Impostos",
            "tipo": CategoryType.EXPENSE,
            "cor": "#6b7280",
            "icone": "receipt",
            "descricao": "Impostos e taxas"
        }
    ]
    
    categories = []
    
    # Criar categorias de receita
    for cat_data in income_categories:
        category = Category(
            user_id=user.id,
            **cat_data
        )
        db.add(category)
        categories.append(category)
    
    # Criar categorias de despesa
    for cat_data in expense_categories:
        subcategorias = cat_data.pop("subcategorias", [])
        
        # Criar categoria pai
        parent_category = Category(
            user_id=user.id,
            **cat_data
        )
        db.add(parent_category)
        categories.append(parent_category)
        
        # Commit para obter o ID da categoria pai
        db.commit()
        db.refresh(parent_category)
        
        # Criar subcategorias
        for subcat_data in subcategorias:
            subcategory = Category(
                user_id=user.id,
                parent_id=parent_category.id,
                tipo=CategoryType.EXPENSE,
                descricao=f"Subcategoria de {parent_category.nome}",
                **subcat_data
            )
            db.add(subcategory)
            categories.append(subcategory)
    
    db.commit()
    
    for category in categories:
        db.refresh(category)
        print(f"Categoria criada: {category.nome_completo}")
    
    return categories


def create_demo_transactions(db: Session, user: User, accounts: list[Account], categories: list[Category]) -> list[Transaction]:
    """Criar transações de demonstração dos últimos 6 meses"""
    print("Criando transações de demonstração...")
    
    # Separar categorias por tipo
    income_categories = [c for c in categories if c.tipo == CategoryType.INCOME]
    expense_categories = [c for c in categories if c.tipo == CategoryType.EXPENSE and not c.is_parent]
    
    # Contas por tipo
    cash_accounts = [a for a in accounts if a.tipo in [AccountType.CASH, AccountType.CHECKING]]
    credit_accounts = [a for a in accounts if a.tipo == AccountType.CREDIT]
    
    transactions = []
    
    # Gerar transações dos últimos 6 meses
    start_date = date.today() - timedelta(days=180)
    current_date = start_date
    
    while current_date <= date.today():
        # Receitas mensais (salário no dia 5)
        if current_date.day == 5:
            salary_transaction = Transaction(
                user_id=user.id,
                account_id=cash_accounts[1].id,  # Conta corrente
                category_id=next(c.id for c in income_categories if c.nome == "Salário"),
                tipo=TransactionType.INCOME,
                valor=Decimal("5000.00"),
                data_lancamento=current_date,
                data_competencia=current_date,
                descricao="Salário mensal",
                status=TransactionStatus.CLEARED,
                payment_method=PaymentMethod.TRANSFER
            )
            db.add(salary_transaction)
            transactions.append(salary_transaction)
        
        # Freelance ocasional
        if random.random() < 0.3:  # 30% de chance
            freelance_transaction = Transaction(
                user_id=user.id,
                account_id=cash_accounts[1].id,
                category_id=next(c.id for c in income_categories if c.nome == "Freelance"),
                tipo=TransactionType.INCOME,
                valor=Decimal(str(random.uniform(500, 2000))),
                data_lancamento=current_date,
                descricao=f"Projeto freelance - {random.choice(['Website', 'App', 'Consultoria', 'Design'])}",
                status=TransactionStatus.CLEARED,
                payment_method=PaymentMethod.PIX
            )
            db.add(freelance_transaction)
            transactions.append(freelance_transaction)
        
        # Despesas diárias
        if random.random() < 0.7:  # 70% de chance de ter despesa no dia
            # Escolher categoria aleatória
            category = random.choice(expense_categories)
            account = random.choice(cash_accounts + credit_accounts)
            
            # Valores típicos por categoria
            valor_ranges = {
                "Supermercado": (50, 200),
                "Restaurantes": (25, 80),
                "Delivery": (20, 50),
                "Combustível": (80, 150),
                "Uber/Taxi": (15, 40),
                "Transporte Público": (5, 15),
                "Cinema": (20, 40),
                "Streaming": (15, 50),
                "Medicamentos": (20, 100),
                "Vestuário": (50, 300)
            }
            
            min_val, max_val = valor_ranges.get(category.nome, (10, 100))
            valor = Decimal(str(random.uniform(min_val, max_val)))
            
            # Método de pagamento baseado no tipo de conta
            if account.tipo == AccountType.CREDIT:
                payment_method = PaymentMethod.CREDIT
            elif category.nome in ["Supermercado", "Combustível"]:
                payment_method = random.choice([PaymentMethod.DEBIT, PaymentMethod.PIX])
            else:
                payment_method = random.choice([PaymentMethod.CASH, PaymentMethod.PIX, PaymentMethod.DEBIT])
            
            transaction = Transaction(
                user_id=user.id,
                account_id=account.id,
                category_id=category.id,
                tipo=TransactionType.EXPENSE,
                valor=valor,
                data_lancamento=current_date,
                descricao=f"{category.nome} - {random.choice(['Compra', 'Pagamento', 'Serviço'])}",
                status=random.choice([TransactionStatus.CLEARED, TransactionStatus.PENDING]),
                payment_method=payment_method,
                tags=[category.nome.lower(), random.choice(["essencial", "opcional", "urgente"])]
            )
            db.add(transaction)
            transactions.append(transaction)
        
        # Despesas mensais fixas
        if current_date.day == 10:  # Aluguel
            aluguel_cat = next((c for c in expense_categories if c.nome == "Aluguel"), None)
            if aluguel_cat:
                aluguel_transaction = Transaction(
                    user_id=user.id,
                    account_id=cash_accounts[1].id,
                    category_id=aluguel_cat.id,
                    tipo=TransactionType.EXPENSE,
                    valor=Decimal("1200.00"),
                    data_lancamento=current_date,
                    descricao="Aluguel mensal",
                    status=TransactionStatus.CLEARED,
                    payment_method=PaymentMethod.TRANSFER
                )
                db.add(aluguel_transaction)
                transactions.append(aluguel_transaction)
        
        if current_date.day == 15:  # Contas de consumo
            contas = [
                ("Energia", Decimal(str(random.uniform(80, 150)))),
                ("Água", Decimal(str(random.uniform(40, 80)))),
                ("Internet", Decimal("89.90"))
            ]
            
            for conta_nome, valor in contas:
                conta_cat = next((c for c in expense_categories if c.nome == conta_nome), None)
                if conta_cat:
                    conta_transaction = Transaction(
                        user_id=user.id,
                        account_id=cash_accounts[1].id,
                        category_id=conta_cat.id,
                        tipo=TransactionType.EXPENSE,
                        valor=valor,
                        data_lancamento=current_date,
                        descricao=f"Conta de {conta_nome.lower()}",
                        status=TransactionStatus.CLEARED,
                        payment_method=PaymentMethod.BOLETO
                    )
                    db.add(conta_transaction)
                    transactions.append(conta_transaction)
        
        current_date += timedelta(days=1)
    
    db.commit()
    
    for transaction in transactions:
        db.refresh(transaction)
    
    print(f"Criadas {len(transactions)} transações")
    return transactions


def create_demo_budgets(db: Session, user: User, categories: list[Category]) -> list[Budget]:
    """Criar orçamentos de demonstração"""
    print("Criando orçamentos de demonstração...")
    
    # Categorias principais de despesa para orçamento
    budget_categories = [
        ("Alimentação", Decimal("800.00")),
        ("Moradia", Decimal("1500.00")),
        ("Transporte", Decimal("400.00")),
        ("Saúde", Decimal("300.00")),
        ("Lazer", Decimal("500.00")),
        ("Educação", Decimal("200.00")),
        ("Vestuário", Decimal("300.00"))
    ]
    
    budgets = []
    current_month = date.today().month
    current_year = date.today().year
    
    for cat_name, valor_planejado in budget_categories:
        category = next((c for c in categories if c.nome == cat_name and c.tipo == CategoryType.EXPENSE), None)
        if category:
            budget = Budget(
                user_id=user.id,
                category_id=category.id,
                ano=current_year,
                mes=current_month,
                valor_planejado=valor_planejado,
                valor_realizado=Decimal(str(random.uniform(float(valor_planejado) * 0.3, float(valor_planejado) * 1.1))),
                ativo=True,
                incluir_subcategorias=True,
                alerta_percentual=80,
                descricao=f"Orçamento para {cat_name} - {current_month:02d}/{current_year}"
            )
            db.add(budget)
            budgets.append(budget)
    
    db.commit()
    
    for budget in budgets:
        db.refresh(budget)
        print(f"Orçamento criado: {budget.category.nome} - R$ {budget.valor_planejado}")
    
    return budgets


def create_demo_recurring_rules(db: Session, user: User, accounts: list[Account], categories: list[Category]) -> list[RecurringRule]:
    """Criar regras de recorrência de demonstração"""
    print("Criando regras de recorrência...")
    
    # Contas
    conta_corrente = next(a for a in accounts if a.tipo == AccountType.CHECKING)
    
    # Categorias
    salary_cat = next(c for c in categories if c.nome == "Salário")
    aluguel_cat = next((c for c in categories if c.nome == "Aluguel"), None)
    internet_cat = next((c for c in categories if c.nome == "Internet"), None)
    
    recurring_rules = []
    
    # Salário mensal
    salary_rule = RecurringRule(
        user_id=user.id,
        account_id=conta_corrente.id,
        category_id=salary_cat.id,
        nome="Salário Mensal",
        descricao_template="Salário do mês",
        tipo="income",
        valor=Decimal("5000.00"),
        payment_method="transfer",
        frequencia=RecurrenceFrequency.MONTHLY,
        intervalo=1,
        dia_do_mes=5,
        data_inicio=date.today().replace(day=1),
        status=RecurrenceStatus.ACTIVE,
        ativo=True,
        observacoes="Salário depositado todo dia 5"
    )
    db.add(salary_rule)
    recurring_rules.append(salary_rule)
    
    # Aluguel mensal
    if aluguel_cat:
        aluguel_rule = RecurringRule(
            user_id=user.id,
            account_id=conta_corrente.id,
            category_id=aluguel_cat.id,
            nome="Aluguel",
            descricao_template="Aluguel mensal",
            tipo="expense",
            valor=Decimal("1200.00"),
            payment_method="transfer",
            frequencia=RecurrenceFrequency.MONTHLY,
            intervalo=1,
            dia_do_mes=10,
            data_inicio=date.today().replace(day=1),
            status=RecurrenceStatus.ACTIVE,
            ativo=True,
            observacoes="Aluguel vence todo dia 10"
        )
        db.add(aluguel_rule)
        recurring_rules.append(aluguel_rule)
    
    # Internet mensal
    if internet_cat:
        internet_rule = RecurringRule(
            user_id=user.id,
            account_id=conta_corrente.id,
            category_id=internet_cat.id,
            nome="Internet",
            descricao_template="Conta de internet",
            tipo="expense",
            valor=Decimal("89.90"),
            payment_method="boleto",
            frequencia=RecurrenceFrequency.MONTHLY,
            intervalo=1,
            dia_do_mes=15,
            data_inicio=date.today().replace(day=1),
            status=RecurrenceStatus.ACTIVE,
            ativo=True,
            observacoes="Internet vence todo dia 15"
        )
        db.add(internet_rule)
        recurring_rules.append(internet_rule)
    
    db.commit()
    
    for rule in recurring_rules:
        db.refresh(rule)
        print(f"Regra de recorrência criada: {rule.nome}")
    
    return recurring_rules


def main():
    """Função principal para executar o seed"""
    print("🌱 Iniciando seed do banco de dados...")
    
    try:
        with get_db_context() as db:
            # Criar usuário demo
            user = create_demo_user(db)
            
            # Criar contas
            accounts = create_demo_accounts(db, user)
            
            # Criar categorias
            categories = create_demo_categories(db, user)
            
            # Criar transações
            transactions = create_demo_transactions(db, user, accounts, categories)
            
            # Criar orçamentos
            budgets = create_demo_budgets(db, user, categories)
            
            # Criar regras de recorrência
            recurring_rules = create_demo_recurring_rules(db, user, accounts, categories)
            
            print("\n✅ Seed concluído com sucesso!")
            print(f"📊 Resumo:")
            print(f"   - 1 usuário")
            print(f"   - {len(accounts)} contas")
            print(f"   - {len(categories)} categorias")
            print(f"   - {len(transactions)} transações")
            print(f"   - {len(budgets)} orçamentos")
            print(f"   - {len(recurring_rules)} regras de recorrência")
            print(f"\n🔑 Login de demonstração:")
            print(f"   Email: admin@demo.com")
            print(f"   Senha: admin123")
            
    except Exception as e:
        print(f"❌ Erro durante o seed: {e}")
        raise


if __name__ == "__main__":
    main()
