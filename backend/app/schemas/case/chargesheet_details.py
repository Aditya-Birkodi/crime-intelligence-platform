"""Pydantic schemas for `ChargesheetDetails`."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ChargesheetDetailsRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    cs_id: int
    case_master_id: int
    cs_date: datetime | None = None
    cs_type: str
    police_person_id: int | None = None


class ChargesheetDetailsCreate(BaseModel):
    cs_date: datetime | None = None
    cs_type: str = Field(..., min_length=1, max_length=1)
    police_person_id: int | None = None
