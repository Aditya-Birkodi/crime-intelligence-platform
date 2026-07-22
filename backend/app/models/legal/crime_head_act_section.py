"""Maps CrimeHead to Act+Section."""

from __future__ import annotations

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class CrimeHeadActSection(Base):
    __tablename__ = "cip_crime_head_act_section"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    crime_head_id: Mapped[int] = mapped_column(
        ForeignKey("cip_crime_head.crime_head_id"), nullable=False
    )
    act_code: Mapped[str] = mapped_column(
        ForeignKey("cip_act.act_code"), nullable=False
    )
    section_code: Mapped[str] = mapped_column(String(20), nullable=False)
