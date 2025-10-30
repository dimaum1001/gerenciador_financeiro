"""
Backend package bootstrap.

This module ensures the internal `app` package remains importable even when
the project is executed from outside the backend directory (e.g. Render).
"""

from __future__ import annotations

import sys
from pathlib import Path

_BACKEND_ROOT = Path(__file__).resolve().parent

if str(_BACKEND_ROOT) not in sys.path:
    # Inserimos o diretório do backend no sys.path para que `import app`
    # funcione mesmo quando o processo é iniciado a partir do diretório raiz.
    sys.path.insert(0, str(_BACKEND_ROOT))


__all__ = ["_BACKEND_ROOT"]
