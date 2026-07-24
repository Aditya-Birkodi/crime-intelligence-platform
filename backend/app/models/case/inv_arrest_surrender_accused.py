"""Junction: ArrestSurrender ↔ Accused (ER: inv_arrestsurrenderaccused)."""

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base

if TYPE_CHECKING:
    from app.models.case.arrest_surrender import ArrestSurrender


class InvArrestSurrenderAccused(Base):
    __tablename__ = "cip_inv_arrest_surrender_accused"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    arrest_surrender_id: Mapped[int] = mapped_column(
        ForeignKey("cip_arrest_surrender.arrest_surrender_id"),
        nullable=False,
        index=True,
    )
    accused_master_id: Mapped[int] = mapped_column(
        ForeignKey("cip_accused.accused_master_id"), nullable=False, index=True
    )

    arrest: Mapped[ArrestSurrender] = relationship(back_populates="accused_links")
