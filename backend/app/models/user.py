"""
Modelo de usuário
"""

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Column, String, DateTime, Boolean, Text
from sqlalchemy.orm import relationship

from app.db.database import Base
from app.db.types import GUID

if TYPE_CHECKING:
    from app.models.account import Account
    from app.models.category import Category
    from app.models.transaction import Transaction
    from app.models.budget import Budget
    from app.models.recurring_rule import RecurringRule


class User(Base):
    """Modelo de usuário do sistema"""
    
    __tablename__ = "users"
    __allow_unmapped__ = True
    
    # Campos principais
    id = Column(GUID, primary_key=True, default=uuid.uuid4, index=True)
    
    nome = Column(String(100), nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    senha_hash = Column(String(255), nullable=False)
    
    # Campos opcionais
    telefone = Column(String(20), nullable=True)
    avatar_url = Column(Text, nullable=True)
    
    # Status e configurações
    ativo = Column(Boolean, default=True, nullable=False)
    email_verificado = Column(Boolean, default=False, nullable=False)
    is_demo = Column(Boolean, default=False, nullable=False)
    
    # Preferências
    timezone = Column(String(50), default="America/Sao_Paulo", nullable=False)
    moeda_padrao = Column(String(3), default="BRL", nullable=False)
    formato_data = Column(String(20), default="DD/MM/YYYY", nullable=False)
    
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
    ultimo_login = Column(DateTime, nullable=True)
    
    # Relacionamentos
    accounts: list["Account"] = relationship(
        "Account", 
        back_populates="user",
        cascade="all, delete-orphan"
    )
    
    categories: list["Category"] = relationship(
        "Category", 
        back_populates="user",
        cascade="all, delete-orphan"
    )
    
    transactions: list["Transaction"] = relationship(
        "Transaction", 
        back_populates="user",
        cascade="all, delete-orphan"
    )
    
    budgets: list["Budget"] = relationship(
        "Budget", 
        back_populates="user",
        cascade="all, delete-orphan"
    )
    
    recurring_rules: list["RecurringRule"] = relationship(
        "RecurringRule", 
        back_populates="user",
        cascade="all, delete-orphan"
    )
    
    def __repr__(self) -> str:
        return f"<User(id={self.id}, email='{self.email}', nome='{self.nome}')>"
    
    @property
    def nome_completo(self) -> str:
        """Retorna nome completo do usuário"""
        return self.nome
    
    @property
    def iniciais(self) -> str:
        """Retorna iniciais do nome"""
        parts = self.nome.split()
        if len(parts) >= 2:
            return f"{parts[0][0]}{parts[-1][0]}".upper()
        return self.nome[0].upper() if self.nome else "U"
