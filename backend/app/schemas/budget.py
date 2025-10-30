"""
Schemas Pydantic para Budget
"""

import uuid
from datetime import datetime
from decimal import Decimal
from typing import Optional, List

from pydantic import BaseModel, Field, ConfigDict, validator

from app.models.budget import BudgetStatus


class BudgetBase(BaseModel):
    """Schema base para orçamento"""
    category_id: uuid.UUID = Field(..., description="ID da categoria")
    ano: int = Field(..., ge=2000, le=2100, description="Ano do orçamento")
    mes: int = Field(..., ge=1, le=12, description="Mês do orçamento")
    valor_planejado: Decimal = Field(..., gt=0, description="Valor planejado")
    ativo: bool = Field(default=True, description="Se o orçamento está ativo")
    incluir_subcategorias: bool = Field(default=True, description="Incluir subcategorias")
    alerta_percentual: int = Field(default=80, ge=0, le=100, description="Percentual para alerta")
    descricao: Optional[str] = Field(None, description="Descrição do orçamento")
    observacoes: Optional[str] = Field(None, description="Observações")


class BudgetCreate(BudgetBase):
    """Schema para criação de orçamento"""
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "category_id": "123e4567-e89b-12d3-a456-426614174000",
                "ano": 2024,
                "mes": 1,
                "valor_planejado": 800.00,
                "ativo": True,
                "incluir_subcategorias": True,
                "alerta_percentual": 80,
                "descricao": "Orçamento para alimentação em janeiro",
                "observacoes": "Incluir gastos com restaurantes"
            }
        }
    )


class BudgetUpdate(BaseModel):
    """Schema para atualização de orçamento"""
    valor_planejado: Optional[Decimal] = Field(None, gt=0)
    ativo: Optional[bool] = None
    incluir_subcategorias: Optional[bool] = None
    alerta_percentual: Optional[int] = Field(None, ge=0, le=100)
    descricao: Optional[str] = None
    observacoes: Optional[str] = None
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "valor_planejado": 900.00,
                "alerta_percentual": 85,
                "observacoes": "Orçamento ajustado para incluir gastos extras"
            }
        }
    )


class BudgetResponse(BudgetBase):
    """Schema de resposta para orçamento"""
    id: uuid.UUID
    user_id: uuid.UUID
    valor_realizado: Decimal
    periodo_display: str
    percentual_utilizado: float
    valor_restante: Decimal
    status: BudgetStatus
    status_display: str
    cor_status: str
    precisa_alerta: bool
    alerta_enviado: bool
    criado_em: datetime
    atualizado_em: datetime
    
    model_config = ConfigDict(from_attributes=True)


class BudgetWithCategory(BudgetResponse):
    """Schema de orçamento com dados da categoria"""
    category_name: str
    category_color: Optional[str] = None
    category_icon: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)


class BudgetSummary(BaseModel):
    """Schema para resumo de orçamentos"""
    category_id: uuid.UUID
    category_name: str
    category_color: Optional[str] = None
    valor_planejado: Decimal
    valor_realizado: Decimal
    percentual_utilizado: float
    valor_restante: Decimal
    status: str
    cor_status: str
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "category_id": "123e4567-e89b-12d3-a456-426614174000",
                "category_name": "Alimentação",
                "category_color": "#ef4444",
                "valor_planejado": 800.00,
                "valor_realizado": 650.00,
                "percentual_utilizado": 81.25,
                "valor_restante": 150.00,
                "status": "active",
                "cor_status": "#f59e0b"
            }
        }
    )


class BudgetStats(BaseModel):
    """Schema para estatísticas de orçamentos"""
    total_orcamentos: int
    orcamentos_ativos: int
    orcamentos_excedidos: int
    valor_total_planejado: Decimal
    valor_total_realizado: Decimal
    percentual_geral: float
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "total_orcamentos": 8,
                "orcamentos_ativos": 6,
                "orcamentos_excedidos": 1,
                "valor_total_planejado": 5000.00,
                "valor_total_realizado": 4250.00,
                "percentual_geral": 85.0
            }
        }
    )


class BudgetAnalysis(BaseModel):
    """Schema para análise de orçamento"""
    budget_id: uuid.UUID
    category_name: str
    periodo: str
    valor_planejado: Decimal
    valor_realizado: Decimal
    media_diaria_planejada: Decimal
    media_diaria_realizada: Decimal
    projecao_mensal: Decimal
    dias_restantes: int
    tendencia: str  # "acima", "dentro", "abaixo"
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "budget_id": "123e4567-e89b-12d3-a456-426614174000",
                "category_name": "Alimentação",
                "periodo": "01/2024",
                "valor_planejado": 800.00,
                "valor_realizado": 400.00,
                "media_diaria_planejada": 25.81,
                "media_diaria_realizada": 26.67,
                "projecao_mensal": 826.67,
                "dias_restantes": 16,
                "tendencia": "acima"
            }
        }
    )


class BudgetFilter(BaseModel):
    """Schema para filtros de orçamento"""
    year: Optional[int] = Field(None, ge=2000, le=2100)
    month: Optional[int] = Field(None, ge=1, le=12)
    category_id: Optional[uuid.UUID] = None
    ativo: Optional[bool] = None
    status: Optional[str] = None
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "year": 2024,
                "month": 1,
                "ativo": True,
                "status": "active"
            }
        }
    )


class BudgetCopy(BaseModel):
    """Schema para copiar orçamento"""
    source_year: int = Field(..., ge=2000, le=2100)
    source_month: int = Field(..., ge=1, le=12)
    target_year: int = Field(..., ge=2000, le=2100)
    target_month: int = Field(..., ge=1, le=12)
    category_ids: Optional[List[uuid.UUID]] = Field(None, description="Categorias específicas para copiar")
    adjust_percentage: Optional[float] = Field(None, description="Percentual de ajuste nos valores")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "source_year": 2024,
                "source_month": 1,
                "target_year": 2024,
                "target_month": 2,
                "adjust_percentage": 5.0
            }
        }
    )


class BudgetListResponse(BaseModel):
    """Resposta paginada de orçamentos"""
    budgets: List[BudgetResponse]
    total: int
    skip: int
    limit: int

    model_config = ConfigDict(from_attributes=True)
