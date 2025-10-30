"""
Tipos personalizados para suporte multi-banco.
"""

from __future__ import annotations

import uuid
from typing import Any

from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.types import CHAR, TypeDecorator


class GUID(TypeDecorator):
    """
    Representa UUID de forma compatível entre PostgreSQL e SQLite.

    Em PostgreSQL utiliza o tipo nativo UUID, enquanto em bancos que não
    possuem suporte (como SQLite) armazena como texto.
    """

    impl = CHAR
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == "postgresql":
            return dialect.type_descriptor(PG_UUID(as_uuid=True))
        return dialect.type_descriptor(CHAR(36))

    def process_bind_param(self, value: Any, dialect):
        if value is None:
            return value

        if isinstance(value, uuid.UUID):
            return str(value)

        return str(uuid.UUID(str(value)))

    def process_result_value(self, value: Any, dialect):
        if value is None:
            return value

        if isinstance(value, uuid.UUID):
            return value

        return uuid.UUID(str(value))
