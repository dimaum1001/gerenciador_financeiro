"""
Modelo de conta financeira
"""

import uuid
from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING
from enum import Enum

from sqlalchemy import Column, String, DateTime, Boolean, Text, Numeric, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship

from app.db.database import Base
from app.db.types import GUID
from app.models._enum_utils import enum_values

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.transaction import Transaction


class AccountType(str, Enum):
    """Tipos de conta"""
    CASH = "dinheiro"
    CHECKING = "conta_corrente"
    SAVINGS = "poupanca"
    CREDIT = "cartao_credito"
    INVESTMENT = "investimento"
    OTHER = "outros"


class Account(Base):
    """Modelo de conta financeira"""
    
    __tablename__ = "contas"
    __allow_unmapped__ = True
    
    # Campos principais
    id = Column(GUID, primary_key=True, default=uuid.uuid4, index=True)
    
    user_id = Column(
        "usuario_id",
        GUID,
        ForeignKey("usuarios.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    is_demo_data = Column("dados_demo", Boolean, default=False, nullable=False, index=True)
    
    nome = Column(String(100), nullable=False, index=True)
    tipo = Column(
        SQLEnum(
            AccountType,
            name="accounttype",
            values_callable=enum_values,
        ),
        nullable=False,
        index=True,
    )
    
    # Saldos e valores
    saldo_inicial = Column(
        Numeric(15, 2), 
        default=Decimal("0.00"), 
        nullable=False
    )
    
    # Configurações
    moeda = Column(String(3), default="BRL", nullable=False)
    ativo = Column(Boolean, default=True, nullable=False)
    incluir_relatorios = Column(Boolean, default=True, nullable=False)
    
    # Campos opcionais
    descricao = Column(Text, nullable=True)
    cor = Column(String(7), nullable=True)  # Hex color
    icone = Column(String(50), nullable=True)
    
    # Informações bancárias (opcional)
    banco = Column(String(100), nullable=True)
    agencia = Column(String(20), nullable=True)
    conta = Column(String(20), nullable=True)
    
    # Limites (para cartão de crédito)
    limite_credito = Column(Numeric(15, 2), nullable=True)
    dia_vencimento = Column(String(2), nullable=True)  # Dia do mês
    dia_fechamento = Column(String(2), nullable=True)  # Dia do mês
    
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
    user: "User" = relationship("User", back_populates="accounts")
    
    transactions: list["Transaction"] = relationship(
        "Transaction",
        back_populates="account",
        cascade="all, delete-orphan",
        foreign_keys="Transaction.account_id",
    )

    transfer_transactions: list["Transaction"] = relationship(
        "Transaction",
        back_populates="transfer_account",
        foreign_keys="Transaction.transfer_account_id",
    )
    
    def __repr__(self) -> str:
        return f"<Account(id={self.id}, nome='{self.nome}', tipo='{self.tipo}')>"
    
    @property
    def saldo_atual(self) -> Decimal:
        """
        Calcula saldo atual baseado no saldo inicial e transações
        
        Returns:
            Decimal: Saldo atual da conta
        """
        # Este cálculo será implementado via query no service
        # Por enquanto retorna o saldo inicial
        return self.saldo_inicial
    
    @property
    def tipo_display(self) -> str:
        """Retorna nome amigável do tipo de conta"""
        tipo_names = {
            AccountType.CASH: "Dinheiro",
            AccountType.CHECKING: "Conta Corrente",
            AccountType.SAVINGS: "Poupança", 
            AccountType.CREDIT: "Cartão de Crédito",
            AccountType.INVESTMENT: "Investimentos",
            AccountType.OTHER: "Outros"
        }
        return tipo_names.get(self.tipo, self.tipo.value)
    
    @property
    def is_credit_card(self) -> bool:
        """Verifica se é cartão de crédito"""
        return self.tipo == AccountType.CREDIT
    
    @property
    def limite_disponivel(self) -> Decimal:
        """Calcula limite disponível para cartão de crédito"""
        if not self.is_credit_card or not self.limite_credito:
            return Decimal("0.00")
        
        # Saldo negativo em cartão de crédito representa dívida
        saldo_usado = abs(self.saldo_atual) if self.saldo_atual < 0 else Decimal("0.00")
        return self.limite_credito - saldo_usado
