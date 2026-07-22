"""UnitType — Police Station, Circle Office, etc."""

from __future__ import annotations

from sqlalchemy import Boolean, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class UnitType(Base):
    __tablename__ = "cip_unit_type"

    unit_type_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    unit_type_name: Mapped[str] = mapped_column(
        String(100), unique=True, nullable=False
    )
    city_dist_state: Mapped[str | None] = mapped_column(String(50), nullable=True)
    hierarchy: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
