"""ChargesheetDetails — final report / chargesheet (ER: ChargesheetDetails)."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base

if TYPE_CHECKING:
    from app.models.case.case_master import CaseMaster


class ChargesheetDetails(Base):
    __tablename__ = "cip_chargesheet_details"

    cs_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    case_master_id: Mapped[int] = mapped_column(
        ForeignKey("cip_case_master.case_master_id"), nullable=False, index=True
    )
    cs_date: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    # A = Chargesheet, B = False Case, C = Undetected
    cs_type: Mapped[str] = mapped_column(String(1), nullable=False)
    police_person_id: Mapped[int | None] = mapped_column(
        ForeignKey("cip_employee.employee_id"), nullable=True
    )

    case: Mapped[CaseMaster] = relationship(back_populates="chargesheets")
