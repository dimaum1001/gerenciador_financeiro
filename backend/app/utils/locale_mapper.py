"""
Ferramentas para traduzir valores de enums entre inglês (legado) e português.

Esta camada permite que os endpoints aceitem termos em português sem quebrar
clientes existentes, além de expor os nomes em português nas respostas com
campos adicionais. A migração definitiva do banco ocorrerá em etapas futuras.
"""

from __future__ import annotations

import unicodedata
from dataclasses import dataclass
from enum import Enum
from typing import Dict, Optional, Type, TypeVar, Union

TEnum = TypeVar("TEnum", bound=Enum)


def _normalize_token(token: str) -> str:
    """Normaliza strings para comparação (minúsculo, sem acentos)."""
    normalized = unicodedata.normalize("NFD", token.strip().lower())
    return "".join(char for char in normalized if not unicodedata.combining(char))


@dataclass
class EnumLocaleMapper:
    """Mapeia valores legados (inglês) para português e vice-versa."""

    enum_cls: Type[TEnum]
    en_to_pt: Dict[str, str]

    def __post_init__(self) -> None:
        # token normalizado -> valor canônico (sempre o valor real do Enum)
        self._token_to_canonical: Dict[str, str] = {}
        # valor canônico -> string em português (para exibição)
        self._canonical_to_pt: Dict[str, str] = {}
        # valor canônico -> string legada em inglês
        self._canonical_to_en: Dict[str, str] = {}

        # Registrar todos os valores reais do Enum (já estão em português)
        for member in self.enum_cls:
            canonical = member.value
            self._token_to_canonical.setdefault(_normalize_token(member.value), canonical)
            self._token_to_canonical.setdefault(_normalize_token(member.name), canonical)
            self._canonical_to_pt.setdefault(canonical, member.value)

        # Registrar traduções legadas (inglês <-> português)
        for legacy_value, portuguese in self.en_to_pt.items():
            canonical = portuguese
            normalized_legacy = _normalize_token(legacy_value)
            normalized_pt = _normalize_token(portuguese)

            self._token_to_canonical[normalized_legacy] = canonical
            self._token_to_canonical[normalized_pt] = canonical

            self._canonical_to_pt.setdefault(canonical, portuguese)
            self._canonical_to_en.setdefault(canonical, legacy_value)

    def _canonical_value(self, value: Union[str, TEnum]) -> Optional[str]:
        if isinstance(value, self.enum_cls):
            return value.value
        token = _normalize_token(str(value))
        return self._token_to_canonical.get(token)

    def to_enum(self, value: Union[str, TEnum, None]) -> Optional[TEnum]:
        """Converte valor (PT/EN) em Enum."""
        if value is None or value == "":
            return None
        canonical = self._canonical_value(value)
        if canonical is None:
            raise ValueError(
                f"Valor '{value}' não é suportado para {self.enum_cls.__name__}"
            )
        try:
            return self.enum_cls(canonical)
        except ValueError as exc:  # pragma: no cover - fallback defensivo
            raise ValueError(
                f"Valor '{value}' não é suportado para {self.enum_cls.__name__}"
            ) from exc

    def to_portuguese(self, value: Union[str, TEnum, None]) -> Optional[str]:
        """Retorna representação em português."""
        enum_value = self.to_enum(value)
        if enum_value is None:
            return None
        canonical = enum_value.value
        return self._canonical_to_pt.get(canonical, canonical)

    def legacy_value(self, value: Union[str, TEnum, None]) -> Optional[str]:
        """Retorna o valor legado (inglês)."""
        enum_value = self.to_enum(value)
        if enum_value is None:
            return None
        canonical = enum_value.value
        return self._canonical_to_en.get(canonical, canonical)


# ----- Instâncias de mapeadores ------------------------------------------------
from app.models.account import AccountType  # noqa: E402
from app.models.category import CategoryType  # noqa: E402
from app.models.transaction import TransactionType, TransactionStatus, PaymentMethod  # noqa: E402
from app.models.budget import BudgetStatus  # noqa: E402
from app.models.recurring_rule import RecurrenceFrequency, RecurrenceStatus  # noqa: E402

account_type_mapper = EnumLocaleMapper(
    AccountType,
    {
        "cash": "dinheiro",
        "checking": "conta_corrente",
        "savings": "poupanca",
        "credit": "cartao_credito",
        "investment": "investimento",
        "other": "outros",
    },
)

category_type_mapper = EnumLocaleMapper(
    CategoryType,
    {
        "income": "receita",
        "expense": "despesa",
    },
)

transaction_type_mapper = EnumLocaleMapper(
    TransactionType,
    {
        "income": "receita",
        "expense": "despesa",
        "transfer": "transferencia",
    },
)

transaction_status_mapper = EnumLocaleMapper(
    TransactionStatus,
    {
        "pending": "pendente",
        "cleared": "compensada",
        "reconciled": "conciliada",
    },
)

payment_method_mapper = EnumLocaleMapper(
    PaymentMethod,
    {
        "cash": "dinheiro",
        "pix": "pix",
        "debit": "cartao_debito",
        "credit": "cartao_credito",
        "boleto": "boleto",
        "transfer": "transferencia",
        "check": "cheque",
        "other": "outros",
    },
)

budget_status_mapper = EnumLocaleMapper(
    BudgetStatus,
    {
        "active": "ativo",
        "paused": "pausado",
        "completed": "concluido",
        "exceeded": "excedido",
    },
)

recurrence_frequency_mapper = EnumLocaleMapper(
    RecurrenceFrequency,
    {
        "daily": "diario",
        "weekly": "semanal",
        "monthly": "mensal",
        "quarterly": "trimestral",
        "yearly": "anual",
    },
)

recurrence_status_mapper = EnumLocaleMapper(
    RecurrenceStatus,
    {
        "active": "ativa",
        "paused": "pausada",
        "completed": "concluida",
        "cancelled": "cancelada",
    },
)


__all__ = [
    "account_type_mapper",
    "category_type_mapper",
    "transaction_type_mapper",
    "transaction_status_mapper",
    "payment_method_mapper",
    "budget_status_mapper",
    "recurrence_frequency_mapper",
    "recurrence_status_mapper",
]
