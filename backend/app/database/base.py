"""SQLAlchemy DeclarativeBase for all ORM models.

TODO: Add common mixin columns (created_at, updated_at, audit) once schema is finalized.
"""

from __future__ import annotations

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):  # type: ignore[misc]
    """Shared declarative base for FIR domain models."""

    pass
