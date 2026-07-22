"""Section under an Act."""

from __future__ import annotations

from sqlalchemy import Boolean, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class Section(Base):
    __tablename__ = "cip_section"
    __table_args__ = (
        UniqueConstraint("act_code", "section_code", name="uq_act_section"),
    )

    section_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    act_code: Mapped[str] = mapped_column(
        ForeignKey("cip_act.act_code"), nullable=False
    )
    section_code: Mapped[str] = mapped_column(String(20), nullable=False)
    section_description: Mapped[str] = mapped_column(String(500), nullable=False)
    active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
