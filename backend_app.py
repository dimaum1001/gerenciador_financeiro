"""
Gunicorn entrypoint for Render/production.

This small module avoids having to tweak PYTHONPATH or working directories.
"""

from backend.app.main import app  # noqa: F401
