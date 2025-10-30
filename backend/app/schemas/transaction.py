"""
Schemas Pydantic para Transaction
"""

import uuid
from datetime import datetime, date
from decimal import Decimal
from typing import Optional, List

from pydantic import BaseModel, Field, ConfigDict, validator

from app.models.transaction import TransactionType, TransactionStatus, PaymentMethod


class TransactionBase(BaseModel):
    """Schema base para transação"""
    account_id: uuid.UUID = Field(..., description="ID da conta")
    category_id: Optional[uuid.UUID] = Field(None, description="ID da categoria")
    tipo: TransactionType = Field(..., description="Tipo da transação")
    valor: Decimal = Field(..., gt=0, description="Valor da transação")
    moeda: str = Field(default="BRL", max_length=3, description="Moeda")
    data_lancamento: date = Field(..., description="Data do lançamento")
    data_competencia: Optional[date] = Field(None, description="Data de competência")
    descricao: str = Field(..., min_length=1, max_length=255, description="Descrição")
    observacoes: Optional[str] = Field(None, description="Observações adicionais")
    status: TransactionStatus = Field(default=TransactionStatus.PENDING, description="Status")
    payment_method: Optional[PaymentMethod] = Field(None, description="Método de pagamento")
    tags: List[str] = Field(default_factory=list, description="Tags da transação")


class TransactionCreate(TransactionBase):
    """Schema para criação de transação"""
    # Campos para parcelas
    parcelas_total: Optional[int] = Field(None, ge=1, le=120, description="Total de parcelas")
    
    # Campos para transferência
    transfer_account_id: Optional[uuid.UUID] = Field(None, description="Conta de destino para transferência")
    
    @validator('transfer_account_id')
    def validate_transfer(cls, v, values):
        if values.get('tipo') == TransactionType.TRANSFER and not v:
            raise ValueError('transfer_account_id é obrigatório para transferências')
        if values.get('tipo') != TransactionType.TRANSFER and v:
            raise ValueError('transfer_account_id só pode ser usado em transferências')
        return v
    
    @validator('category_id')
    def validate_category_for_transfer(cls, v, values):
        if values.get('tipo') == TransactionType.TRANSFER and v:
            raise ValueError('Transferências não devem ter categoria')
        return v
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "account_id": "123e4567-e89b-12d3-a456-426614174000",
                "category_id": "456e7890-e89b-12d3-a456-426614174000",
                "tipo": "expense",
                "valor": 150.50,
                "moeda": "BRL",
                "data_lancamento": "2024-01-15",
                "data_competencia": "2024-01-15",
                "descricao": "Supermercado Extra",
                "observacoes": "Compras da semana",
                "status": "cleared",
                "payment_method": "debit",
                "tags": ["supermercado", "alimentação"]
            }
        }
    )


class TransactionUpdate(BaseModel):
    """Schema para atualização de transação"""
    category_id: Optional[uuid.UUID] = None
    valor: Optional[Decimal] = Field(None, gt=0)
    data_lancamento: Optional[date] = None
    data_competencia: Optional[date] = None
    descricao: Optional[str] = Field(None, min_length=1, max_length=255)
    observacoes: Optional[str] = None
    status: Optional[TransactionStatus] = None
    payment_method: Optional[PaymentMethod] = None
    tags: Optional[List[str]] = None
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "descricao": "Supermercado Extra - Atualizado",
                "status": "reconciled",
                "tags": ["supermercado", "alimentação", "semanal"]
            }
        }
    )


class TransactionResponse(TransactionBase):
    """Schema de resposta para transação"""
    id: uuid.UUID
    user_id: uuid.UUID
    valor_formatado: str
    is_income: bool
    is_expense: bool
    is_transfer: bool
    is_installment: bool
    installment_display: Optional[str] = None
    status_display: str
    payment_method_display: str
    data_efetiva: date
    
    # Campos de parcelas
    parcela_atual: Optional[int] = None
    parcelas_total: Optional[int] = None
    grupo_parcelas: Optional[uuid.UUID] = None
    
    # Campos de transferência
    transfer_account_id: Optional[uuid.UUID] = None
    transfer_transaction_id: Optional[uuid.UUID] = None
    
    # Campos de anexo
    attachment_url: Optional[str] = None
    attachment_name: Optional[str] = None
    
    # Campos de recorrência
    recurring_rule_id: Optional[uuid.UUID] = None
    
    # Campos de conciliação
    reconciled_at: Optional[datetime] = None
    bank_reference: Optional[str] = None
    
    # Timestamps
    criado_em: datetime
    atualizado_em: datetime
    
    model_config = ConfigDict(from_attributes=True)


