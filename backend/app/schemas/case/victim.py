"""Pydantic stubs for `Victim`.

TODO: Victim records for a CaseMaster (1:N).
TODO: Add Create/Update/Read schemas with field validation.
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class VictimBase(BaseModel):
    """Shared fields for `Victim` DTOs.

    TODO: Declare fields matching the ER diagram.
    """

    model_config = ConfigDict(from_attributes=True)


class VictimRead(VictimBase):
    """Read model for `Victim`.

    TODO: Include primary key and nested relations as needed.
    """

    pass


class VictimCreate(VictimBase):
    """Create payload for `Victim`.

    TODO: Required fields only.
    """

    pass
