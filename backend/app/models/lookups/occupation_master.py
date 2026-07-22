"""OccupationMaster lookup."""

from __future__ import annotations

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class OccupationMaster(Base):
    __tablename__ = "cip_occupation_master"

    occupation_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    occupation_name: Mapped[str] = mapped_column(
        String(100), unique=True, nullable=False
    )
