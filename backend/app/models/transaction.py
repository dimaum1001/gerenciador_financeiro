"""
Modelo de transação financeira
"""

import uuid
from datetime import datetime, date
from decimal import Decimal
from typing import TYPE_CHECKING, Optional
from enum import Enum

from sqlalchemy import Column, String, DateTime, Date, Boolean, Text, Numeric, ForeignKey, Integer, Enum as SQLEnum, JSON
from sqlalchemy.orm import relationship

from app.db.database import Base
from app.db.types import GUID

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.account import Account
    from app.models.category import Category
    from app.models.recurring_rule import RecurringRule


class TransactionType(str, Enum):
    """Tipos de transação"""
    INCOME = "income"       # Receita
    EXPENSE = "expense"     # Despesa
    TRANSFER = "transfer"   # Transferência


class TransactionStatus(str, Enum):
    """Status da transação"""
    PENDING = "pending"         # Pendente
    CLEARED = "cleared"         # Compensada
    RECONCILED = "reconciled"   # Conciliada


class PaymentMethod(str, Enum):
    """Métodos de pagamento"""
    CASH = "cash"           # Dinheiro
    PIX = "pix"             # PIX
    DEBIT = "debit"         # Cartão de Débito
    CREDIT = "credit"       # Cartão de Crédito
    BOLETO = "boleto"       # Boleto
    TRANSFER = "transfer"   # Transferência
    CHECK = "check"         # Cheque
    OTHER = "other"         # Outros


class Transaction(Base):
    """Modelo de transação financeira"""
    
    __tablename__ = "transactions"
    __allow_unmapped__ = True
    
    # Campos principais
    id = Column(GUID, primary_key=True, default=uuid.uuid4, index=True)
    
    user_id = Column(
        GUID,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    is_demo_data = Column(Boolean, default=False, nullable=False, index=True)
    
    account_id = Column(
        GUID,
        ForeignKey("accounts.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    category_id = Column(
        GUID,
        ForeignKey("categories.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )
    
    # Dados da transação
    tipo = Column(SQLEnum(TransactionType), nullable=False, index=True)
    valor = Column(Numeric(15, 2), nullable=False)
    moeda = Column(String(3), default="BRL", nullable=False)
    
    # Datas
    data_lancamento = Column(Date, nullable=False, index=True)
    data_competencia = Column(Date, nullable=True, index=True)
    
    # Descrição e detalhes
    descricao = Column(String(255), nullable=False, index=True)
    observacoes = Column(Text, nullable=True)
    
    # Status e método
    status = Column(SQLEnum(TransactionStatus), default=TransactionStatus.PENDING, nullable=False, index=True)
    payment_method = Column(SQLEnum(PaymentMethod), nullable=True, index=True)
    
    # Tags e categorização
    tags = Column(JSON, nullable=True, default=list)
    
    # Anexos
    attachment_url = Column(Text, nullable=True)
    attachment_name = Column(String(255), nullable=True)
    
    # Parcelas
    parcela_atual = Column(Integer, nullable=True)
    parcelas_total = Column(Integer, nullable=True)
    grupo_parcelas = Column(GUID, nullable=True, index=True)
    
    # Transferências
    transfer_account_id = Column(
        GUID,
        ForeignKey("accounts.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )
    transfer_transaction_id = Column(
        GUID,
        ForeignKey("transactions.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )
    
    # Recorrência
    recurring_rule_id = Column(
        GUID,
        ForeignKey("recurring_rules.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )
    
    # Conciliação
    reconciled_at = Column(DateTime, nullable=True)
    bank_reference = Column(String(100), nullable=True)
    
    # Timestamps
    criado_em = Column(
        DateTime, 
        default=datetime.utcnow, 
        nullable=False,
        index=True
    )
    atualizado_em = Column(
        DateTime, 
        default=datetime.utcnow, 
        onupdate=datetime.utcnow,
        nullable=False
    )
    
    # Relacionamentos
    user: "User" = relationship("User", back_populates="transactions")
    account: "Account" = relationship("Account", back_populates="transactions", foreign_keys=[account_id])
    category: Optional["Category"] = relationship("Category", back_populates="transactions")
    
    # Conta de destino para transferências
    transfer_account: Optional["Account"] = relationship(
        "Account",
        foreign_keys=[transfer_account_id],
        back_populates="transfer_transactions",
    )
    
    # Transação vinculada (para transferências)
    transfer_transaction: Optional["Transaction"] = relationship(
        "Transaction", 
        remote_side=[id],
        foreign_keys=[transfer_transaction_id]
    )
    
    recurring_rule: Optional["RecurringRule"] = relationship(
        "RecurringRule",
        back_populates="transactions",
        foreign_keys=[recurring_rule_id],
    )
    
    def __repr__(self) -> str:
        return f"<Transaction(id={self.id}, tipo='{self.tipo}', valor={self.valor}, descricao='{self.descricao}')>"
    
    @property
    def valor_formatado(self) -> str:
        """Retorna valor formatado em moeda brasileira"""
        return f"R$ {self.valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    
    @property
    def is_income(self) -> bool:
        """Verifica se é receita"""
        return self.tipo == TransactionType.INCOME
    
    @property
    def is_expense(self) -> bool:
        """Verifica se é despesa"""
        return self.tipo == TransactionType.EXPENSE
    
    @property
    def is_transfer(self) -> bool:
        """Verifica se é transferência"""
        return self.tipo == TransactionType.TRANSFER
    
    @property
    def is_installment(self) -> bool:
        """Verifica se faz parte de parcelas"""
        return self.parcelas_total is not None and self.parcelas_total > 1
    
    @property
    def installment_display(self) -> Optional[str]:
        """Retorna texto das parcelas (ex: "2/12")"""
        if self.is_installment:
            return f"{self.parcela_atual}/{self.parcelas_total}"
        return None
    
    @property
    def status_display(self) -> str:
        """Retorna nome amigável do status"""
        status_names = {
            TransactionStatus.PENDING: "Pendente",
            TransactionStatus.CLEARED: "Compensada",
            TransactionStatus.RECONCILED: "Conciliada"
        }
        return status_names.get(self.status, self.status.value)
    
    @property
    def payment_method_display(self) -> str:
        """Retorna nome amigável do método de pagamento"""
        method_names = {
            PaymentMethod.CASH: "Dinheiro",
            PaymentMethod.PIX: "PIX",
            PaymentMethod.DEBIT: "Cartão de Débito",
            PaymentMethod.CREDIT: "Cartão de Crédito",
            PaymentMethod.BOLETO: "Boleto",
            PaymentMethod.TRANSFER: "Transferência",
            PaymentMethod.CHECK: "Cheque",
            PaymentMethod.OTHER: "Outros"
        }
        return method_names.get(self.payment_method, self.payment_method.value if self.payment_method else "")
    
    @property
    def data_efetiva(self) -> date:
        """Retorna data de competência ou lançamento"""
        return self.data_competencia or self.data_lancamento
    
    def get_valor_com_sinal(self) -> Decimal:
        """
        Retorna valor com sinal correto baseado no tipo
        
        Returns:
            Decimal: Valor positivo para receitas, negativo para despesas
        """
        if self.tipo == TransactionType.INCOME:
            return abs(self.valor)
        elif self.tipo == TransactionType.EXPENSE:
            return -abs(self.valor)
        else:  # TRANSFER
            return self.valor  # Mantém sinal original
