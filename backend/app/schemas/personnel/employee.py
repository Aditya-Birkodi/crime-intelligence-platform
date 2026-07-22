"""Pydantic stubs for `Employee`.

TODO: Police employee; KGID, Rank, Designation, Unit, District.
TODO: Add Create/Update/Read schemas with field validation.
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class EmployeeBase(BaseModel):
    """Shared fields for `Employee` DTOs.

    TODO: Declare fields matching the ER diagram.
    """

    model_config = ConfigDict(from_attributes=True)


class EmployeeRead(EmployeeBase):
    """Read model for `Employee`.

    TODO: Include primary key and nested relations as needed.
    """

    pass


class EmployeeCreate(EmployeeBase):
    """Create payload for `Employee`.

    TODO: Required fields only.
    """

    pass
