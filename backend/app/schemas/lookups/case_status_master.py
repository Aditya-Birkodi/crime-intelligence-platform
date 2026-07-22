"""Pydantic stubs for `CaseStatusMaster`.

TODO: Case status (Under Investigation, Charge Sheeted, Closed, …).
TODO: Add Create/Update/Read schemas with field validation.
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class CaseStatusMasterBase(BaseModel):
    """Shared fields for `CaseStatusMaster` DTOs.

    TODO: Declare fields matching the ER diagram.
    """

    model_config = ConfigDict(from_attributes=True)


class CaseStatusMasterRead(CaseStatusMasterBase):
    """Read model for `CaseStatusMaster`.

    TODO: Include primary key and nested relations as needed.
    """

    pass


class CaseStatusMasterCreate(CaseStatusMasterBase):
    """Create payload for `CaseStatusMaster`.

    TODO: Required fields only.
    """

    pass
