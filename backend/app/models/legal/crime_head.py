"""Major crime head."""

from __future__ import annotations

from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class CrimeHead(Base):
    __tablename__ = "cip_crime_head"

    crime_head_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    crime_group_name: Mapped[str] = mapped_column(
        String(150), unique=True, nullable=False
    )
    active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
