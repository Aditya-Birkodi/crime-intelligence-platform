"""Pydantic stubs for `ReligionMaster`.

TODO: Religion lookup for complainants.
TODO: Add Create/Update/Read schemas with field validation.
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class ReligionMasterBase(BaseModel):
    """Shared fields for `ReligionMaster` DTOs.

    TODO: Declare fields matching the ER diagram.
    """

    model_config = ConfigDict(from_attributes=True)


class ReligionMasterRead(ReligionMasterBase):
    """Read model for `ReligionMaster`.

    TODO: Include primary key and nested relations as needed.
    """

    pass


class ReligionMasterCreate(ReligionMasterBase):
    """Create payload for `ReligionMaster`.

    TODO: Required fields only.
    """

    pass
