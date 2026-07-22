"""Pydantic stubs for `Accused`.

TODO: Accused persons for a CaseMaster (1:N); PersonID sorting A1/A2/….
TODO: Add Create/Update/Read schemas with field validation.
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class AccusedBase(BaseModel):
    """Shared fields for `Accused` DTOs.

    TODO: Declare fields matching the ER diagram.
    """

    model_config = ConfigDict(from_attributes=True)


class AccusedRead(AccusedBase):
    """Read model for `Accused`.

    TODO: Include primary key and nested relations as needed.
    """

    pass


class AccusedCreate(AccusedBase):
    """Create payload for `Accused`.

    TODO: Required fields only.
    """

    pass
