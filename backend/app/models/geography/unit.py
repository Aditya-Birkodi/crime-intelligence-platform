"""Unit / police station."""

from __future__ import annotations

from sqlalchemy import Boolean, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class Unit(Base):
    __tablename__ = "cip_unit"

    unit_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=False)
    unit_name: Mapped[str] = mapped_column(String(150), nullable=False)
    type_id: Mapped[int] = mapped_column(
        ForeignKey("cip_unit_type.unit_type_id"), nullable=False
    )
    parent_unit: Mapped[int | None] = mapped_column(
        ForeignKey("cip_unit.unit_id"), nullable=True
    )
    state_id: Mapped[int] = mapped_column(
        ForeignKey("cip_state.state_id"), nullable=False
    )
    district_id: Mapped[int] = mapped_column(
        ForeignKey("cip_district.district_id"), nullable=False
    )
    active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
