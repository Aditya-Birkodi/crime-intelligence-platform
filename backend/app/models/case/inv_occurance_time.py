"""Inv_OccuranceTime — 1:1 occurrence place/time detail for a CaseMaster."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base

if TYPE_CHECKING:
    from app.models.case.case_master import CaseMaster


class InvOccuranceTime(Base):
    """Occurrence place / beat detail (ER: Inv_OccuranceTime)."""

    __tablename__ = "cip_inv_occurance_time"

    case_master_id: Mapped[int] = mapped_column(
        ForeignKey("cip_case_master.case_master_id"), primary_key=True
    )
    occurrence_from: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    occurrence_to: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    place_of_occurrence: Mapped[str | None] = mapped_column(Text, nullable=True)
    beat_number: Mapped[str | None] = mapped_column(String(20), nullable=True)
    distance_from_ps_km: Mapped[float | None] = mapped_column(
        Numeric(8, 2), nullable=True
    )
    direction_from_ps: Mapped[str | None] = mapped_column(String(50), nullable=True)
    village_or_city: Mapped[str | None] = mapped_column(String(150), nullable=True)

    case: Mapped[CaseMaster] = relationship(back_populates="occurrence")
