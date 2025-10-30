"""
Schemas Pydantic para User
"""

import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field, ConfigDict


class UserBase(BaseModel):
    """Schema base para usuário"""
    nome: str = Field(..., min_length=2, max_length=100, description="Nome completo do usuário")
    email: EmailStr = Field(..., description="Email único do usuário")
    telefone: Optional[str] = Field(None, max_length=20, description="Telefone do usuário")
    timezone: str = Field(default="America/Sao_Paulo", description="Timezone do usuário")
    moeda_padrao: str = Field(default="BRL", max_length=3, description="Moeda padrão")
    formato_data: str = Field(default="DD/MM/YYYY", description="Formato de data preferido")


class UserCreate(UserBase):
    """Schema para criação de usuário"""
    senha: str = Field(..., min_length=8, description="Senha do usuário")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "nome": "João Silva",
                "email": "joao@exemplo.com",
                "senha": "minhasenha123",
                "telefone": "(11) 99999-9999",
                "timezone": "America/Sao_Paulo",
                "moeda_padrao": "BRL",
                "formato_data": "DD/MM/YYYY"
            }
        }
    )


class UserUpdate(BaseModel):
    """Schema para atualização de usuário"""
    nome: Optional[str] = Field(None, min_length=2, max_length=100)
    telefone: Optional[str] = Field(None, max_length=20)
    avatar_url: Optional[str] = None
    timezone: Optional[str] = None
    moeda_padrao: Optional[str] = Field(None, max_length=3)
    formato_data: Optional[str] = None
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "nome": "João Silva Santos",
                "telefone": "(11) 88888-8888",
                "timezone": "America/Sao_Paulo"
            }
        }
    )


class UserChangePassword(BaseModel):
    """Schema para alteração de senha"""
    senha_atual: str = Field(..., description="Senha atual")
    senha_nova: str = Field(..., min_length=8, description="Nova senha")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "senha_atual": "senhaatual123",
                "senha_nova": "novasenha456"
            }
        }
    )


class UserResponse(UserBase):
    """Schema de resposta para usuário"""
    id: uuid.UUID
    ativo: bool
    email_verificado: bool
    is_demo: bool
    avatar_url: Optional[str] = None
    criado_em: datetime
    atualizado_em: datetime
    ultimo_login: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)


class UserProfile(UserResponse):
    """Schema completo do perfil do usuário"""
    iniciais: str
    
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "nome": "João Silva",
                "email": "joao@exemplo.com",
                "telefone": "(11) 99999-9999",
            "ativo": True,
            "email_verificado": True,
            "is_demo": False,
            "timezone": "America/Sao_Paulo",
            "moeda_padrao": "BRL",
            "formato_data": "DD/MM/YYYY",
            "iniciais": "JS",
                "criado_em": "2024-01-01T10:00:00Z",
                "atualizado_em": "2024-01-01T10:00:00Z"
            }
        }
    )


class UserStats(BaseModel):
    """Schema para estatísticas do usuário"""
    total_contas: int
    total_categorias: int
    total_transacoes: int
    total_orcamentos: int
    saldo_total: float
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "total_contas": 5,
                "total_categorias": 15,
                "total_transacoes": 234,
                "total_orcamentos": 8,
                "saldo_total": 15750.50
            }
        }
    )
