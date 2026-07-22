"""Lookups read APIs for FE dropdowns (B1 support)."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends
from pydantic import BaseModel, ConfigDict
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models.geography.district import District
from app.models.geography.unit import Unit
from app.models.legal.crime_head import CrimeHead
from app.models.lookups.case_category import CaseCategory
from app.models.lookups.case_status_master import CaseStatusMaster
from app.models.lookups.gravity_offence import GravityOffence

router = APIRouter(prefix="/lookups", tags=["cases"])


class IdName(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str


@router.get("/case-statuses", response_model=list[IdName])
def case_statuses(db: Annotated[Session, Depends(get_db)]) -> list[IdName]:
    rows = db.scalars(
        select(CaseStatusMaster).order_by(CaseStatusMaster.case_status_id)
    ).all()
    return [IdName(id=r.case_status_id, name=r.case_status_name) for r in rows]


@router.get("/case-categories", response_model=list[IdName])
def case_categories(db: Annotated[Session, Depends(get_db)]) -> list[IdName]:
    rows = db.scalars(
        select(CaseCategory).order_by(CaseCategory.case_category_id)
    ).all()
    return [IdName(id=r.case_category_id, name=r.lookup_value) for r in rows]


@router.get("/gravity-offences", response_model=list[IdName])
def gravity_offences(db: Annotated[Session, Depends(get_db)]) -> list[IdName]:
    rows = db.scalars(
        select(GravityOffence).order_by(GravityOffence.gravity_offence_id)
    ).all()
    return [IdName(id=r.gravity_offence_id, name=r.lookup_value) for r in rows]


@router.get("/crime-heads", response_model=list[IdName])
def crime_heads(db: Annotated[Session, Depends(get_db)]) -> list[IdName]:
    rows = db.scalars(select(CrimeHead).order_by(CrimeHead.crime_head_id)).all()
    return [IdName(id=r.crime_head_id, name=r.crime_group_name) for r in rows]


@router.get("/districts", response_model=list[IdName])
def districts(db: Annotated[Session, Depends(get_db)]) -> list[IdName]:
    rows = db.scalars(select(District).order_by(District.district_id)).all()
    return [IdName(id=r.district_id, name=r.district_name) for r in rows]


@router.get("/stations", response_model=list[IdName])
def stations(
    db: Annotated[Session, Depends(get_db)],
    district_id: int | None = None,
) -> list[IdName]:
    stmt = select(Unit).order_by(Unit.unit_id)
    if district_id is not None:
        stmt = stmt.where(Unit.district_id == district_id)
    rows = db.scalars(stmt).all()
    return [IdName(id=r.unit_id, name=r.unit_name) for r in rows]
