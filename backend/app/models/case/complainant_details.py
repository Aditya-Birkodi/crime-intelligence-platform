"""ComplainantDetails linked to CaseMaster."""

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base

if TYPE_CHECKING:
    from app.models.case.case_master import CaseMaster


class ComplainantDetails(Base):
    __tablename__ = "cip_complainant_details"

    complainant_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    case_master_id: Mapped[int] = mapped_column(
        ForeignKey("cip_case_master.case_master_id"), nullable=False, index=True
    )
    complainant_name: Mapped[str] = mapped_column(String(150), nullable=False)
    age_year: Mapped[int | None] = mapped_column(Integer, nullable=True)
    occupation_id: Mapped[int | None] = mapped_column(
        ForeignKey("cip_occupation_master.occupation_id"), nullable=True
    )
    religion_id: Mapped[int | None] = mapped_column(
        ForeignKey("cip_religion_master.religion_id"), nullable=True
    )
    caste_id: Mapped[int | None] = mapped_column(
        ForeignKey("cip_caste_master.caste_master_id"), nullable=True
    )
    gender_id: Mapped[str | None] = mapped_column(String(1), nullable=True)

    case: Mapped[CaseMaster] = relationship(back_populates="complainants")
