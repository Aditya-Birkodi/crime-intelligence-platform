"""Designation — IO, SHO, etc. (ER: Designation)."""

from __future__ import annotations

from sqlalchemy import Boolean, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class Designation(Base):
    __tablename__ = "cip_designation"

    designation_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    designation_name: Mapped[str] = mapped_column(
        String(100), unique=True, nullable=False
    )
    active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    sort_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
