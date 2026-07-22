"""Pydantic stubs for `Section`.

TODO: Section under an Act; FK ActCode.
TODO: Add Create/Update/Read schemas with field validation.
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class SectionBase(BaseModel):
    """Shared fields for `Section` DTOs.

    TODO: Declare fields matching the ER diagram.
    """

    model_config = ConfigDict(from_attributes=True)


class SectionRead(SectionBase):
    """Read model for `Section`.

    TODO: Include primary key and nested relations as needed.
    """

    pass


class SectionCreate(SectionBase):
    """Create payload for `Section`.

    TODO: Required fields only.
    """

    pass
