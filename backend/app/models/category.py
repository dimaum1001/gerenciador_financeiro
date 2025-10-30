"""
Modelo de categoria
"""

import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Optional
from enum import Enum

from sqlalchemy import Column, String, DateTime, Boolean, Text, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship

from app.db.database import Base
from app.db.types import GUID

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.transaction import Transaction
    from app.models.budget import Budget


class CategoryType(str, Enum):
    """Tipos de categoria"""
    INCOME = "income"     # Receita
    EXPENSE = "expense"   # Despesa


class Category(Base):
    """Modelo de categoria"""
    
    __tablename__ = "categories"
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
    
    nome = Column(String(100), nullable=False, index=True)
    tipo = Column(SQLEnum(CategoryType), nullable=False, index=True)
    
    # Hierarquia
    parent_id = Column(
        GUID,
        ForeignKey("categories.id", ondelete="CASCADE"),
        nullable=True,
        index=True
    )
    
    # Configurações visuais
    cor = Column(String(7), nullable=True)  # Hex color
    icone = Column(String(50), nullable=True)
    
    # Campos opcionais
    descricao = Column(Text, nullable=True)
    ativo = Column(Boolean, default=True, nullable=False)
    
    # Configurações
    incluir_relatorios = Column(Boolean, default=True, nullable=False)
    meta_mensal = Column(String(15), nullable=True)  # Meta de gasto/receita mensal
    
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
    user: "User" = relationship("User", back_populates="categories")
    
    # Auto-relacionamento para hierarquia
    parent: Optional["Category"] = relationship(
        "Category", 
        remote_side=[id],
        back_populates="children"
    )
    
    children: list["Category"] = relationship(
        "Category", 
        back_populates="parent",
        cascade="all, delete-orphan"
    )
    
    transactions: list["Transaction"] = relationship(
        "Transaction", 
        back_populates="category"
    )
    
    budgets: list["Budget"] = relationship(
        "Budget", 
        back_populates="category",
        cascade="all, delete-orphan"
    )
    
    def __repr__(self) -> str:
        return f"<Category(id={self.id}, nome='{self.nome}', tipo='{self.tipo}')>"
    
    @property
    def nome_completo(self) -> str:
        """Retorna nome completo incluindo hierarquia"""
        if self.parent:
            return f"{self.parent.nome_completo} > {self.nome}"
        return self.nome
    
    @property
    def nivel(self) -> int:
        """Retorna nível na hierarquia (0 = raiz)"""
        if self.parent:
            return self.parent.nivel + 1
        return 0
    
    @property
    def is_parent(self) -> bool:
        """Verifica se tem subcategorias"""
        return len(self.children) > 0
    
    @property
    def tipo_display(self) -> str:
        """Retorna nome amigável do tipo"""
        tipo_names = {
            CategoryType.INCOME: "Receita",
            CategoryType.EXPENSE: "Despesa"
        }
        return tipo_names.get(self.tipo, self.tipo.value)
    
    def get_all_children_ids(self) -> list[uuid.UUID]:
        """
        Retorna IDs de todas as subcategorias (recursivo)
        
        Returns:
            list: Lista de UUIDs das subcategorias
        """
        ids = []
        for child in self.children:
            ids.append(child.id)
            ids.extend(child.get_all_children_ids())
        return ids
    
    def get_root_category(self) -> "Category":
        """
        Retorna categoria raiz da hierarquia
        
        Returns:
            Category: Categoria raiz
        """
        if self.parent:
            return self.parent.get_root_category()
        return self
