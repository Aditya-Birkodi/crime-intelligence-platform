"""Pydantic schemas for CaseMaster and nested parties."""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.case.arrest_surrender import ArrestSurrenderRead
from app.schemas.case.chargesheet_details import ChargesheetDetailsRead
from app.schemas.case.complainant_details import (
    ComplainantDetailsCreate,
    ComplainantDetailsRead,
)
from app.schemas.case.inv_occurance_time import InvOccuranceTimeRead


class VictimRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    victim_master_id: int
    case_master_id: int
    victim_name: str
    age_year: int | None = None
    gender_id: str | None = None
    victim_police: str | None = None


class VictimCreate(BaseModel):
    victim_name: str = Field(..., min_length=1, max_length=150)
    age_year: int | None = None
    gender_id: str | None = Field(default=None, max_length=1)
    victim_police: str | None = Field(default="0", max_length=1)


class AccusedRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    accused_master_id: int
    case_master_id: int
    accused_name: str
    age_year: int | None = None
    gender_id: str | None = None
    person_id: str | None = None


class AccusedCreate(BaseModel):
    accused_name: str = Field(..., min_length=1, max_length=150)
    age_year: int | None = None
    gender_id: str | None = Field(default=None, max_length=1)
    person_id: str | None = Field(default=None, max_length=10)


class ActSectionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    case_master_id: int
    act_id: str
    section_id: str
    act_order_id: int
    section_order_id: int


class ActSectionCreate(BaseModel):
    act_id: str = Field(..., min_length=1, max_length=20)
    section_id: str = Field(..., min_length=1, max_length=20)
    act_order_id: int = 1
    section_order_id: int = 1


class CaseMasterBase(BaseModel):
    crime_no: str = Field(..., min_length=18, max_length=18)
    case_no: str = Field(..., min_length=1, max_length=20)
    crime_registered_date: date | None = None
    police_person_id: int | None = None
    police_station_id: int
    case_category_id: int
    gravity_offence_id: int | None = None
    crime_major_head_id: int | None = None
    crime_minor_head_id: int | None = None
    case_status_id: int
    court_id: int | None = None
    incident_from_date: datetime | None = None
    incident_to_date: datetime | None = None
    info_received_ps_date: datetime | None = None
    latitude: Decimal | None = None
    longitude: Decimal | None = None
    brief_facts: str | None = None


class CaseMasterCreate(CaseMasterBase):
    victims: list[VictimCreate] = Field(default_factory=list)
    accused: list[AccusedCreate] = Field(default_factory=list)
    complainants: list[ComplainantDetailsCreate] = Field(default_factory=list)
    act_sections: list[ActSectionCreate] = Field(default_factory=list)


class CaseMasterRead(CaseMasterBase):
    model_config = ConfigDict(from_attributes=True)

    case_master_id: int


class CaseMasterDetail(CaseMasterRead):
    victims: list[VictimRead] = Field(default_factory=list)
    accused: list[AccusedRead] = Field(default_factory=list)
    complainants: list[ComplainantDetailsRead] = Field(default_factory=list)
    act_sections: list[ActSectionRead] = Field(default_factory=list)
    occurrence: InvOccuranceTimeRead | None = None
    arrests: list[ArrestSurrenderRead] = Field(default_factory=list)
    chargesheets: list[ChargesheetDetailsRead] = Field(default_factory=list)


class CaseMasterListResponse(BaseModel):
    items: list[CaseMasterRead]
    total: int
    limit: int
    offset: int
