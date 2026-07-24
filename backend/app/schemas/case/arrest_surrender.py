"""Pydantic schemas for `ArrestSurrender`."""

from __future__ import annotations

from datetime import date

from pydantic import BaseModel, ConfigDict


class ArrestSurrenderRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    arrest_surrender_id: int
    case_master_id: int
    arrest_surrender_type_id: int
    arrest_surrender_date: date | None = None
    arrest_surrender_state_id: int | None = None
    arrest_surrender_district_id: int | None = None
    police_station_id: int | None = None
    io_id: int | None = None
    court_id: int | None = None
    accused_master_id: int | None = None
    is_accused: bool = True
    is_complainant_accused: bool = False


class ArrestSurrenderCreate(BaseModel):
    arrest_surrender_type_id: int
    arrest_surrender_date: date | None = None
    arrest_surrender_state_id: int | None = None
    arrest_surrender_district_id: int | None = None
    police_station_id: int | None = None
    io_id: int | None = None
    court_id: int | None = None
    accused_master_id: int | None = None
    is_accused: bool = True
    is_complainant_accused: bool = False
