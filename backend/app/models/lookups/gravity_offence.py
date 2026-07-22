"""GravityOffence — Heinous / Non-Heinous."""

from __future__ import annotations

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class GravityOffence(Base):
    __tablename__ = "cip_gravity_offence"

    gravity_offence_id: Mapped[int] = mapped_column(
        primary_key=True, autoincrement=True
    )
    lookup_value: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
