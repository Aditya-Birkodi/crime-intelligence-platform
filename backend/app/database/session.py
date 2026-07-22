"""Database engine and session factory.

Local development uses PostgreSQL via DATABASE_URL.
Production SHOULD use Catalyst Data Store adapters.

TODO: Add Catalyst Data Store session adapter and async engine option (asyncpg).
"""

from __future__ import annotations

from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import get_settings

_settings = get_settings()

engine = create_engine(
    _settings.database.database_url,
    pool_size=_settings.database.pool_size,
    max_overflow=_settings.database.max_overflow,
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(
    bind=engine, autocommit=False, autoflush=False, class_=Session
)


def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency yielding a DB session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
