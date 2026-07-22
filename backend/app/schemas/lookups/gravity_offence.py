"""Pydantic stubs for `GravityOffence`.

TODO: Offence gravity (Heinous / Non-Heinous).
TODO: Add Create/Update/Read schemas with field validation.
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class GravityOffenceBase(BaseModel):
    """Shared fields for `GravityOffence` DTOs.

    TODO: Declare fields matching the ER diagram.
    """

    model_config = ConfigDict(from_attributes=True)


class GravityOffenceRead(GravityOffenceBase):
    """Read model for `GravityOffence`.

    TODO: Include primary key and nested relations as needed.
    """

    pass


class GravityOffenceCreate(GravityOffenceBase):
    """Create payload for `GravityOffence`.

    TODO: Required fields only.
    """

    pass
