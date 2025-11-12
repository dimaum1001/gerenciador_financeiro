"""
Schemas Pydantic para RecurringRule
"""

import uuid
from datetime import datetime, date
from decimal import Decimal
from typing import Optional, List

from pydantic import BaseModel, Field, ConfigDict, validator, computed_field, AliasChoices

from app.models.recurring_rule import RecurrenceFrequency, RecurrenceStatus
from app.models.transaction import TransactionType, PaymentMethod
from app.utils.locale_mapper import (
    transaction_type_mapper,
    payment_method_mapper,
    recurrence_frequency_mapper,
    recurrence_status_mapper,
)


class RecurringRuleBase(BaseModel):
    """Schema base para regra de recorrência"""
    account_id: uuid.UUID = Field(
        ...,
        description="ID da conta",
        validation_alias=AliasChoices("conta_id", "account_id"),
        serialization_alias="conta_id",
    )
    category_id: Optional[uuid.UUID] = Field(
        None,
        description="ID da categoria",
        validation_alias=AliasChoices("categoria_id", "category_id"),
        serialization_alias="categoria_id",
    )
    nome: str = Field(..., min_length=1, max_length=100, description="Nome da regra")
    descricao_template: str = Field(..., min_length=1, max_length=255, description="Descrição template")
    tipo: TransactionType = Field(..., description="Tipo da transação")
    valor: Decimal = Field(..., gt=0, description="Valor da transação")
    payment_method: Optional[PaymentMethod] = Field(
        None,
        description="Método de pagamento",
        validation_alias=AliasChoices("metodo_pagamento", "payment_method"),
        serialization_alias="metodo_pagamento",
    )
    frequencia: RecurrenceFrequency = Field(..., description="Frequência de recorrência")
    intervalo: int = Field(default=1, ge=1, le=12, description="Intervalo entre execuções")
    data_inicio: date = Field(..., description="Data de início")
    data_fim: Optional[date] = Field(None, description="Data de fim (opcional)")
    ativo: bool = Field(default=True, description="Se a regra está ativa")
    model_config = ConfigDict(populate_by_name=True)

    @validator("tipo", pre=True)
    def _normalize_tipo(cls, value):
        return transaction_type_mapper.to_enum(value)

    @validator("payment_method", pre=True)
    def _normalize_payment_method(cls, value):
        if value in (None, "", "none"):
            return None
        return payment_method_mapper.to_enum(value)

    @validator("frequencia", pre=True)
    def _normalize_frequencia(cls, value):
        return recurrence_frequency_mapper.to_enum(value)


class RecurringRuleCreate(RecurringRuleBase):
    """Schema para criação de regra de recorrência"""
    # Configurações específicas
    dia_do_mes: Optional[int] = Field(None, ge=1, le=31, description="Dia do mês (para mensal/anual)")
    dias_da_semana: Optional[List[int]] = Field(None, description="Dias da semana (0=domingo)")
    
    # Configurações avançadas
    ajustar_fins_de_semana: bool = Field(default=False, description="Ajustar para dias úteis")
    pular_feriados: bool = Field(default=False, description="Pular feriados")
    criar_antecipado_dias: int = Field(default=0, ge=0, le=30, description="Criar com antecedência")
    max_execucoes: Optional[int] = Field(None, ge=1, description="Máximo de execuções")
    
    # Campos opcionais
    observacoes: Optional[str] = Field(None, description="Observações")
    tags_template: List[str] = Field(default_factory=list, description="Tags para as transações")
    
    @validator('dias_da_semana')
    def validate_dias_semana(cls, v):
        if v is not None:
            if not all(0 <= dia <= 6 for dia in v):
                raise ValueError('Dias da semana devem estar entre 0 (domingo) e 6 (sábado)')
            if len(v) == 0:
                raise ValueError('Deve especificar pelo menos um dia da semana')
        return v
    
    @validator('data_fim')
    def validate_data_fim(cls, v, values):
        if v and 'data_inicio' in values and v <= values['data_inicio']:
            raise ValueError('Data de fim deve ser posterior à data de início')
        return v
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "account_id": "123e4567-e89b-12d3-a456-426614174000",
                "category_id": "456e7890-e89b-12d3-a456-426614174000",
                "nome": "Salário Mensal",
                "descricao_template": "Salário do mês",
                "tipo": "income",
                "valor": 5000.00,
                "payment_method": "transfer",
                "frequencia": "monthly",
                "intervalo": 1,
                "data_inicio": "2024-01-05",
                "data_fim": None,
                "dia_do_mes": 5,
                "ativo": True,
                "observacoes": "Salário depositado todo dia 5",
                "tags_template": ["salário", "renda"]
            }
        }
    )


class RecurringRuleUpdate(BaseModel):
    """Schema para atualização de regra de recorrência"""
    nome: Optional[str] = Field(None, min_length=1, max_length=100)
    descricao_template: Optional[str] = Field(None, min_length=1, max_length=255)
    valor: Optional[Decimal] = Field(None, gt=0)
    payment_method: Optional[PaymentMethod] = None
    data_fim: Optional[date] = None
    ativo: Optional[bool] = None
    status: Optional[RecurrenceStatus] = None
    dia_do_mes: Optional[int] = Field(None, ge=1, le=31)
    dias_da_semana: Optional[List[int]] = None
    ajustar_fins_de_semana: Optional[bool] = None
    pular_feriados: Optional[bool] = None
    criar_antecipado_dias: Optional[int] = Field(None, ge=0, le=30)
    max_execucoes: Optional[int] = Field(None, ge=1)
    observacoes: Optional[str] = None
    tags_template: Optional[List[str]] = None
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "valor": 5500.00,
                "observacoes": "Salário com aumento",
                "tags_template": ["salário", "renda", "aumento"]
            }
        }
    )


