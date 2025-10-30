"""
Configuração do banco de dados SQLAlchemy 2.0
"""

from __future__ import annotations

from pathlib import Path

from sqlalchemy import MetaData, create_engine, event
from sqlalchemy.engine import make_url
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.config import settings


raw_database_url = settings.database_url
database_url = make_url(raw_database_url)

if database_url.get_backend_name() == "sqlite" and not settings.is_testing:
    raise RuntimeError(
        "SQLite nao e mais suportado fora de ambientes de testes. "
        "Defina DATABASE_URL apontando para o cluster Neon PostgreSQL."
    )

engine_kwargs: dict = {
    "echo": settings.debug,  # Log SQL queries apenas quando debug ativo
}

if database_url.get_backend_name() == "sqlite":
    # Resolve caminho para o arquivo SQLite (caso não seja absoluto)
    database_path = database_url.database
    if database_path and database_path != ":memory:":
        resolved_path = Path(database_path)
        if not resolved_path.is_absolute():
            project_root = Path(__file__).resolve().parents[2]
            resolved_path = (project_root / resolved_path).resolve()
        resolved_path.parent.mkdir(parents=True, exist_ok=True)
        database_url = database_url.set(database=resolved_path.as_posix())

    engine_kwargs["connect_args"] = {"check_same_thread": False}

    # Usa StaticPool apenas para banco em memória
    if database_url.database in (None, "", ":memory:"):
        engine_kwargs["poolclass"] = StaticPool
else:
    engine_kwargs.update(
        {
            "pool_pre_ping": True,  # Verifica conexões antes de usar
            "pool_recycle": 3600,  # Recicla conexões a cada hora
        }
    )

    if database_url.get_backend_name().startswith("postgresql"):
        engine_kwargs["connect_args"] = {
            "options": "-c timezone=UTC"  # Força timezone UTC no PostgreSQL
        }

# Configuração do engine
engine = create_engine(database_url, **engine_kwargs)

if database_url.get_backend_name() == "sqlite":
    @event.listens_for(engine, "connect")
    def _set_sqlite_pragma(dbapi_connection, connection_record):  # pragma: no cover
        """Garante suporte a chaves estrangeiras no SQLite."""
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

# Session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

# Base para modelos
Base = declarative_base()

# Metadata com convenções de nomenclatura
convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}

Base.metadata = MetaData(naming_convention=convention)
