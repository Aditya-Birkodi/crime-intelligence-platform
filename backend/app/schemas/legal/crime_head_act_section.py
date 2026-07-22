"""Pydantic stubs for `CrimeHeadActSection`.

TODO: Maps CrimeHead to Act+Section combinations.
TODO: Add Create/Update/Read schemas with field validation.
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class CrimeHeadActSectionBase(BaseModel):
    """Shared fields for `CrimeHeadActSection` DTOs.

    TODO: Declare fields matching the ER diagram.
    """

    model_config = ConfigDict(from_attributes=True)


class CrimeHeadActSectionRead(CrimeHeadActSectionBase):
    """Read model for `CrimeHeadActSection`.

    TODO: Include primary key and nested relations as needed.
    """

    pass


class CrimeHeadActSectionCreate(CrimeHeadActSectionBase):
    """Create payload for `CrimeHeadActSection`.

    TODO: Required fields only.
    """

    pass
