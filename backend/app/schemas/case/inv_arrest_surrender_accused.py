"""Pydantic stubs for `inv_arrestsurrenderaccused`.

TODO: Junction linking ArrestSurrender to multiple Accused.
TODO: Add Create/Update/Read schemas with field validation.
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class InvArrestSurrenderAccusedBase(BaseModel):
    """Shared fields for `inv_arrestsurrenderaccused` DTOs.

    TODO: Declare fields matching the ER diagram.
    """

    model_config = ConfigDict(from_attributes=True)


class InvArrestSurrenderAccusedRead(InvArrestSurrenderAccusedBase):
    """Read model for `inv_arrestsurrenderaccused`.

    TODO: Include primary key and nested relations as needed.
    """

    pass


class InvArrestSurrenderAccusedCreate(InvArrestSurrenderAccusedBase):
    """Create payload for `inv_arrestsurrenderaccused`.

    TODO: Required fields only.
    """

    pass
