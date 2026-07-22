"""CaseMaster — central FIR aggregate root."""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import Date, DateTime, ForeignKey, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base

if TYPE_CHECKING:
    from app.models.case.accused import Accused
    from app.models.case.act_section_association import ActSectionAssociation
    from app.models.case.complainant_details import ComplainantDetails
    from app.models.case.victim import Victim


class CaseMaster(Base):
    __tablename__ = "cip_case_master"

    case_master_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    crime_no: Mapped[str] = mapped_column(
        String(18), unique=True, nullable=False, index=True
    )
    case_no: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    crime_registered_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    police_station_id: Mapped[int] = mapped_column(
        ForeignKey("cip_unit.unit_id"), nullable=False, index=True
    )
    case_category_id: Mapped[int] = mapped_column(
        ForeignKey("cip_case_category.case_category_id"), nullable=False
    )
    gravity_offence_id: Mapped[int | None] = mapped_column(
        ForeignKey("cip_gravity_offence.gravity_offence_id"), nullable=True
    )
    crime_major_head_id: Mapped[int | None] = mapped_column(
        ForeignKey("cip_crime_head.crime_head_id"), nullable=True, index=True
    )
    crime_minor_head_id: Mapped[int | None] = mapped_column(
        ForeignKey("cip_crime_sub_head.crime_sub_head_id"), nullable=True
    )
    case_status_id: Mapped[int] = mapped_column(
        ForeignKey("cip_case_status_master.case_status_id"), nullable=False, index=True
    )
    court_id: Mapped[int | None] = mapped_column(
        ForeignKey("cip_court.court_id"), nullable=True
    )
    incident_from_date: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    incident_to_date: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    info_received_ps_date: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    latitude: Mapped[Decimal | None] = mapped_column(Numeric(10, 7), nullable=True)
    longitude: Mapped[Decimal | None] = mapped_column(Numeric(10, 7), nullable=True)
    brief_facts: Mapped[str | None] = mapped_column(Text, nullable=True)

    victims: Mapped[list[Victim]] = relationship(
        back_populates="case", cascade="all, delete-orphan"
    )
    accused: Mapped[list[Accused]] = relationship(
        back_populates="case", cascade="all, delete-orphan"
    )
    complainants: Mapped[list[ComplainantDetails]] = relationship(
        back_populates="case", cascade="all, delete-orphan"
    )
    act_sections: Mapped[list[ActSectionAssociation]] = relationship(
        back_populates="case", cascade="all, delete-orphan"
    )
