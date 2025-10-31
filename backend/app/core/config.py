"""
Configurações da aplicação usando Pydantic Settings v2
"""

import json
from typing import List, Optional
from functools import lru_cache

from pydantic import Field, validator, PrivateAttr, AliasChoices
from pydantic_settings import BaseSettings, SettingsConfigDict


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
    cors_origins_raw: Optional[str] = Field(
        default=None,
        env="CORS_ORIGINS",
        validation_alias=AliasChoices("cors_origins", "CORS_ORIGINS"),
        repr=False,
    )
    _cors_origins: List[str] = PrivateAttr(default_factory=lambda: ["http://localhost:5173"])
    
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

    def model_post_init(self, __context) -> None:
        parsed = self._parse_cors_origins(self.cors_origins_raw)
        if parsed:
            object.__setattr__(self, "_cors_origins", parsed)

    @staticmethod
    def _parse_cors_origins(value: Optional[str]) -> List[str]:
        if not value:
            return []

        stripped = value.strip()
        if not stripped:
            return []

        if stripped.startswith("[") and stripped.endswith("]"):
            try:
                parsed = json.loads(stripped)
                if isinstance(parsed, list):
                    return [
                        str(origin).strip()
                        for origin in parsed
                        if str(origin).strip()
                    ]
            except json.JSONDecodeError:
                pass

        normalized = stripped.replace("\n", ",")
        origins: List[str] = []
        for part in normalized.split(","):
            token = part.strip().strip("\"'")
            if token:
                origins.append(token)
        return origins

    @property
    def cors_origins(self) -> List[str]:
        return self._cors_origins

    @cors_origins.setter
    def cors_origins(self, value: List[str]) -> None:
        object.__setattr__(self, "_cors_origins", value)
    
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
