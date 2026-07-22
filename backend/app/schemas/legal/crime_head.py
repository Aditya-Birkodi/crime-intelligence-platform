"""Pydantic stubs for `CrimeHead`.

TODO: Major crime head / crime group.
TODO: Add Create/Update/Read schemas with field validation.
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class CrimeHeadBase(BaseModel):
    """Shared fields for `CrimeHead` DTOs.

    TODO: Declare fields matching the ER diagram.
    """

    model_config = ConfigDict(from_attributes=True)


class CrimeHeadRead(CrimeHeadBase):
    """Read model for `CrimeHead`.

    TODO: Include primary key and nested relations as needed.
    """

    pass


class CrimeHeadCreate(CrimeHeadBase):
    """Create payload for `CrimeHead`.

    TODO: Required fields only.
    """

    pass