class TransactionWithDetails(TransactionResponse):
    """Schema de transação com detalhes relacionados"""
    account_name: Optional[str] = None
    category_name: Optional[str] = None
    category_color: Optional[str] = None
    transfer_account_name: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)


class TransactionSummary(BaseModel):
    """Schema para resumo de transações"""
    total_transacoes: int
    total_receitas: Decimal
    total_despesas: Decimal
    saldo_periodo: Decimal
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "total_transacoes": 45,
                "total_receitas": 5000.00,
                "total_despesas": 3250.00,
                "saldo_periodo": 1750.00
            }
        }
    )


class TransactionListResponse(BaseModel):
    """Resposta paginada de transações"""
    transactions: List[TransactionResponse]
    total: int
    skip: int
    limit: int

    model_config = ConfigDict(from_attributes=True)


class TransactionImport(BaseModel):
    """Schema para importação de transações"""
    account_id: uuid.UUID = Field(..., description="Conta de destino")
    file_type: str = Field(..., description="Tipo do arquivo (csv, ofx)")
    column_mapping: dict = Field(..., description="Mapeamento de colunas")
    dry_run: bool = Field(default=True, description="Executar em modo teste")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "account_id": "123e4567-e89b-12d3-a456-426614174000",
                "file_type": "csv",
                "column_mapping": {
                    "data": "Data",
                    "descricao": "Descrição",
                    "valor": "Valor",
                    "tipo": "Tipo"
                },
                "dry_run": True
            }
        }
    )


class TransactionImportResult(BaseModel):
    """Schema para resultado da importação"""
    total_linhas: int
    linhas_processadas: int
    linhas_com_erro: int
    transacoes_criadas: int
    erros: List[str]
    preview: List[dict]
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "total_linhas": 100,
                "linhas_processadas": 95,
                "linhas_com_erro": 5,
                "transacoes_criadas": 95,
                "erros": ["Linha 10: Valor inválido", "Linha 25: Data inválida"],
                "preview": [
                    {
                        "data": "2024-01-15",
                        "descricao": "Supermercado",
                        "valor": 150.50,
                        "tipo": "expense"
                    }
                ]
            }
        }
    )


class TransactionBulkUpdate(BaseModel):
    """Schema para atualização em massa"""
    transaction_ids: List[uuid.UUID] = Field(..., description="IDs das transações")
    updates: dict = Field(..., description="Campos para atualizar")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "transaction_ids": [
                    "123e4567-e89b-12d3-a456-426614174000",
                    "456e7890-e89b-12d3-a456-426614174000"
                ],
                "updates": {
                    "status": "cleared",
                    "category_id": "789e0123-e89b-12d3-a456-426614174000"
                }
            }
        }
    )


class TransactionFilter(BaseModel):
    """Schema para filtros de transação"""
    date_from: Optional[date] = None
    date_to: Optional[date] = None
    month: Optional[int] = Field(None, ge=1, le=12)
    year: Optional[int] = Field(None, ge=2000)
    account_id: Optional[uuid.UUID] = None
    category_id: Optional[uuid.UUID] = None
    tipo: Optional[TransactionType] = None
    status: Optional[TransactionStatus] = None
    payment_method: Optional[PaymentMethod] = None
    min_value: Optional[Decimal] = Field(None, ge=0)
    max_value: Optional[Decimal] = Field(None, ge=0)
    tags: Optional[List[str]] = None
    q: Optional[str] = Field(None, description="Busca textual na descrição")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "date_from": "2024-01-01",
                "date_to": "2024-01-31",
                "account_id": "123e4567-e89b-12d3-a456-426614174000",
                "tipo": "expense",
                "status": "cleared",
                "min_value": 50.00,
                "max_value": 500.00,
                "tags": ["alimentação"],
                "q": "supermercado"
            }
        }
    )
