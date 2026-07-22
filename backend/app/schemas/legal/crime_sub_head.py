"""Pydantic stubs for `CrimeSubHead`.

TODO: Crime sub-head under CrimeHead.
TODO: Add Create/Update/Read schemas with field validation.
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class CrimeSubHeadBase(BaseModel):
    """Shared fields for `CrimeSubHead` DTOs.

    TODO: Declare fields matching the ER diagram.
    """

    model_config = ConfigDict(from_attributes=True)


class CrimeSubHeadRead(CrimeSubHeadBase):
    """Read model for `CrimeSubHead`.

    TODO: Include primary key and nested relations as needed.
    """

    pass


class CrimeSubHeadCreate(CrimeSubHeadBase):
    """Create payload for `CrimeSubHead`.

    TODO: Required fields only.
    """

    pass
