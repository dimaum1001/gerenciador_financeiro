"""
Schemas Pydantic para Account
"""

import uuid
from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field, ConfigDict

from app.models.account import AccountType


class AccountBase(BaseModel):
    """Schema base para conta"""
    nome: str = Field(..., min_length=1, max_length=100, description="Nome da conta")
    tipo: AccountType = Field(..., description="Tipo da conta")
    saldo_inicial: Decimal = Field(default=Decimal("0.00"), description="Saldo inicial")
    moeda: str = Field(default="BRL", max_length=3, description="Moeda da conta")
    ativo: bool = Field(default=True, description="Se a conta está ativa")
    incluir_relatorios: bool = Field(default=True, description="Incluir nos relatórios")
    descricao: Optional[str] = Field(None, description="Descrição da conta")
    cor: Optional[str] = Field(None, max_length=7, description="Cor em hexadecimal")
    icone: Optional[str] = Field(None, max_length=50, description="Ícone da conta")


class AccountCreate(AccountBase):
    """Schema para criação de conta"""
    # Campos específicos para cartão de crédito
    limite_credito: Optional[Decimal] = Field(None, description="Limite do cartão de crédito")
    dia_vencimento: Optional[str] = Field(None, max_length=2, description="Dia do vencimento")
    dia_fechamento: Optional[str] = Field(None, max_length=2, description="Dia do fechamento")
    
    # Informações bancárias opcionais
    banco: Optional[str] = Field(None, max_length=100, description="Nome do banco")
    agencia: Optional[str] = Field(None, max_length=20, description="Agência")
    conta: Optional[str] = Field(None, max_length=20, description="Número da conta")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "nome": "Conta Corrente Banco do Brasil",
                "tipo": "checking",
                "saldo_inicial": 1500.00,
                "moeda": "BRL",
                "ativo": True,
                "incluir_relatorios": True,
                "descricao": "Conta principal para movimentação",
                "cor": "#1e40af",
                "banco": "Banco do Brasil",
                "agencia": "1234-5",
                "conta": "12345-6"
            }
        }
    )


class AccountUpdate(BaseModel):
    """Schema para atualização de conta"""
    nome: Optional[str] = Field(None, min_length=1, max_length=100)
    ativo: Optional[bool] = None
    incluir_relatorios: Optional[bool] = None
    descricao: Optional[str] = None
    cor: Optional[str] = Field(None, max_length=7)
    icone: Optional[str] = Field(None, max_length=50)
    limite_credito: Optional[Decimal] = None
    dia_vencimento: Optional[str] = Field(None, max_length=2)
    dia_fechamento: Optional[str] = Field(None, max_length=2)
    banco: Optional[str] = Field(None, max_length=100)
    agencia: Optional[str] = Field(None, max_length=20)
    conta: Optional[str] = Field(None, max_length=20)
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "nome": "Conta Corrente BB - Atualizada",
                "ativo": True,
                "cor": "#2563eb"
            }
        }
    )


class AccountResponse(AccountBase):
    """Schema de resposta para conta"""
    id: uuid.UUID
    user_id: uuid.UUID
    saldo_atual: Decimal
    tipo_display: str
    is_credit_card: bool
    limite_disponivel: Optional[Decimal] = None
    banco: Optional[str] = None
    agencia: Optional[str] = None
    conta: Optional[str] = None
    limite_credito: Optional[Decimal] = None
    dia_vencimento: Optional[str] = None
    dia_fechamento: Optional[str] = None
    criado_em: datetime
    atualizado_em: datetime
    
    model_config = ConfigDict(from_attributes=True)


class AccountSummary(BaseModel):
    """Schema para resumo da conta"""
    id: uuid.UUID
    nome: str
    tipo: AccountType
    tipo_display: str
    saldo_atual: Decimal
    cor: Optional[str] = None
    icone: Optional[str] = None
    ativo: bool
    
    model_config = ConfigDict(from_attributes=True)


class AccountBalance(BaseModel):
    """Schema para saldo da conta"""
    account_id: uuid.UUID
    nome: str
    saldo_inicial: Decimal
    saldo_atual: Decimal
    total_receitas: Decimal
    total_despesas: Decimal
    total_transferencias: Decimal
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "account_id": "123e4567-e89b-12d3-a456-426614174000",
                "nome": "Conta Corrente",
                "saldo_inicial": 1000.00,
                "saldo_atual": 1250.50,
                "total_receitas": 2500.00,
                "total_despesas": -2249.50,
                "total_transferencias": 0.00
            }
        }
    )


class AccountStats(BaseModel):
    """Schema para estatísticas da conta"""
    total_transacoes: int
    media_mensal_receitas: Decimal
    media_mensal_despesas: Decimal
    maior_receita: Decimal
    maior_despesa: Decimal
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "total_transacoes": 45,
                "media_mensal_receitas": 3500.00,
                "media_mensal_despesas": 2800.00,
                "maior_receita": 5000.00,
                "maior_despesa": 1200.00
            }
        }
    )


class AccountListResponse(BaseModel):
    """Resposta paginada de contas"""
    accounts: list[AccountResponse]
    total: int
    skip: int
    limit: int

    model_config = ConfigDict(from_attributes=True)
