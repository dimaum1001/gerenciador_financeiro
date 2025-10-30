"""
Modelo de orçamento
"""

import uuid
from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING
from enum import Enum

from sqlalchemy import Column, String, DateTime, Boolean, Text, Numeric, ForeignKey, Integer, Enum as SQLEnum
from sqlalchemy.orm import relationship

from app.db.database import Base
from app.db.types import GUID

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.category import Category


class BudgetStatus(str, Enum):
    """Status do orçamento"""
    ACTIVE = "active"       # Ativo
    PAUSED = "paused"       # Pausado
    COMPLETED = "completed" # Concluído
    EXCEEDED = "exceeded"   # Excedido


class Budget(Base):
    """Modelo de orçamento"""
    
    __tablename__ = "budgets"
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
    
    category_id = Column(
        GUID, 
        ForeignKey("categories.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    # Período
    ano = Column(Integer, nullable=False, index=True)
    mes = Column(Integer, nullable=False, index=True)
    
    # Valores
    valor_planejado = Column(Numeric(15, 2), nullable=False)
    valor_realizado = Column(Numeric(15, 2), default=Decimal("0.00"), nullable=False)
    
    # Configurações
    ativo = Column(Boolean, default=True, nullable=False)
    incluir_subcategorias = Column(Boolean, default=True, nullable=False)
    
    # Alertas
    alerta_percentual = Column(Integer, default=80, nullable=False)  # % para alerta
    alerta_enviado = Column(Boolean, default=False, nullable=False)
    
    # Campos opcionais
    descricao = Column(Text, nullable=True)
    observacoes = Column(Text, nullable=True)
    
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
    user: "User" = relationship("User", back_populates="budgets")
    category: "Category" = relationship("Category", back_populates="budgets")
    
    def __repr__(self) -> str:
        return f"<Budget(id={self.id}, ano={self.ano}, mes={self.mes}, valor_planejado={self.valor_planejado})>"
    
    @property
    def periodo_display(self) -> str:
        """Retorna período formatado (MM/YYYY)"""
        return f"{self.mes:02d}/{self.ano}"
    
    @property
    def percentual_utilizado(self) -> float:
        """Calcula percentual utilizado do orçamento"""
        if self.valor_planejado == 0:
            return 0.0
        return float((self.valor_realizado / self.valor_planejado) * 100)
    
    @property
    def valor_restante(self) -> Decimal:
        """Calcula valor restante do orçamento"""
        return self.valor_planejado - self.valor_realizado
    
    @property
    def status(self) -> BudgetStatus:
        """Determina status atual do orçamento"""
        if not self.ativo:
            return BudgetStatus.PAUSED
        
        percentual = self.percentual_utilizado
        
        if percentual >= 100:
            return BudgetStatus.EXCEEDED
        elif percentual >= 95:
            return BudgetStatus.COMPLETED
        else:
            return BudgetStatus.ACTIVE
    
    @property
    def status_display(self) -> str:
        """Retorna nome amigável do status"""
        status_names = {
            BudgetStatus.ACTIVE: "Ativo",
            BudgetStatus.PAUSED: "Pausado",
            BudgetStatus.COMPLETED: "Concluído",
            BudgetStatus.EXCEEDED: "Excedido"
        }
        return status_names.get(self.status, self.status.value)
    
    @property
    def cor_status(self) -> str:
        """Retorna cor baseada no status"""
        percentual = self.percentual_utilizado
        
        if percentual >= 100:
            return "#ef4444"  # Vermelho - Excedido
        elif percentual >= 80:
            return "#f59e0b"  # Amarelo - Atenção
        elif percentual >= 60:
            return "#3b82f6"  # Azul - Progresso
        else:
            return "#10b981"  # Verde - Saudável
    
    @property
    def precisa_alerta(self) -> bool:
        """Verifica se precisa enviar alerta"""
        return (
            self.ativo and 
            not self.alerta_enviado and 
            self.percentual_utilizado >= self.alerta_percentual
        )
    
    def calcular_media_diaria(self, dias_no_mes: int) -> Decimal:
        """
        Calcula média diária baseada no valor planejado
        
        Args:
            dias_no_mes: Número de dias no mês
            
        Returns:
            Decimal: Valor médio por dia
        """
        if dias_no_mes <= 0:
            return Decimal("0.00")
        return self.valor_planejado / dias_no_mes
    
    def calcular_projecao_mensal(self, dia_atual: int, dias_no_mes: int) -> Decimal:
        """
        Calcula projeção de gasto para o mês baseado no ritmo atual
        
        Args:
            dia_atual: Dia atual do mês
            dias_no_mes: Total de dias no mês
            
        Returns:
            Decimal: Projeção de gasto mensal
        """
        if dia_atual <= 0 or self.valor_realizado == 0:
            return Decimal("0.00")
        
        media_diaria_atual = self.valor_realizado / dia_atual
        return media_diaria_atual * dias_no_mes
