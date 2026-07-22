"""Pydantic stubs for `ComplainantDetails`.

TODO: Complainant linked to CaseMaster; FKs to Occupation/Religion/Caste masters.
TODO: Add Create/Update/Read schemas with field validation.
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class ComplainantDetailsBase(BaseModel):
    """Shared fields for `ComplainantDetails` DTOs.

    TODO: Declare fields matching the ER diagram.
    """

    model_config = ConfigDict(from_attributes=True)


class ComplainantDetailsRead(ComplainantDetailsBase):
    """Read model for `ComplainantDetails`.

    TODO: Include primary key and nested relations as needed.
    """

    pass


class ComplainantDetailsCreate(ComplainantDetailsBase):
    """Create payload for `ComplainantDetails`.

    TODO: Required fields only.
    """

    pass
