"""
Gunicorn entrypoint for Render/production.

This module guarantees the backend package is importable no matter the working
directory used by the host platform (e.g. Render).
"""

from __future__ import annotations

import sys
from pathlib import Path

# Caminho absoluto do diretório `backend`.
_BACKEND_DIR = Path(__file__).resolve().parent / "backend"

if not _BACKEND_DIR.exists():
    raise RuntimeError(f"Backend directory not found at {_BACKEND_DIR}")

# Inserimos o caminho do backend explicitamente para evitar depender do CWD.
if str(_BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(_BACKEND_DIR))

from app.main import app  # noqa: E402  # pylint: disable=wrong-import-position

__all__ = ["app"]
