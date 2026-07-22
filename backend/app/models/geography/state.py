"""State master."""

from __future__ import annotations

from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class State(Base):
    __tablename__ = "cip_state"

    state_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    state_name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
