"""Pydantic schemas for `Inv_OccuranceTime`."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class InvOccuranceTimeRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    case_master_id: int
    occurrence_from: datetime | None = None
    occurrence_to: datetime | None = None
    place_of_occurrence: str | None = None
    beat_number: str | None = None
    distance_from_ps_km: Decimal | None = None
    direction_from_ps: str | None = None
    village_or_city: str | None = None


class InvOccuranceTimeCreate(BaseModel):
    occurrence_from: datetime | None = None
    occurrence_to: datetime | None = None
    place_of_occurrence: str | None = None
    beat_number: str | None = Field(default=None, max_length=20)
    distance_from_ps_km: Decimal | None = None
    direction_from_ps: str | None = Field(default=None, max_length=50)
    village_or_city: str | None = Field(default=None, max_length=150)
