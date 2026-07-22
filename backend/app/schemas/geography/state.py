"""Pydantic stubs for `State`.

TODO: State master; referenced by District, Unit, Court, ArrestSurrender.
TODO: Add Create/Update/Read schemas with field validation.
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class StateBase(BaseModel):
    """Shared fields for `State` DTOs.

    TODO: Declare fields matching the ER diagram.
    """

    model_config = ConfigDict(from_attributes=True)


class StateRead(StateBase):
    """Read model for `State`.

    TODO: Include primary key and nested relations as needed.
    """

    pass


class StateCreate(StateBase):
    """Create payload for `State`.

    TODO: Required fields only.
    """

    pass
