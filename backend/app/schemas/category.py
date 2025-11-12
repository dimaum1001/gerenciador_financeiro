"""
Schemas Pydantic para Category
"""

import uuid
from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, Field, ConfigDict, validator, computed_field, AliasChoices

from app.models.category import CategoryType
from app.utils.locale_mapper import category_type_mapper


class CategoryBase(BaseModel):
    """Schema base para categoria"""
    nome: str = Field(..., min_length=1, max_length=100, description="Nome da categoria")
    tipo: CategoryType = Field(..., description="Tipo da categoria (income/expense)")
    parent_id: Optional[uuid.UUID] = Field(
        None,
        description="ID da categoria pai",
        validation_alias=AliasChoices("categoria_pai_id", "parent_id"),
        serialization_alias="categoria_pai_id",
    )
    cor: Optional[str] = Field(None, max_length=7, description="Cor em hexadecimal")
    icone: Optional[str] = Field(None, max_length=50, description="Ícone da categoria")
    descricao: Optional[str] = Field(None, description="Descrição da categoria")
    ativo: bool = Field(default=True, description="Se a categoria está ativa")
    incluir_relatorios: bool = Field(default=True, description="Incluir nos relatórios")
    meta_mensal: Optional[str] = Field(None, max_length=15, description="Meta mensal")

    model_config = ConfigDict(populate_by_name=True)

    @validator("tipo", pre=True)
    def _normalize_tipo(cls, value):
        return category_type_mapper.to_enum(value)


class CategoryCreate(CategoryBase):
    """Schema para criação de categoria"""
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "nome": "Alimentação",
                "tipo": "expense",
                "parent_id": None,
                "cor": "#ef4444",
                "icone": "utensils",
                "descricao": "Gastos com alimentação e restaurantes",
                "ativo": True,
                "incluir_relatorios": True,
                "meta_mensal": "800.00"
            }
        }
    )


class CategoryUpdate(BaseModel):
    """Schema para atualização de categoria"""
    nome: Optional[str] = Field(None, min_length=1, max_length=100)
    parent_id: Optional[uuid.UUID] = None
    cor: Optional[str] = Field(None, max_length=7)
    icone: Optional[str] = Field(None, max_length=50)
    descricao: Optional[str] = None
    ativo: Optional[bool] = None
    incluir_relatorios: Optional[bool] = None
    meta_mensal: Optional[str] = Field(None, max_length=15)
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "nome": "Alimentação e Restaurantes",
                "cor": "#dc2626",
                "meta_mensal": "900.00"
            }
        }
    )


class CategoryResponse(CategoryBase):
    """Schema de resposta para categoria"""
    id: uuid.UUID
    user_id: uuid.UUID = Field(
        ...,
        validation_alias=AliasChoices("usuario_id", "user_id"),
        serialization_alias="usuario_id",
    )
    nome_completo: str
    nivel: int
    is_parent: bool
    tipo_display: str
    criado_em: datetime
    atualizado_em: datetime
    
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    @computed_field
    def tipo_portugues(self) -> Optional[str]:
        return category_type_mapper.to_portuguese(self.tipo)

    @computed_field
    def tipo_legado(self) -> Optional[str]:
        return category_type_mapper.legacy_value(self.tipo)


class CategoryTree(CategoryResponse):
    """Schema para árvore de categorias"""
    children: List["CategoryTree"] = Field(default_factory=list)
    
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class CategorySummary(BaseModel):
    """Schema para resumo da categoria"""
    id: uuid.UUID
    nome: str
    nome_completo: str
    tipo: CategoryType
    tipo_display: str
    cor: Optional[str] = None
    icone: Optional[str] = None
    ativo: bool
    total_transacoes: int = 0
    valor_total: float = 0.0
    
    model_config = ConfigDict(from_attributes=True)

    @computed_field
    def tipo_portugues(self) -> Optional[str]:
        return category_type_mapper.to_portuguese(self.tipo)

    @computed_field
    def tipo_legado(self) -> Optional[str]:
        return category_type_mapper.legacy_value(self.tipo)


class CategoryStats(BaseModel):
    """Schema para estatísticas da categoria"""
    category_id: uuid.UUID
    nome: str
    total_transacoes: int
    valor_total: float
    valor_medio: float
    percentual_do_total: float
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "category_id": "123e4567-e89b-12d3-a456-426614174000",
                "nome": "Alimentação",
                "total_transacoes": 25,
                "valor_total": 1250.00,
                "valor_medio": 50.00,
                "percentual_do_total": 15.5
            }
        }
    )


class CategoryBudgetSummary(BaseModel):
    """Schema para resumo de categoria com orçamento"""
    category_id: uuid.UUID = Field(
        ...,
        validation_alias=AliasChoices("categoria_id", "category_id"),
        serialization_alias="categoria_id",
    )
    nome: str
    nome_completo: str
    tipo: CategoryType
    cor: Optional[str] = None
    valor_planejado: float = 0.0
    valor_realizado: float = 0.0
    percentual_utilizado: float = 0.0
    valor_restante: float = 0.0
    status: str = "active"

    @computed_field
    def tipo_portugues(self) -> Optional[str]:
        return category_type_mapper.to_portuguese(self.tipo)

    @computed_field
    def tipo_legado(self) -> Optional[str]:
        return category_type_mapper.legacy_value(self.tipo)
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "category_id": "123e4567-e89b-12d3-a456-426614174000",
                "nome": "Alimentação",
                "nome_completo": "Alimentação",
                "tipo": "expense",
                "cor": "#ef4444",
                "valor_planejado": 800.00,
                "valor_realizado": 650.00,
                "percentual_utilizado": 81.25,
                "valor_restante": 150.00,
                "status": "active"
            }
        }
    )


# Resolver referência circular
CategoryTree.model_rebuild()


class CategoryListResponse(BaseModel):
    """Resposta paginada de categorias"""
    categories: List[CategoryResponse]
    total: int
    skip: int
    limit: int

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
