"""
Helpers for working with SQLAlchemy enums.
"""

from __future__ import annotations

from enum import Enum
from typing import List, Type


def enum_values(enum_cls: Type[Enum]) -> List[str]:
    """
    Return the value of each enum member.

    SQLAlchemy's Enum column type stores the member ``name`` by default.
    Our database columns now contain the localized values, so we instruct
    SQLAlchemy to use ``value`` via ``values_callable=enum_values``.
    """
    return [member.value for member in enum_cls]


__all__ = ["enum_values"]
