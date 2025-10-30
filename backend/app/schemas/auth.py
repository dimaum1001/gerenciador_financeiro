"""
Schemas Pydantic para autenticação
"""

from typing import Optional
from pydantic import BaseModel, EmailStr, Field, ConfigDict, AliasChoices

from app.schemas.user import UserResponse


class LoginRequest(BaseModel):
    """Schema para requisição de login"""
    email: EmailStr = Field(..., description="Email do usuario")
    senha: str = Field(
        ...,
        description="Senha do usuario",
        validation_alias=AliasChoices("senha", "password"),
    )
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "email": "admin@demo.com",
                "senha": "admin123"
            }
        }
    )


class LoginResponse(BaseModel):
    """Schema para resposta de login"""
    access_token: str = Field(..., description="Token JWT de acesso")
    token_type: str = Field(default="bearer", description="Tipo do token")
    expires_in: int = Field(..., description="Tempo de expiração em segundos")
    user: UserResponse = Field(..., description="Dados do usuário")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "expires_in": 259200,
                "user": {
                    "id": "123e4567-e89b-12d3-a456-426614174000",
                    "nome": "Administrador",
                    "email": "admin@demo.com",
                    "ativo": True,
                    "email_verificado": True,
                    "timezone": "America/Sao_Paulo",
                    "moeda_padrao": "BRL",
                    "formato_data": "DD/MM/YYYY"
                }
            }
        }
    )


class TokenData(BaseModel):
    """Schema para dados do token"""
    user_id: Optional[str] = None


class PasswordResetRequest(BaseModel):
    """Schema para solicitação de reset de senha"""
    email: EmailStr = Field(..., description="Email do usuario")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "email": "usuario@exemplo.com"
            }
        }
    )


class PasswordResetConfirm(BaseModel):
    """Schema para confirmação de reset de senha"""
    token: str = Field(..., description="Token de reset")
    nova_senha: str = Field(..., min_length=8, description="Nova senha")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "nova_senha": "novasenha123"
            }
        }
    )


class RefreshTokenRequest(BaseModel):
    """Schema para renovação de token"""
    refresh_token: str = Field(..., description="Token de renovação")


class ApiKeyResponse(BaseModel):
    """Schema para resposta de chave de API"""
    api_key: str = Field(..., description="Chave de API gerada")
    created_at: str = Field(..., description="Data de criação")
    expires_at: Optional[str] = Field(None, description="Data de expiração")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "api_key": "fmgr_1234567890abcdef",
                "created_at": "2024-01-01T10:00:00Z",
                "expires_at": "2024-12-31T23:59:59Z"
            }
        }
    )
