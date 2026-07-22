"""Pydantic stubs for `OccupationMaster`.

TODO: Occupation lookup for complainants.
TODO: Add Create/Update/Read schemas with field validation.
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class OccupationMasterBase(BaseModel):
    """Shared fields for `OccupationMaster` DTOs.

    TODO: Declare fields matching the ER diagram.
    """

    model_config = ConfigDict(from_attributes=True)


class OccupationMasterRead(OccupationMasterBase):
    """Read model for `OccupationMaster`.

    TODO: Include primary key and nested relations as needed.
    """

    pass


class OccupationMasterCreate(OccupationMasterBase):
    """Create payload for `OccupationMaster`.

    TODO: Required fields only.
    """

    pass
