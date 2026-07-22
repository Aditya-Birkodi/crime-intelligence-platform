"""Accused linked to CaseMaster."""

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base

if TYPE_CHECKING:
    from app.models.case.case_master import CaseMaster


class Accused(Base):
    __tablename__ = "cip_accused"

    accused_master_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    case_master_id: Mapped[int] = mapped_column(
        ForeignKey("cip_case_master.case_master_id"), nullable=False, index=True
    )
    accused_name: Mapped[str] = mapped_column(String(150), nullable=False)
    age_year: Mapped[int | None] = mapped_column(Integer, nullable=True)
    gender_id: Mapped[str | None] = mapped_column(String(1), nullable=True)
    person_id: Mapped[str | None] = mapped_column(String(10), nullable=True)

    case: Mapped[CaseMaster] = relationship(back_populates="accused")
