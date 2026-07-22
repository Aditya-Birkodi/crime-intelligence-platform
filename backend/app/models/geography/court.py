"""Court master."""

from __future__ import annotations

from sqlalchemy import Boolean, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class Court(Base):
    __tablename__ = "cip_court"

    court_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    court_name: Mapped[str] = mapped_column(String(200), nullable=False)
    district_id: Mapped[int] = mapped_column(
        ForeignKey("cip_district.district_id"), nullable=False
    )
    state_id: Mapped[int] = mapped_column(
        ForeignKey("cip_state.state_id"), nullable=False
    )
    active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
