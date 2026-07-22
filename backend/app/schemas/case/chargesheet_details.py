"""Pydantic stubs for `ChargesheetDetails`.

TODO: Chargesheet / final report (types A/B/C) for a case.
TODO: Add Create/Update/Read schemas with field validation.
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class ChargesheetDetailsBase(BaseModel):
    """Shared fields for `ChargesheetDetails` DTOs.

    TODO: Declare fields matching the ER diagram.
    """

    model_config = ConfigDict(from_attributes=True)


class ChargesheetDetailsRead(ChargesheetDetailsBase):
    """Read model for `ChargesheetDetails`.

    TODO: Include primary key and nested relations as needed.
    """

    pass


class ChargesheetDetailsCreate(ChargesheetDetailsBase):
    """Create payload for `ChargesheetDetails`.

    TODO: Required fields only.
    """

    pass
