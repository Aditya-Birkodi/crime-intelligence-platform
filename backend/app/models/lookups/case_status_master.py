"""CaseStatusMaster — Under Investigation, Charge Sheeted, Closed, etc."""

from __future__ import annotations

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class CaseStatusMaster(Base):
    __tablename__ = "cip_case_status_master"

    case_status_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    case_status_name: Mapped[str] = mapped_column(
        String(100), unique=True, nullable=False
    )
