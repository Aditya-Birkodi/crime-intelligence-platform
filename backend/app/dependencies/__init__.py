"""FastAPI dependency injection providers.

TODO: Add get_current_user via Catalyst Authentication and get_cache via Catalyst Cache.
"""

from __future__ import annotations

from collections.abc import Generator
from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from app.core.config import Settings, get_settings
from app.database.session import get_db

DbSession = Annotated[Session, Depends(get_db)]


def settings_dependency() -> Settings:
    """Provide application settings."""
    return get_settings()


def db_dependency(db: DbSession) -> Generator[Session, None, None]:
    """Provide a SQLAlchemy session (local) / Catalyst Data Store adapter (prod TODO)."""
    yield db
