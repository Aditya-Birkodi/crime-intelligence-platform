"""Pydantic stubs for `ActSectionAssociation`.

TODO: Junction of CaseMaster ↔ Act ↔ Section with display order.
TODO: Add Create/Update/Read schemas with field validation.
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class ActSectionAssociationBase(BaseModel):
    """Shared fields for `ActSectionAssociation` DTOs.

    TODO: Declare fields matching the ER diagram.
    """

    model_config = ConfigDict(from_attributes=True)


class ActSectionAssociationRead(ActSectionAssociationBase):
    """Read model for `ActSectionAssociation`.

    TODO: Include primary key and nested relations as needed.
    """

    pass


class ActSectionAssociationCreate(ActSectionAssociationBase):
    """Create payload for `ActSectionAssociation`.

    TODO: Required fields only.
    """

    pass
