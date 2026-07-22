"""CaseCategory — FIR, UDR, PAR, Zero FIR, etc."""

from __future__ import annotations

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class CaseCategory(Base):
    __tablename__ = "cip_case_category"

    case_category_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    lookup_value: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    category_code: Mapped[str] = mapped_column(String(1), unique=True, nullable=False)
