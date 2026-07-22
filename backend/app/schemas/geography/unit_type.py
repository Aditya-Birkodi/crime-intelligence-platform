"""Pydantic stubs for `UnitType`.

TODO: Unit type (Police Station, Circle Office, …).
TODO: Add Create/Update/Read schemas with field validation.
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class UnitTypeBase(BaseModel):
    """Shared fields for `UnitType` DTOs.

    TODO: Declare fields matching the ER diagram.
    """

    model_config = ConfigDict(from_attributes=True)


class UnitTypeRead(UnitTypeBase):
    """Read model for `UnitType`.

    TODO: Include primary key and nested relations as needed.
    """

    pass


class UnitTypeCreate(UnitTypeBase):
    """Create payload for `UnitType`.

    TODO: Required fields only.
    """

    pass
