"""Pydantic schemas for `ComplainantDetails`."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class ComplainantDetailsRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    complainant_id: int
    case_master_id: int
    complainant_name: str
    age_year: int | None = None
    gender_id: str | None = None
    occupation_id: int | None = None
    religion_id: int | None = None
    caste_id: int | None = None


class ComplainantDetailsCreate(BaseModel):
    complainant_name: str = Field(..., min_length=1, max_length=150)
    age_year: int | None = None
    gender_id: str | None = Field(default=None, max_length=1)
    occupation_id: int | None = None
    religion_id: int | None = None
    caste_id: int | None = None
