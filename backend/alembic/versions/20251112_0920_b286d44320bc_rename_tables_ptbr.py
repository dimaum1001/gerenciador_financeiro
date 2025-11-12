"""rename_tables_ptbr

Revision ID: b286d44320bc
Revises: 0001
Create Date: 2025-11-12 09:20:15.251560-03:00

"""
from alembic import op
import sqlalchemy as sa


ACCOUNT_TYPE_MAP = {
    "CASH": "dinheiro",
    "CHECKING": "conta_corrente",
    "SAVINGS": "poupanca",
    "CREDIT": "cartao_credito",
    "INVESTMENT": "investimento",
    "OTHER": "outros",
}

CATEGORY_TYPE_MAP = {
    "INCOME": "receita",
    "EXPENSE": "despesa",
}

TRANSACTION_TYPE_MAP = {
    "INCOME": "receita",
    "EXPENSE": "despesa",
    "TRANSFER": "transferencia",
}

TRANSACTION_STATUS_MAP = {
    "PENDING": "pendente",
    "CLEARED": "compensada",
    "RECONCILED": "conciliada",
}

PAYMENT_METHOD_MAP = {
    "CASH": "dinheiro",
    "PIX": "pix",
    "DEBIT": "cartao_debito",
    "CREDIT": "cartao_credito",
    "BOLETO": "boleto",
    "TRANSFER": "transferencia",
    "CHECK": "cheque",
    "OTHER": "outros",
}

RECURRENCE_FREQUENCY_MAP = {
    "DAILY": "diario",
    "WEEKLY": "semanal",
    "MONTHLY": "mensal",
    "QUARTERLY": "trimestral",
    "YEARLY": "anual",
}

RECURRENCE_STATUS_MAP = {
    "ACTIVE": "ativa",
    "PAUSED": "pausada",
    "COMPLETED": "concluida",
    "CANCELLED": "cancelada",
}


def _replace_enum(table, column, enum_name, mapping):
    """Replace existing enum values (PostgreSQL) with new mapping."""
    conn = op.get_bind()
    old_enum = f"{enum_name}_old"
    op.execute(sa.text(f'ALTER TYPE {enum_name} RENAME TO {old_enum}'))
    new_enum = sa.Enum(*mapping.values(), name=enum_name)
    new_enum.create(conn, checkfirst=False)

    case_parts = [
        f"WHEN \"{column}\" = '{old}' THEN '{new}'"
        for old, new in mapping.items()
    ]
    case_expr = (
        f"CASE WHEN \"{column}\" IS NULL THEN NULL "
        + " ".join(case_parts)
        + f" ELSE \"{column}\"::text END"
    )

    op.execute(
        sa.text(
            f'ALTER TABLE {table} ALTER COLUMN "{column}" '
            f"TYPE {enum_name} USING ({case_expr})::{enum_name}"
        )
    )
    op.execute(sa.text(f"DROP TYPE {old_enum}"))


def _restore_enum(table, column, enum_name, mapping):
    """Inverse of _replace_enum."""
    inverse_map = {new: old for old, new in mapping.items()}
    conn = op.get_bind()
    old_enum = f"{enum_name}_old"
    op.execute(sa.text(f'ALTER TYPE {enum_name} RENAME TO {old_enum}'))
    original_enum = sa.Enum(*inverse_map.values(), name=enum_name)
    original_enum.create(conn, checkfirst=False)

    case_parts = [
        f"WHEN \"{column}\" = '{new}' THEN '{old}'"
        for old, new in mapping.items()
    ]
    case_expr = (
        f"CASE WHEN \"{column}\" IS NULL THEN NULL "
        + " ".join(case_parts)
        + f" ELSE \"{column}\"::text END"
    )
    op.execute(
        sa.text(
            f'ALTER TABLE {table} ALTER COLUMN "{column}" '
            f"TYPE {enum_name} USING ({case_expr})::{enum_name}"
        )
    )
    op.execute(sa.text(f"DROP TYPE {old_enum}"))


