"""Pydantic stubs for `ArrestSurrender`.

TODO: Arrest/surrender events; FKs to State/District/Unit/Employee/Court/Accused.
TODO: Add Create/Update/Read schemas with field validation.
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class ArrestSurrenderBase(BaseModel):
    """Shared fields for `ArrestSurrender` DTOs.

    TODO: Declare fields matching the ER diagram.
    """

    model_config = ConfigDict(from_attributes=True)


class ArrestSurrenderRead(ArrestSurrenderBase):
    """Read model for `ArrestSurrender`.

    TODO: Include primary key and nested relations as needed.
    """

    pass


class ArrestSurrenderCreate(ArrestSurrenderBase):
    """Create payload for `ArrestSurrender`.

    TODO: Required fields only.
    """

    pass
