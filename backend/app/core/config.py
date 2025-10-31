"""
Configurações da aplicação usando Pydantic Settings v2
"""

import os
import json
from typing import Any, List, Optional
from functools import lru_cache

from pydantic import Field, validator
from pydantic_settings import BaseSettings, SettingsConfigDict


def _flexible_json_loads(value: Any) -> Any:
    """
    Permite que variáveis de ambiente complexas sejam carregadas como JSON quando possível,
    mantendo suporte a valores simples (strings separadas por vírgula, vazio, etc.).
    """
    if value is None or isinstance(value, (list, dict)):
        return value

    if isinstance(value, str):
        stripped = value.strip()
        if not stripped:
            return ""
        try:
            return json.loads(stripped)
        except json.JSONDecodeError:
            return stripped

    return value


class Settings(BaseSettings):
    """Configurações da aplicação"""
    
    # App Info
    app_name: str = "Gerenciador Financeiro API"
    app_version: str = "1.0.0"
    app_description: str = "API completa para gestão financeira multi-conta"
    
    # Environment
    environment: str = Field(default="development", env="ENVIRONMENT")
    debug: bool = Field(default=False, env="DEBUG")
    timezone: str = Field(default="America/Sao_Paulo", env="TZ")
    
    # Database
    database_url: str = Field(env="DATABASE_URL")
    
    # Security
    secret_key: str = Field(env="SECRET_KEY")
    access_token_expire_minutes: int = Field(default=4320, env="ACCESS_TOKEN_EXPIRE_MINUTES")  # 3 days
    algorithm: str = "HS256"
    
    # CORS
    cors_origins: List[str] = Field(default=["http://localhost:5173"], env="CORS_ORIGINS")
    
    @validator("cors_origins", pre=True)
    def parse_cors_origins(cls, v):
        if isinstance(v, str):
            value = v.strip()
            if value.startswith("[") and value.endswith("]"):
                try:
                    parsed = json.loads(value)
                    if isinstance(parsed, list):
                        return [str(origin).strip() for origin in parsed]
                except json.JSONDecodeError:
                    pass
            return [
                origin.strip().strip("\"'")
                for origin in value.split(",")
                if origin.strip()
            ]
        return v
    
    # Logging
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    log_format: str = Field(default="json", env="LOG_FORMAT")
    
    # File Upload
    max_file_size: int = Field(default=10485760, env="MAX_FILE_SIZE")  # 10MB
    allowed_extensions: List[str] = Field(default=["csv", "xlsx", "xls", "ofx", "qif"], env="ALLOWED_EXTENSIONS")
    upload_path: str = Field(default="storage/attachments", env="UPLOAD_PATH")
    
    @validator("allowed_extensions", pre=True)
    def parse_allowed_extensions(cls, v):
        if isinstance(v, str):
            return [ext.strip() for ext in v.split(",")]
        return v
    
    # Rate Limiting
    rate_limit_per_minute: int = Field(default=60, env="RATE_LIMIT_PER_MINUTE")
    rate_limit_burst: int = Field(default=10, env="RATE_LIMIT_BURST")
    
    # Cache
    redis_url: Optional[str] = Field(default=None, env="REDIS_URL")
    cache_ttl: int = Field(default=3600, env="CACHE_TTL")
    
    # Monitoring
    sentry_dsn: Optional[str] = Field(default=None, env="SENTRY_DSN")
    prometheus_enabled: bool = Field(default=False, env="PROMETHEUS_ENABLED")
    
    # Email
    smtp_host: Optional[str] = Field(default=None, env="SMTP_HOST")
    smtp_port: int = Field(default=587, env="SMTP_PORT")
    smtp_user: Optional[str] = Field(default=None, env="SMTP_USER")
    smtp_password: Optional[str] = Field(default=None, env="SMTP_PASSWORD")
    smtp_from_email: str = Field(default="noreply@finance.com", env="SMTP_FROM_EMAIL")
    smtp_use_tls: bool = Field(default=True, env="SMTP_USE_TLS")
    
    # Features
    enable_import: bool = Field(default=True, env="ENABLE_IMPORT")
    enable_export: bool = Field(default=True, env="ENABLE_EXPORT")
    enable_attachments: bool = Field(default=True, env="ENABLE_ATTACHMENTS")
    enable_recurring: bool = Field(default=True, env="ENABLE_RECURRING")
    enable_budgets: bool = Field(default=True, env="ENABLE_BUDGETS")
    
    # Backup
    backup_enabled: bool = Field(default=False, env="BACKUP_ENABLED")
    backup_schedule: str = Field(default="0 2 * * *", env="BACKUP_SCHEDULE")
    backup_retention_days: int = Field(default=30, env="BACKUP_RETENTION_DAYS")
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    @staticmethod
    def _wrap_source(source):
        def _inner():
            data = source()
            if not data:
                return data
            return {key: _flexible_json_loads(value) for key, value in data.items()}
        return _inner

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls,
        init_settings,
        env_settings,
        dotenv_settings,
        file_secret_settings,
    ):
        wrapped_env = cls._wrap_source(env_settings) if env_settings else env_settings
        wrapped_dotenv = cls._wrap_source(dotenv_settings) if dotenv_settings else dotenv_settings
        return (
            init_settings,
            wrapped_env,
            wrapped_dotenv,
            file_secret_settings,
        )
    
    @property
    def is_development(self) -> bool:
        return self.environment.lower() == "development"
    
    @property
    def is_production(self) -> bool:
        return self.environment.lower() == "production"
    
    @property
    def is_testing(self) -> bool:
        return self.environment.lower() == "testing"


@lru_cache()
def get_settings() -> Settings:
    """Retorna instância singleton das configurações"""
    return Settings()


# Instância global das configurações
settings = get_settings()
