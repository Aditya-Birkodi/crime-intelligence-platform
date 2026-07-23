"""Database engine and session factory.

Local development uses PostgreSQL via DATABASE_URL.
When PERSISTENCE_BACKEND=catalyst, engine creation is deferred so AppSail
can boot without a reachable Postgres.
"""

from __future__ import annotations

from collections.abc import Generator

from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import get_settings

_engine: Engine | None = None
_SessionLocal: sessionmaker[Session] | None = None


def get_engine() -> Engine:
    global _engine, _SessionLocal
    if _engine is None:
        settings = get_settings()
        _engine = create_engine(
            settings.database.database_url,
            pool_size=settings.database.pool_size,
            max_overflow=settings.database.max_overflow,
            pool_pre_ping=True,
        )
        _SessionLocal = sessionmaker(
            bind=_engine, autocommit=False, autoflush=False, class_=Session
        )
    return _engine


def get_session_factory() -> sessionmaker[Session]:
    get_engine()
    assert _SessionLocal is not None
    return _SessionLocal


# Backwards-compatible names used by older imports
def __getattr__(name: str) -> object:
    if name == "engine":
        return get_engine()
    if name == "SessionLocal":
        return get_session_factory()
    raise AttributeError(name)


def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency yielding a DB session."""
    db = get_session_factory()()
    try:
        yield db
    finally:
        db.close()
