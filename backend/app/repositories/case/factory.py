"""Resolve CaseStore from PERSISTENCE_BACKEND."""

from __future__ import annotations

from collections.abc import Generator
from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.database.session import SessionLocal
from app.repositories.case.case_store import CaseStore
from app.repositories.case.catalyst_case_store import CatalystCaseStore
from app.repositories.case.postgres_case_store import PostgresCaseStore


def get_case_store() -> Generator[CaseStore, None, None]:
    """Postgres (default/CI) or Catalyst Data Store (hackathon/prod / mock)."""
    settings = get_settings()
    if settings.persistence_backend == "catalyst":
        yield CatalystCaseStore()
        return

    db: Session = SessionLocal()
    try:
        yield PostgresCaseStore(db)
    finally:
        db.close()


CaseStoreDep = Annotated[CaseStore, Depends(get_case_store)]
