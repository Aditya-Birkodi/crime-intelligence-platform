"""Rank — police rank hierarchy (ER: Rank)."""

from __future__ import annotations

from sqlalchemy import Boolean, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class Rank(Base):
    __tablename__ = "cip_rank"

    rank_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    rank_name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    hierarchy: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
