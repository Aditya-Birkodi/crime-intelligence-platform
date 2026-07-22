"""Pydantic stubs for `Designation`.

TODO: Designation (IO, SHO, …).
TODO: Add Create/Update/Read schemas with field validation.
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class DesignationBase(BaseModel):
    """Shared fields for `Designation` DTOs.

    TODO: Declare fields matching the ER diagram.
    """

    model_config = ConfigDict(from_attributes=True)


class DesignationRead(DesignationBase):
    """Read model for `Designation`.

    TODO: Include primary key and nested relations as needed.
    """

    pass


class DesignationCreate(DesignationBase):
    """Create payload for `Designation`.

    TODO: Required fields only.
    """

    pass
