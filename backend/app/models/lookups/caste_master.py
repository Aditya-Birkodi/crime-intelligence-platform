"""CasteMaster lookup."""

from __future__ import annotations

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class CasteMaster(Base):
    __tablename__ = "cip_caste_master"

    caste_master_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    caste_master_name: Mapped[str] = mapped_column(
        String(100), unique=True, nullable=False
    )
