"""Crime sub-head under CrimeHead."""

from __future__ import annotations

from sqlalchemy import Boolean, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class CrimeSubHead(Base):
    __tablename__ = "cip_crime_sub_head"

    crime_sub_head_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    crime_head_id: Mapped[int] = mapped_column(
        ForeignKey("cip_crime_head.crime_head_id"), nullable=False
    )
    crime_head_name: Mapped[str] = mapped_column(String(150), nullable=False)
    seq_id: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
