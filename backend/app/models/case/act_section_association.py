"""Act/Section applied to a case."""

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base

if TYPE_CHECKING:
    from app.models.case.case_master import CaseMaster


class ActSectionAssociation(Base):
    __tablename__ = "cip_act_section_association"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    case_master_id: Mapped[int] = mapped_column(
        ForeignKey("cip_case_master.case_master_id"), nullable=False, index=True
    )
    act_id: Mapped[str] = mapped_column(ForeignKey("cip_act.act_code"), nullable=False)
    section_id: Mapped[str] = mapped_column(String(20), nullable=False)
    act_order_id: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    section_order_id: Mapped[int] = mapped_column(Integer, default=1, nullable=False)

    case: Mapped[CaseMaster] = relationship(back_populates="act_sections")
