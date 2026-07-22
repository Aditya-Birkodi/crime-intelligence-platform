"""Pydantic stubs for `Act`.

TODO: Legal act master (e.g. IPC, NDPS); PK ActCode.
TODO: Add Create/Update/Read schemas with field validation.
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class ActBase(BaseModel):
    """Shared fields for `Act` DTOs.

    TODO: Declare fields matching the ER diagram.
    """

    model_config = ConfigDict(from_attributes=True)


class ActRead(ActBase):
    """Read model for `Act`.

    TODO: Include primary key and nested relations as needed.
    """

    pass


class ActCreate(ActBase):
    """Create payload for `Act`.

    TODO: Required fields only.
    """

    pass
