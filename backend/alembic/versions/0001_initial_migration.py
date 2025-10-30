"""Initial migration

Revision ID: 0001
Revises: 
Create Date: 2024-01-01 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

from app.db.types import GUID

# revision identifiers, used by Alembic.
revision = '0001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create users table
    op.create_table('users',
        sa.Column('id', GUID(), nullable=False),
        sa.Column('nome', sa.String(length=100), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('senha_hash', sa.String(length=255), nullable=False),
        sa.Column('telefone', sa.String(length=20), nullable=True),
        sa.Column('avatar_url', sa.Text(), nullable=True),
        sa.Column('ativo', sa.Boolean(), nullable=False),
        sa.Column('email_verificado', sa.Boolean(), nullable=False),
        sa.Column('timezone', sa.String(length=50), nullable=False),
        sa.Column('moeda_padrao', sa.String(length=3), nullable=False),
        sa.Column('formato_data', sa.String(length=20), nullable=False),
        sa.Column('criado_em', sa.DateTime(), nullable=False),
        sa.Column('atualizado_em', sa.DateTime(), nullable=False),
        sa.Column('ultimo_login', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_users')),
        sa.UniqueConstraint('email', name=op.f('uq_users_email'))
    )
    op.create_index(op.f('ix_users_criado_em'), 'users', ['criado_em'], unique=False)
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=False)
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)
    op.create_index(op.f('ix_users_nome'), 'users', ['nome'], unique=False)

    # Create accounts table
    op.create_table('accounts',
        sa.Column('id', GUID(), nullable=False),
        sa.Column('user_id', GUID(), nullable=False),
        sa.Column('nome', sa.String(length=100), nullable=False),
        sa.Column('tipo', sa.Enum('CASH', 'CHECKING', 'SAVINGS', 'CREDIT', 'INVESTMENT', 'OTHER', name='accounttype'), nullable=False),
        sa.Column('saldo_inicial', sa.Numeric(precision=15, scale=2), nullable=False),
        sa.Column('moeda', sa.String(length=3), nullable=False),
        sa.Column('ativo', sa.Boolean(), nullable=False),
        sa.Column('incluir_relatorios', sa.Boolean(), nullable=False),
        sa.Column('descricao', sa.Text(), nullable=True),
        sa.Column('cor', sa.String(length=7), nullable=True),
        sa.Column('icone', sa.String(length=50), nullable=True),
        sa.Column('banco', sa.String(length=100), nullable=True),
        sa.Column('agencia', sa.String(length=20), nullable=True),
        sa.Column('conta', sa.String(length=20), nullable=True),
        sa.Column('limite_credito', sa.Numeric(precision=15, scale=2), nullable=True),
        sa.Column('dia_vencimento', sa.String(length=2), nullable=True),
        sa.Column('dia_fechamento', sa.String(length=2), nullable=True),
        sa.Column('criado_em', sa.DateTime(), nullable=False),
        sa.Column('atualizado_em', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], name=op.f('fk_accounts_user_id_users'), ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_accounts'))
    )
    op.create_index(op.f('ix_accounts_criado_em'), 'accounts', ['criado_em'], unique=False)
    op.create_index(op.f('ix_accounts_id'), 'accounts', ['id'], unique=False)
    op.create_index(op.f('ix_accounts_nome'), 'accounts', ['nome'], unique=False)
    op.create_index(op.f('ix_accounts_tipo'), 'accounts', ['tipo'], unique=False)
    op.create_index(op.f('ix_accounts_user_id'), 'accounts', ['user_id'], unique=False)

    # Create categories table
    op.create_table('categories',
        sa.Column('id', GUID(), nullable=False),
        sa.Column('user_id', GUID(), nullable=False),
        sa.Column('nome', sa.String(length=100), nullable=False),
        sa.Column('tipo', sa.Enum('INCOME', 'EXPENSE', name='categorytype'), nullable=False),
        sa.Column('parent_id', GUID(), nullable=True),
        sa.Column('cor', sa.String(length=7), nullable=True),
        sa.Column('icone', sa.String(length=50), nullable=True),
        sa.Column('descricao', sa.Text(), nullable=True),
        sa.Column('ativo', sa.Boolean(), nullable=False),
        sa.Column('incluir_relatorios', sa.Boolean(), nullable=False),
        sa.Column('meta_mensal', sa.String(length=15), nullable=True),
        sa.Column('criado_em', sa.DateTime(), nullable=False),
        sa.Column('atualizado_em', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['parent_id'], ['categories.id'], name=op.f('fk_categories_parent_id_categories'), ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], name=op.f('fk_categories_user_id_users'), ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_categories'))
    )
    op.create_index(op.f('ix_categories_criado_em'), 'categories', ['criado_em'], unique=False)
    op.create_index(op.f('ix_categories_id'), 'categories', ['id'], unique=False)
    op.create_index(op.f('ix_categories_nome'), 'categories', ['nome'], unique=False)
    op.create_index(op.f('ix_categories_parent_id'), 'categories', ['parent_id'], unique=False)
    op.create_index(op.f('ix_categories_tipo'), 'categories', ['tipo'], unique=False)
    op.create_index(op.f('ix_categories_user_id'), 'categories', ['user_id'], unique=False)

    # Create recurring_rules table
    op.create_table('recurring_rules',
        sa.Column('id', GUID(), nullable=False),
        sa.Column('user_id', GUID(), nullable=False),
        sa.Column('account_id', GUID(), nullable=False),
        sa.Column('category_id', GUID(), nullable=True),
        sa.Column('nome', sa.String(length=100), nullable=False),
        sa.Column('descricao_template', sa.String(length=255), nullable=False),
        sa.Column('tipo', sa.String(length=20), nullable=False),
        sa.Column('valor', sa.Numeric(precision=15, scale=2), nullable=False),
        sa.Column('payment_method', sa.String(length=20), nullable=True),
        sa.Column('frequencia', sa.Enum('DAILY', 'WEEKLY', 'MONTHLY', 'QUARTERLY', 'YEARLY', name='recurrencefrequency'), nullable=False),
        sa.Column('intervalo', sa.Integer(), nullable=False),
        sa.Column('dia_do_mes', sa.Integer(), nullable=True),
        sa.Column('dias_da_semana', sa.JSON(), nullable=True),
        sa.Column('data_inicio', sa.Date(), nullable=False),
        sa.Column('data_fim', sa.Date(), nullable=True),
        sa.Column('status', sa.Enum('ACTIVE', 'PAUSED', 'COMPLETED', 'CANCELLED', name='recurrencestatus'), nullable=False),
        sa.Column('ativo', sa.Boolean(), nullable=False),
        sa.Column('proxima_execucao', sa.Date(), nullable=True),
        sa.Column('ultima_execucao', sa.Date(), nullable=True),
        sa.Column('total_execucoes', sa.Integer(), nullable=False),
        sa.Column('max_execucoes', sa.Integer(), nullable=True),
        sa.Column('ajustar_fins_de_semana', sa.Boolean(), nullable=False),
        sa.Column('pular_feriados', sa.Boolean(), nullable=False),
        sa.Column('criar_antecipado_dias', sa.Integer(), nullable=False),
        sa.Column('observacoes', sa.Text(), nullable=True),
        sa.Column('tags_template', sa.JSON(), nullable=True),
        sa.Column('criado_em', sa.DateTime(), nullable=False),
        sa.Column('atualizado_em', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['account_id'], ['accounts.id'], name=op.f('fk_recurring_rules_account_id_accounts'), ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['category_id'], ['categories.id'], name=op.f('fk_recurring_rules_category_id_categories'), ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], name=op.f('fk_recurring_rules_user_id_users'), ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_recurring_rules'))
    )
    op.create_index(op.f('ix_recurring_rules_criado_em'), 'recurring_rules', ['criado_em'], unique=False)
    op.create_index(op.f('ix_recurring_rules_data_fim'), 'recurring_rules', ['data_fim'], unique=False)
    op.create_index(op.f('ix_recurring_rules_data_inicio'), 'recurring_rules', ['data_inicio'], unique=False)
    op.create_index(op.f('ix_recurring_rules_frequencia'), 'recurring_rules', ['frequencia'], unique=False)
    op.create_index(op.f('ix_recurring_rules_id'), 'recurring_rules', ['id'], unique=False)
    op.create_index(op.f('ix_recurring_rules_nome'), 'recurring_rules', ['nome'], unique=False)
    op.create_index(op.f('ix_recurring_rules_proxima_execucao'), 'recurring_rules', ['proxima_execucao'], unique=False)
    op.create_index(op.f('ix_recurring_rules_status'), 'recurring_rules', ['status'], unique=False)
    op.create_index(op.f('ix_recurring_rules_user_id'), 'recurring_rules', ['user_id'], unique=False)

    # Create transactions table
    op.create_table('transactions',
        sa.Column('id', GUID(), nullable=False),
        sa.Column('user_id', GUID(), nullable=False),
        sa.Column('account_id', GUID(), nullable=False),
        sa.Column('category_id', GUID(), nullable=True),
        sa.Column('tipo', sa.Enum('INCOME', 'EXPENSE', 'TRANSFER', name='transactiontype'), nullable=False),
        sa.Column('valor', sa.Numeric(precision=15, scale=2), nullable=False),
        sa.Column('moeda', sa.String(length=3), nullable=False),
        sa.Column('data_lancamento', sa.Date(), nullable=False),
        sa.Column('data_competencia', sa.Date(), nullable=True),
        sa.Column('descricao', sa.String(length=255), nullable=False),
        sa.Column('observacoes', sa.Text(), nullable=True),
        sa.Column('status', sa.Enum('PENDING', 'CLEARED', 'RECONCILED', name='transactionstatus'), nullable=False),
        sa.Column('payment_method', sa.Enum('CASH', 'PIX', 'DEBIT', 'CREDIT', 'BOLETO', 'TRANSFER', 'CHECK', 'OTHER', name='paymentmethod'), nullable=True),
        sa.Column('tags', sa.JSON(), nullable=True),
        sa.Column('attachment_url', sa.Text(), nullable=True),
        sa.Column('attachment_name', sa.String(length=255), nullable=True),
        sa.Column('parcela_atual', sa.Integer(), nullable=True),
        sa.Column('parcelas_total', sa.Integer(), nullable=True),
        sa.Column('grupo_parcelas', GUID(), nullable=True),
        sa.Column('transfer_account_id', GUID(), nullable=True),
        sa.Column('transfer_transaction_id', GUID(), nullable=True),
        sa.Column('recurring_rule_id', GUID(), nullable=True),
        sa.Column('reconciled_at', sa.DateTime(), nullable=True),
        sa.Column('bank_reference', sa.String(length=100), nullable=True),
        sa.Column('criado_em', sa.DateTime(), nullable=False),
        sa.Column('atualizado_em', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['account_id'], ['accounts.id'], name=op.f('fk_transactions_account_id_accounts'), ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['category_id'], ['categories.id'], name=op.f('fk_transactions_category_id_categories'), ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['recurring_rule_id'], ['recurring_rules.id'], name=op.f('fk_transactions_recurring_rule_id_recurring_rules'), ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['transfer_account_id'], ['accounts.id'], name=op.f('fk_transactions_transfer_account_id_accounts'), ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['transfer_transaction_id'], ['transactions.id'], name=op.f('fk_transactions_transfer_transaction_id_transactions'), ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], name=op.f('fk_transactions_user_id_users'), ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_transactions'))
    )
    op.create_index(op.f('ix_transactions_account_id'), 'transactions', ['account_id'], unique=False)
    op.create_index(op.f('ix_transactions_category_id'), 'transactions', ['category_id'], unique=False)
    op.create_index(op.f('ix_transactions_criado_em'), 'transactions', ['criado_em'], unique=False)
    op.create_index(op.f('ix_transactions_data_competencia'), 'transactions', ['data_competencia'], unique=False)
    op.create_index(op.f('ix_transactions_data_lancamento'), 'transactions', ['data_lancamento'], unique=False)
    op.create_index(op.f('ix_transactions_descricao'), 'transactions', ['descricao'], unique=False)
    op.create_index(op.f('ix_transactions_grupo_parcelas'), 'transactions', ['grupo_parcelas'], unique=False)
    op.create_index(op.f('ix_transactions_id'), 'transactions', ['id'], unique=False)
    op.create_index(op.f('ix_transactions_payment_method'), 'transactions', ['payment_method'], unique=False)
    op.create_index(op.f('ix_transactions_status'), 'transactions', ['status'], unique=False)
    op.create_index(op.f('ix_transactions_tags'), 'transactions', ['tags'], unique=False)
    op.create_index(op.f('ix_transactions_tipo'), 'transactions', ['tipo'], unique=False)
    op.create_index(op.f('ix_transactions_transfer_account_id'), 'transactions', ['transfer_account_id'], unique=False)
    op.create_index(op.f('ix_transactions_transfer_transaction_id'), 'transactions', ['transfer_transaction_id'], unique=False)
    op.create_index(op.f('ix_transactions_user_id'), 'transactions', ['user_id'], unique=False)

    # Create budgets table
    op.create_table('budgets',
        sa.Column('id', GUID(), nullable=False),
        sa.Column('user_id', GUID(), nullable=False),
        sa.Column('category_id', GUID(), nullable=False),
        sa.Column('ano', sa.Integer(), nullable=False),
        sa.Column('mes', sa.Integer(), nullable=False),
        sa.Column('valor_planejado', sa.Numeric(precision=15, scale=2), nullable=False),
        sa.Column('valor_realizado', sa.Numeric(precision=15, scale=2), nullable=False),
        sa.Column('ativo', sa.Boolean(), nullable=False),
        sa.Column('incluir_subcategorias', sa.Boolean(), nullable=False),
        sa.Column('alerta_percentual', sa.Integer(), nullable=False),
        sa.Column('alerta_enviado', sa.Boolean(), nullable=False),
        sa.Column('descricao', sa.Text(), nullable=True),
        sa.Column('observacoes', sa.Text(), nullable=True),
        sa.Column('criado_em', sa.DateTime(), nullable=False),
        sa.Column('atualizado_em', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['category_id'], ['categories.id'], name=op.f('fk_budgets_category_id_categories'), ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], name=op.f('fk_budgets_user_id_users'), ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_budgets'))
    )
    op.create_index(op.f('ix_budgets_ano'), 'budgets', ['ano'], unique=False)
    op.create_index(op.f('ix_budgets_category_id'), 'budgets', ['category_id'], unique=False)
    op.create_index(op.f('ix_budgets_criado_em'), 'budgets', ['criado_em'], unique=False)
    op.create_index(op.f('ix_budgets_id'), 'budgets', ['id'], unique=False)
    op.create_index(op.f('ix_budgets_mes'), 'budgets', ['mes'], unique=False)
    op.create_index(op.f('ix_budgets_user_id'), 'budgets', ['user_id'], unique=False)


def downgrade() -> None:
    op.drop_table('budgets')
    op.drop_table('transactions')
    op.drop_table('recurring_rules')
    op.drop_table('categories')
    op.drop_table('accounts')
    op.drop_table('users')
    
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        # Drop enums específicos do PostgreSQL
        op.execute('DROP TYPE IF EXISTS accounttype')
        op.execute('DROP TYPE IF EXISTS categorytype')
        op.execute('DROP TYPE IF EXISTS transactiontype')
        op.execute('DROP TYPE IF EXISTS transactionstatus')
        op.execute('DROP TYPE IF EXISTS paymentmethod')
        op.execute('DROP TYPE IF EXISTS recurrencefrequency')
        op.execute('DROP TYPE IF EXISTS recurrencestatus')
