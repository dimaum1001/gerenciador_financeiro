"""
Modelo de regra de recorrência
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
from app.models._enum_utils import enum_values

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.account import Account
    from app.models.category import Category
    from app.models.transaction import Transaction


class RecurrenceFrequency(str, Enum):
    """Frequência de recorrência"""
    DAILY = "diario"
    WEEKLY = "semanal"
    MONTHLY = "mensal"
    QUARTERLY = "trimestral"
    YEARLY = "anual"


class RecurrenceStatus(str, Enum):
    """Status da regra de recorrência"""
    ACTIVE = "ativa"
    PAUSED = "pausada"
    COMPLETED = "concluida"
    CANCELLED = "cancelada"


class RecurringRule(Base):
    """Modelo de regra de recorrência"""
    
    __tablename__ = "regras_recorrentes"
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
    
    # Template da transação
    account_id = Column(
        "conta_id",
        GUID, 
        ForeignKey("contas.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    category_id = Column(
        "categoria_id",
        GUID, 
        ForeignKey("categorias.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )
    
    # Dados do template
    nome = Column(String(100), nullable=False, index=True)
    descricao_template = Column(String(255), nullable=False)
    tipo = Column(String(20), nullable=False)  # income, expense, transfer
    valor = Column(Numeric(15, 2), nullable=False)
    payment_method = Column("metodo_pagamento", String(20), nullable=True)
    
    # Configurações de recorrência
    frequencia = Column(
        SQLEnum(
            RecurrenceFrequency,
            name="recurrencefrequency",
            values_callable=enum_values,
        ),
        nullable=False,
        index=True,
    )
    intervalo = Column(Integer, default=1, nullable=False)  # A cada X períodos
    
    # Configurações específicas
    dia_do_mes = Column(Integer, nullable=True)  # Para mensal/anual (1-31)
    dias_da_semana = Column(JSON, nullable=True)  # Para semanal [0-6] (0=domingo)
    
    # Período de vigência
    data_inicio = Column(Date, nullable=False, index=True)
    data_fim = Column(Date, nullable=True, index=True)
    
    # Status e controle
    status = Column(
        "status_regra",
        SQLEnum(
            RecurrenceStatus,
            name="recurrencestatus",
            values_callable=enum_values,
        ),
        default=RecurrenceStatus.ACTIVE,
        nullable=False,
        index=True,
    )
    ativo = Column(Boolean, default=True, nullable=False)
    
    # Controle de execução
    proxima_execucao = Column(Date, nullable=True, index=True)
    ultima_execucao = Column(Date, nullable=True)
    total_execucoes = Column(Integer, default=0, nullable=False)
    max_execucoes = Column(Integer, nullable=True)  # Limite de execuções
    
    # Configurações avançadas
    ajustar_fins_de_semana = Column(Boolean, default=False, nullable=False)
    pular_feriados = Column(Boolean, default=False, nullable=False)
    criar_antecipado_dias = Column(Integer, default=0, nullable=False)
    
    # Campos opcionais
    observacoes = Column(Text, nullable=True)
    tags_template = Column(JSON, nullable=True, default=list)
    
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
    user: "User" = relationship("User", back_populates="recurring_rules")
    account: "Account" = relationship("Account")
    category: Optional["Category"] = relationship("Category")
    
    # Transações geradas por esta regra
    transactions: list["Transaction"] = relationship(
        "Transaction",
        back_populates="recurring_rule",
        foreign_keys="Transaction.recurring_rule_id"
    )
    
    def __repr__(self) -> str:
        return f"<RecurringRule(id={self.id}, nome='{self.nome}', frequencia='{self.frequencia}')>"
    
    @property
    def frequencia_display(self) -> str:
        """Retorna nome amigável da frequência"""
        freq_names = {
            RecurrenceFrequency.DAILY: "Diário",
            RecurrenceFrequency.WEEKLY: "Semanal",
            RecurrenceFrequency.MONTHLY: "Mensal",
            RecurrenceFrequency.QUARTERLY: "Trimestral",
            RecurrenceFrequency.YEARLY: "Anual"
        }
        return freq_names.get(self.frequencia, self.frequencia.value)
    
    @property
    def status_display(self) -> str:
        """Retorna nome amigável do status"""
        status_names = {
            RecurrenceStatus.ACTIVE: "Ativa",
            RecurrenceStatus.PAUSED: "Pausada",
            RecurrenceStatus.COMPLETED: "Concluída",
            RecurrenceStatus.CANCELLED: "Cancelada"
        }
        return status_names.get(self.status, self.status.value)
    
    @property
    def descricao_completa(self) -> str:
        """Retorna descrição completa da recorrência"""
        desc = f"{self.frequencia_display}"
        
        if self.intervalo > 1:
            desc = f"A cada {self.intervalo} {desc.lower()}s"
        
        if self.frequencia == RecurrenceFrequency.MONTHLY and self.dia_do_mes:
            desc += f" no dia {self.dia_do_mes}"
        elif self.frequencia == RecurrenceFrequency.WEEKLY and self.dias_da_semana:
            dias_nomes = ["Dom", "Seg", "Ter", "Qua", "Qui", "Sex", "Sáb"]
            dias = [dias_nomes[d] for d in self.dias_da_semana]
            desc += f" ({', '.join(dias)})"
        
        return desc
    
    @property
    def is_active(self) -> bool:
        """Verifica se a regra está ativa"""
        return self.ativo and self.status == RecurrenceStatus.ACTIVE
    
    @property
    def is_expired(self) -> bool:
        """Verifica se a regra expirou"""
        if self.data_fim and date.today() > self.data_fim:
            return True
        if self.max_execucoes and self.total_execucoes >= self.max_execucoes:
            return True
        return False
    
    @property
    def valor_formatado(self) -> str:
        """Retorna valor formatado em moeda brasileira"""
        return f"R$ {self.valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    
    def calcular_proxima_execucao(self, data_base: Optional[date] = None) -> Optional[date]:
        """
        Calcula próxima data de execução
        
        Args:
            data_base: Data base para cálculo (padrão: hoje)
            
        Returns:
            date: Próxima data de execução ou None se não aplicável
        """
        from dateutil.relativedelta import relativedelta
        
        if not self.is_active or self.is_expired:
            return None
        
        base = data_base or date.today()
        
        if self.frequencia == RecurrenceFrequency.DAILY:
            return base + relativedelta(days=self.intervalo)
        
        elif self.frequencia == RecurrenceFrequency.WEEKLY:
            return base + relativedelta(weeks=self.intervalo)
        
        elif self.frequencia == RecurrenceFrequency.MONTHLY:
            next_date = base + relativedelta(months=self.intervalo)
            if self.dia_do_mes:
                try:
                    next_date = next_date.replace(day=self.dia_do_mes)
                except ValueError:
                    # Se o dia não existe no mês (ex: 31 em fevereiro), usa último dia
                    next_date = next_date + relativedelta(day=31)
            return next_date
        
        elif self.frequencia == RecurrenceFrequency.QUARTERLY:
            return base + relativedelta(months=3 * self.intervalo)
        
        elif self.frequencia == RecurrenceFrequency.YEARLY:
            return base + relativedelta(years=self.intervalo)
        
        return None
    
    def pode_executar(self, data_execucao: date) -> bool:
        """
        Verifica se pode executar na data especificada
        
        Args:
            data_execucao: Data para verificar
            
        Returns:
            bool: True se pode executar
        """
        if not self.is_active:
            return False
        
        if data_execucao < self.data_inicio:
            return False
        
        if self.data_fim and data_execucao > self.data_fim:
            return False
        
        if self.max_execucoes and self.total_execucoes >= self.max_execucoes:
            return False
        
        return True
