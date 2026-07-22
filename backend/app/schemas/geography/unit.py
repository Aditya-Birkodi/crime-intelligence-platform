"""Pydantic stubs for `Unit`.

TODO: Police unit / station; hierarchical ParentUnit.
TODO: Add Create/Update/Read schemas with field validation.
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class UnitBase(BaseModel):
    """Shared fields for `Unit` DTOs.

    TODO: Declare fields matching the ER diagram.
    """

    model_config = ConfigDict(from_attributes=True)


class UnitRead(UnitBase):
    """Read model for `Unit`.

    TODO: Include primary key and nested relations as needed.
    """

    pass


class UnitCreate(UnitBase):
    """Create payload for `Unit`.

    TODO: Required fields only.
    """

    pass
