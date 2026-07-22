"""Pydantic stubs for `Rank`.

TODO: Police rank hierarchy.
TODO: Add Create/Update/Read schemas with field validation.
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class RankBase(BaseModel):
    """Shared fields for `Rank` DTOs.

    TODO: Declare fields matching the ER diagram.
    """

    model_config = ConfigDict(from_attributes=True)


class RankRead(RankBase):
    """Read model for `Rank`.

    TODO: Include primary key and nested relations as needed.
    """

    pass


class RankCreate(RankBase):
    """Create payload for `Rank`.

    TODO: Required fields only.
    """

    pass
