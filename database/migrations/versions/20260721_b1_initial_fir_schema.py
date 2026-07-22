"""B1 initial FIR schema.

Revision ID: 20260721_b1
Revises:
Create Date: 2026-07-21
"""

from __future__ import annotations

from collections.abc import Sequence

from alembic import op

revision: str = "20260721_b1"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Use metadata create_all via models for local speed; this revision
    # documents B1 schema and runs create_all-equivalent DDL for Postgres.
    import app.models  # noqa: F401
    from app.database.base import Base

    bind = op.get_bind()
    Base.metadata.create_all(bind=bind)


def downgrade() -> None:
    import app.models  # noqa: F401
    from app.database.base import Base

    bind = op.get_bind()
    Base.metadata.drop_all(bind=bind)
