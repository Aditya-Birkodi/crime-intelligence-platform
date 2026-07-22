"""Pydantic stubs for `Inv_OccuranceTime`.

TODO: Occurrence time/location record (1:1 with CaseMaster per ER matrix).
TODO: Add Create/Update/Read schemas with field validation.
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class InvOccuranceTimeBase(BaseModel):
    """Shared fields for `Inv_OccuranceTime` DTOs.

    TODO: Declare fields matching the ER diagram.
    """

    model_config = ConfigDict(from_attributes=True)


class InvOccuranceTimeRead(InvOccuranceTimeBase):
    """Read model for `Inv_OccuranceTime`.

    TODO: Include primary key and nested relations as needed.
    """

    pass


class InvOccuranceTimeCreate(InvOccuranceTimeBase):
    """Create payload for `Inv_OccuranceTime`.

    TODO: Required fields only.
    """

    pass