class RecurringRuleResponse(RecurringRuleBase):
    """Schema de resposta para regra de recorrência"""
    id: uuid.UUID
    user_id: uuid.UUID = Field(
        ...,
        validation_alias=AliasChoices("usuario_id", "user_id"),
        serialization_alias="usuario_id",
    )
    status: RecurrenceStatus
    frequencia_display: str
    status_display: str
    descricao_completa: str
    is_active: bool
    is_expired: bool
    valor_formatado: str
    
    # Configurações específicas
    dia_do_mes: Optional[int] = None
    dias_da_semana: Optional[List[int]] = None
    
    # Controle de execução
    proxima_execucao: Optional[date] = None
    ultima_execucao: Optional[date] = None
    total_execucoes: int
    max_execucoes: Optional[int] = None
    
    # Configurações avançadas
    ajustar_fins_de_semana: bool
    pular_feriados: bool
    criar_antecipado_dias: int
    
    # Campos opcionais
    observacoes: Optional[str] = None
    tags_template: List[str] = Field(default_factory=list)
    
    # Timestamps
    criado_em: datetime
    atualizado_em: datetime
    
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    @validator("status", pre=True)
    def _normalize_status(cls, value):
        return recurrence_status_mapper.to_enum(value)

    @computed_field
    def tipo_portugues(self) -> Optional[str]:
        return transaction_type_mapper.to_portuguese(self.tipo)

    @computed_field
    def tipo_legado(self) -> Optional[str]:
        return transaction_type_mapper.legacy_value(self.tipo)

    @computed_field
    def metodo_pagamento_portugues(self) -> Optional[str]:
        return payment_method_mapper.to_portuguese(self.payment_method)

    @computed_field
    def metodo_pagamento_legado(self) -> Optional[str]:
        return payment_method_mapper.legacy_value(self.payment_method)

    @computed_field
    def frequencia_portugues(self) -> Optional[str]:
        return recurrence_frequency_mapper.to_portuguese(self.frequencia)

    @computed_field
    def frequencia_legado(self) -> Optional[str]:
        return recurrence_frequency_mapper.legacy_value(self.frequencia)

    @computed_field
    def status_portugues(self) -> Optional[str]:
        return recurrence_status_mapper.to_portuguese(self.status)

    @computed_field
    def status_legado(self) -> Optional[str]:
        return recurrence_status_mapper.legacy_value(self.status)


class RecurringRuleWithDetails(RecurringRuleResponse):
    """Schema de regra com detalhes relacionados"""
    account_name: str
    category_name: Optional[str] = None
    category_color: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)


class RecurringRuleSummary(BaseModel):
    """Schema para resumo de regras de recorrência"""
    id: uuid.UUID
    nome: str
    tipo: TransactionType
    valor: Decimal
    frequencia_display: str
    status_display: str
    proxima_execucao: Optional[date] = None
    account_name: str
    category_name: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)

    @computed_field
    def tipo_portugues(self) -> Optional[str]:
        return transaction_type_mapper.to_portuguese(self.tipo)

    @computed_field
    def tipo_legado(self) -> Optional[str]:
        return transaction_type_mapper.legacy_value(self.tipo)


class RecurringRuleExecution(BaseModel):
    """Schema para execução de regras"""
    rule_id: uuid.UUID
    data_execucao: date
    valor: Decimal
    descricao: str
    sucesso: bool
    erro: Optional[str] = None
    transaction_id: Optional[uuid.UUID] = None
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "rule_id": "123e4567-e89b-12d3-a456-426614174000",
                "data_execucao": "2024-01-05",
                "valor": 5000.00,
                "descricao": "Salário do mês",
                "sucesso": True,
                "erro": None,
                "transaction_id": "789e0123-e89b-12d3-a456-426614174000"
            }
        }
    )


class RecurringRuleRunRequest(BaseModel):
    """Schema para executar regras de recorrência"""
    year: Optional[int] = Field(None, ge=2000, le=2100, description="Ano específico")
    month: Optional[int] = Field(None, ge=1, le=12, description="Mês específico")
    rule_ids: Optional[List[uuid.UUID]] = Field(None, description="IDs específicos de regras")
    dry_run: bool = Field(default=False, description="Executar em modo teste")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "year": 2024,
                "month": 1,
                "dry_run": False
            }
        }
    )


class RecurringRuleRunResult(BaseModel):
    """Schema para resultado da execução"""
    total_regras: int
    regras_executadas: int
    transacoes_criadas: int
    erros: List[str]
    execucoes: List[RecurringRuleExecution]
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "total_regras": 5,
                "regras_executadas": 4,
                "transacoes_criadas": 4,
                "erros": ["Regra 'Aluguel': Conta inativa"],
                "execucoes": [
                    {
                        "rule_id": "123e4567-e89b-12d3-a456-426614174000",
                        "data_execucao": "2024-01-05",
                        "valor": 5000.00,
                        "descricao": "Salário do mês",
                        "sucesso": True,
                        "transaction_id": "789e0123-e89b-12d3-a456-426614174000"
                    }
                ]
            }
        }
    )


class RecurringRuleFilter(BaseModel):
    """Schema para filtros de regras de recorrência"""
    account_id: Optional[uuid.UUID] = None
    category_id: Optional[uuid.UUID] = None
    tipo: Optional[TransactionType] = None
    frequencia: Optional[RecurrenceFrequency] = None
    status: Optional[RecurrenceStatus] = None
    ativo: Optional[bool] = None
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "account_id": "123e4567-e89b-12d3-a456-426614174000",
                "tipo": "income",
                "frequencia": "monthly",
                "ativo": True
            }
        }
    )
