"""Analytics + intelligence FIR entities (Arrest, Chargesheet, Employee, Occurrence).

Revision ID: 20260723_b1_intel
Revises: 20260721_b1
Create Date: 2026-07-23
"""

from __future__ import annotations

from collections.abc import Sequence

from alembic import op

revision: str = "20260723_b1_intel"
down_revision: str | None = "20260721_b1"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    import app.models  # noqa: F401
    from app.database.base import Base

    bind = op.get_bind()
    Base.metadata.create_all(bind=bind)


def downgrade() -> None:
    # Keep prior tables; only drop intel-era tables if present.
    op.execute("DROP TABLE IF EXISTS cip_inv_arrest_surrender_accused CASCADE")
    op.execute("DROP TABLE IF EXISTS cip_arrest_surrender CASCADE")
    op.execute("DROP TABLE IF EXISTS cip_chargesheet_details CASCADE")
    op.execute("DROP TABLE IF EXISTS cip_inv_occurance_time CASCADE")
    # police_person_id column may remain; safe for local demo
