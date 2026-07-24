"""ArrestSurrender — arrest / surrender events (ER: ArrestSurrender)."""

from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Date, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base

if TYPE_CHECKING:
    from app.models.case.case_master import CaseMaster
    from app.models.case.inv_arrest_surrender_accused import InvArrestSurrenderAccused


class ArrestSurrender(Base):
    __tablename__ = "cip_arrest_surrender"

    arrest_surrender_id: Mapped[int] = mapped_column(
        primary_key=True, autoincrement=True
    )
    case_master_id: Mapped[int] = mapped_column(
        ForeignKey("cip_case_master.case_master_id"), nullable=False, index=True
    )
    # 1 = arrest, 2 = voluntary surrender (lookup-style int per ER)
    arrest_surrender_type_id: Mapped[int] = mapped_column(Integer, nullable=False)
    arrest_surrender_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    arrest_surrender_state_id: Mapped[int | None] = mapped_column(
        ForeignKey("cip_state.state_id"), nullable=True
    )
    arrest_surrender_district_id: Mapped[int | None] = mapped_column(
        ForeignKey("cip_district.district_id"), nullable=True
    )
    police_station_id: Mapped[int | None] = mapped_column(
        ForeignKey("cip_unit.unit_id"), nullable=True
    )
    io_id: Mapped[int | None] = mapped_column(
        ForeignKey("cip_employee.employee_id"), nullable=True
    )
    court_id: Mapped[int | None] = mapped_column(
        ForeignKey("cip_court.court_id"), nullable=True
    )
    accused_master_id: Mapped[int | None] = mapped_column(
        ForeignKey("cip_accused.accused_master_id"), nullable=True
    )
    is_accused: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_complainant_accused: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )

    case: Mapped[CaseMaster] = relationship(back_populates="arrests")
    accused_links: Mapped[list[InvArrestSurrenderAccused]] = relationship(
        back_populates="arrest", cascade="all, delete-orphan"
    )
