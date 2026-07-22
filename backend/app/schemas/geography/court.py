"""Pydantic stubs for `Court`.

TODO: Court master; District/State FKs.
TODO: Add Create/Update/Read schemas with field validation.
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class CourtBase(BaseModel):
    """Shared fields for `Court` DTOs.

    TODO: Declare fields matching the ER diagram.
    """

    model_config = ConfigDict(from_attributes=True)


class CourtRead(CourtBase):
    """Read model for `Court`.

    TODO: Include primary key and nested relations as needed.
    """

    pass


class CourtCreate(CourtBase):
    """Create payload for `Court`.

    TODO: Required fields only.
    """

    pass
