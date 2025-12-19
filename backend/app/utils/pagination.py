"""
Utilitários de paginação.

O objetivo é reduzir round-trips ao banco (principalmente em conexões remotas),
evitando o padrão "count() + select". Usamos COUNT(*) OVER() para obter o total
na mesma consulta do retorno paginado.
"""

from __future__ import annotations

from typing import List, Tuple, TypeVar

from sqlalchemy import func
from sqlalchemy.orm import Query

T = TypeVar("T")


def paginate_query(query: Query, *, skip: int, limit: int) -> Tuple[List[T], int]:
    """
    Retorna itens e total em uma única query usando window function.

    Observação:
        - `query` deve selecionar uma única entidade ORM (ex: db.query(Model)).
        - Para listas pequenas, isso tende a ser mais rápido em bancos remotos
          (ex: Neon) do que fazer `count()` separado.
    """
    total_expr = func.count().over().label("total")
    rows = query.add_columns(total_expr).offset(skip).limit(limit).all()

    if not rows:
        return [], 0

    items = [row[0] for row in rows]
    total = int(rows[0][1] or 0)
    return items, total

