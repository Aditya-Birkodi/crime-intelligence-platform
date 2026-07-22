"""ORM stub for ER table `ArrestSurrender`.

TODO: Arrest/surrender events; FKs to State/District/Unit/Employee/Court/Accused.
TODO: Add SQLAlchemy Mapped columns — no business logic in this scaffold.
"""

from __future__ import annotations

from app.database.base import Base


class ArrestSurrender(Base):
    """Placeholder model for `ArrestSurrender`.

    TODO: Define __tablename__ and columns from Police_FIR_ER_Diagram.pdf.
    """

    __abstract__ = True
