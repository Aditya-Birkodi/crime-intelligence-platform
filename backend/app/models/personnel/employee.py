"""ORM stub for ER table `Employee`.

TODO: Police employee; KGID, Rank, Designation, Unit, District.
TODO: Add SQLAlchemy Mapped columns — no business logic in this scaffold.
"""

from __future__ import annotations

from app.database.base import Base


class Employee(Base):
    """Placeholder model for `Employee`.

    TODO: Define __tablename__ and columns from Police_FIR_ER_Diagram.pdf.
    """

    __abstract__ = True
