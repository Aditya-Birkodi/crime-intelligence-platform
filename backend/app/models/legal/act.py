"""Act master (IPC, NDPS, …)."""

from __future__ import annotations

from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class Act(Base):
    __tablename__ = "cip_act"

    act_code: Mapped[str] = mapped_column(String(20), primary_key=True)
    act_description: Mapped[str] = mapped_column(String(255), nullable=False)
    short_name: Mapped[str | None] = mapped_column(String(50), nullable=True)
    active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
