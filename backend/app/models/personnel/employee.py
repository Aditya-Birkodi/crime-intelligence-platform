"""Employee — police personnel (ER: Employee)."""

from __future__ import annotations

from datetime import date

from sqlalchemy import Boolean, Date, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class Employee(Base):
    __tablename__ = "cip_employee"

    employee_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    district_id: Mapped[int] = mapped_column(
        ForeignKey("cip_district.district_id"), nullable=False, index=True
    )
    unit_id: Mapped[int] = mapped_column(
        ForeignKey("cip_unit.unit_id"), nullable=False, index=True
    )
    rank_id: Mapped[int] = mapped_column(ForeignKey("cip_rank.rank_id"), nullable=False)
    designation_id: Mapped[int] = mapped_column(
        ForeignKey("cip_designation.designation_id"), nullable=False
    )
    kgid: Mapped[str] = mapped_column(String(30), unique=True, nullable=False)
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    employee_dob: Mapped[date | None] = mapped_column(Date, nullable=True)
    gender_id: Mapped[str | None] = mapped_column(String(1), nullable=True)
    blood_group_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    physically_challenged: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )
    appointment_date: Mapped[date | None] = mapped_column(Date, nullable=True)
