"""Pydantic stubs for `CaseCategory`.

TODO: Case category (FIR, UDR, PAR, …).
TODO: Add Create/Update/Read schemas with field validation.
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class CaseCategoryBase(BaseModel):
    """Shared fields for `CaseCategory` DTOs.

    TODO: Declare fields matching the ER diagram.
    """

    model_config = ConfigDict(from_attributes=True)


class CaseCategoryRead(CaseCategoryBase):
    """Read model for `CaseCategory`.

    TODO: Include primary key and nested relations as needed.
    """

    pass


class CaseCategoryCreate(CaseCategoryBase):
    """Create payload for `CaseCategory`.

    TODO: Required fields only.
    """

    pass
