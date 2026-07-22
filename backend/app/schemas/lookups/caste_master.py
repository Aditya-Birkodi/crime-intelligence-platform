"""Pydantic stubs for `CasteMaster`.

TODO: Caste lookup for complainants.
TODO: Add Create/Update/Read schemas with field validation.
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class CasteMasterBase(BaseModel):
    """Shared fields for `CasteMaster` DTOs.

    TODO: Declare fields matching the ER diagram.
    """

    model_config = ConfigDict(from_attributes=True)


class CasteMasterRead(CasteMasterBase):
    """Read model for `CasteMaster`.

    TODO: Include primary key and nested relations as needed.
    """

    pass


class CasteMasterCreate(CasteMasterBase):
    """Create payload for `CasteMaster`.

    TODO: Required fields only.
    """

    pass
