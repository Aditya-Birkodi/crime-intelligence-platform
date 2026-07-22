"""Pydantic stubs for `District`.

TODO: District under State.
TODO: Add Create/Update/Read schemas with field validation.
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class DistrictBase(BaseModel):
    """Shared fields for `District` DTOs.

    TODO: Declare fields matching the ER diagram.
    """

    model_config = ConfigDict(from_attributes=True)


class DistrictRead(DistrictBase):
    """Read model for `District`.

    TODO: Include primary key and nested relations as needed.
    """

    pass


class DistrictCreate(DistrictBase):
    """Create payload for `District`.

    TODO: Required fields only.
    """

    pass