# revision identifiers, used by Alembic.
revision = 'b286d44320bc'
down_revision = '0001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Rename tables
    op.rename_table('users', 'usuarios')
    op.rename_table('accounts', 'contas')
    op.rename_table('categories', 'categorias')
    op.rename_table('transactions', 'transacoes')
    op.rename_table('budgets', 'orcamentos')
    op.rename_table('recurring_rules', 'regras_recorrentes')

    # Rename columns in `usuarios`
    op.alter_column('usuarios', 'timezone', new_column_name='fuso_horario')
    op.alter_column('usuarios', 'is_demo', new_column_name='demo')

    # Rename columns in `contas`
    op.alter_column('contas', 'user_id', new_column_name='usuario_id')
    op.alter_column('contas', 'is_demo_data', new_column_name='dados_demo')

    # Rename columns in `categorias`
    op.alter_column('categorias', 'user_id', new_column_name='usuario_id')
    op.alter_column('categorias', 'parent_id', new_column_name='categoria_pai_id')
    op.alter_column('categorias', 'is_demo_data', new_column_name='dados_demo')

    # Rename columns in `transacoes`
    op.alter_column('transacoes', 'user_id', new_column_name='usuario_id')
    op.alter_column('transacoes', 'account_id', new_column_name='conta_id')
    op.alter_column('transacoes', 'category_id', new_column_name='categoria_id')
    op.alter_column('transacoes', 'transfer_account_id', new_column_name='conta_transferencia_id')
    op.alter_column('transacoes', 'transfer_transaction_id', new_column_name='transacao_transferencia_id')
    op.alter_column('transacoes', 'recurring_rule_id', new_column_name='regra_recorrente_id')
    op.alter_column('transacoes', 'payment_method', new_column_name='metodo_pagamento')
    op.alter_column('transacoes', 'attachment_url', new_column_name='anexo_url')
    op.alter_column('transacoes', 'attachment_name', new_column_name='anexo_nome')
    op.alter_column('transacoes', 'bank_reference', new_column_name='referencia_bancaria')
    op.alter_column('transacoes', 'is_demo_data', new_column_name='dados_demo')

    # Rename columns in `orcamentos`
    op.alter_column('orcamentos', 'user_id', new_column_name='usuario_id')
    op.alter_column('orcamentos', 'category_id', new_column_name='categoria_id')
    op.alter_column('orcamentos', 'is_demo_data', new_column_name='dados_demo')

    # Rename columns in `regras_recorrentes`
    op.alter_column('regras_recorrentes', 'user_id', new_column_name='usuario_id')
    op.alter_column('regras_recorrentes', 'account_id', new_column_name='conta_id')
    op.alter_column('regras_recorrentes', 'category_id', new_column_name='categoria_id')
    op.alter_column('regras_recorrentes', 'payment_method', new_column_name='metodo_pagamento')
    op.alter_column('regras_recorrentes', 'status', new_column_name='status_regra')
    op.alter_column('regras_recorrentes', 'is_demo_data', new_column_name='dados_demo')

    # Replace enums/data
    _replace_enum('contas', 'tipo', 'accounttype', ACCOUNT_TYPE_MAP)
    _replace_enum('categorias', 'tipo', 'categorytype', CATEGORY_TYPE_MAP)
    _replace_enum('transacoes', 'tipo', 'transactiontype', TRANSACTION_TYPE_MAP)
    _replace_enum('transacoes', 'status', 'transactionstatus', TRANSACTION_STATUS_MAP)
    _replace_enum('transacoes', 'metodo_pagamento', 'paymentmethod', PAYMENT_METHOD_MAP)
    _replace_enum('regras_recorrentes', 'frequencia', 'recurrencefrequency', RECURRENCE_FREQUENCY_MAP)
    _replace_enum('regras_recorrentes', 'status_regra', 'recurrencestatus', RECURRENCE_STATUS_MAP)


def downgrade() -> None:
    # Restore enums
    _restore_enum('regras_recorrentes', 'status_regra', 'recurrencestatus', RECURRENCE_STATUS_MAP)
    _restore_enum('regras_recorrentes', 'frequencia', 'recurrencefrequency', RECURRENCE_FREQUENCY_MAP)
    _restore_enum('transacoes', 'metodo_pagamento', 'paymentmethod', PAYMENT_METHOD_MAP)
    _restore_enum('transacoes', 'status', 'transactionstatus', TRANSACTION_STATUS_MAP)
    _restore_enum('transacoes', 'tipo', 'transactiontype', TRANSACTION_TYPE_MAP)
    _restore_enum('categorias', 'tipo', 'categorytype', CATEGORY_TYPE_MAP)
    _restore_enum('contas', 'tipo', 'accounttype', ACCOUNT_TYPE_MAP)

    # Rename columns back
    op.alter_column('regras_recorrentes', 'dados_demo', new_column_name='is_demo_data')
    op.alter_column('regras_recorrentes', 'status_regra', new_column_name='status')
    op.alter_column('regras_recorrentes', 'metodo_pagamento', new_column_name='payment_method')
    op.alter_column('regras_recorrentes', 'categoria_id', new_column_name='category_id')
    op.alter_column('regras_recorrentes', 'conta_id', new_column_name='account_id')
    op.alter_column('regras_recorrentes', 'usuario_id', new_column_name='user_id')

    op.alter_column('orcamentos', 'dados_demo', new_column_name='is_demo_data')
    op.alter_column('orcamentos', 'categoria_id', new_column_name='category_id')
    op.alter_column('orcamentos', 'usuario_id', new_column_name='user_id')

    op.alter_column('transacoes', 'dados_demo', new_column_name='is_demo_data')
    op.alter_column('transacoes', 'referencia_bancaria', new_column_name='bank_reference')
    op.alter_column('transacoes', 'anexo_nome', new_column_name='attachment_name')
    op.alter_column('transacoes', 'anexo_url', new_column_name='attachment_url')
    op.alter_column('transacoes', 'metodo_pagamento', new_column_name='payment_method')
    op.alter_column('transacoes', 'regra_recorrente_id', new_column_name='recurring_rule_id')
    op.alter_column('transacoes', 'transacao_transferencia_id', new_column_name='transfer_transaction_id')
    op.alter_column('transacoes', 'conta_transferencia_id', new_column_name='transfer_account_id')
    op.alter_column('transacoes', 'categoria_id', new_column_name='category_id')
    op.alter_column('transacoes', 'conta_id', new_column_name='account_id')
    op.alter_column('transacoes', 'usuario_id', new_column_name='user_id')

    op.alter_column('categorias', 'dados_demo', new_column_name='is_demo_data')
    op.alter_column('categorias', 'categoria_pai_id', new_column_name='parent_id')
    op.alter_column('categorias', 'usuario_id', new_column_name='user_id')

    op.alter_column('contas', 'dados_demo', new_column_name='is_demo_data')
    op.alter_column('contas', 'usuario_id', new_column_name='user_id')

    op.alter_column('usuarios', 'demo', new_column_name='is_demo')
    op.alter_column('usuarios', 'fuso_horario', new_column_name='timezone')

    # Rename tables back
    op.rename_table('regras_recorrentes', 'recurring_rules')
    op.rename_table('orcamentos', 'budgets')
    op.rename_table('transacoes', 'transactions')
    op.rename_table('categorias', 'categories')
    op.rename_table('contas', 'accounts')
    op.rename_table('usuarios', 'users')
