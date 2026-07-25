"""Lookups read APIs for FE dropdowns (B1 support).

Postgres when PERSISTENCE_BACKEND=postgres.
On Catalyst AppSail: Data Store master tables (district/unit/status) with
appsail_lookups.json fallback for the rest.
"""

from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel, ConfigDict
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.database.session import get_session_factory
from app.models.geography.district import District
from app.models.geography.unit import Unit
from app.models.legal.crime_head import CrimeHead
from app.models.lookups.case_category import CaseCategory
from app.models.lookups.case_status_master import CaseStatusMaster
from app.models.lookups.gravity_offence import GravityOffence
from app.services import lookups_catalog as catalog

router = APIRouter(prefix="/lookups", tags=["cases"])


class IdName(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str


def _use_catalog() -> bool:
    return get_settings().persistence_backend == "catalyst"


@router.get("/case-statuses", response_model=list[IdName])
def case_statuses() -> list[IdName]:
    if _use_catalog():
        return [IdName(**r) for r in catalog.id_name_list("case_statuses")]
    db: Session = get_session_factory()()
    try:
        rows = db.scalars(
            select(CaseStatusMaster).order_by(CaseStatusMaster.case_status_id)
        ).all()
        return [IdName(id=r.case_status_id, name=r.case_status_name) for r in rows]
    finally:
        db.close()


@router.get("/case-categories", response_model=list[IdName])
def case_categories() -> list[IdName]:
    if _use_catalog():
        return [IdName(**r) for r in catalog.id_name_list("case_categories")]
    db: Session = get_session_factory()()
    try:
        rows = db.scalars(
            select(CaseCategory).order_by(CaseCategory.case_category_id)
        ).all()
        return [IdName(id=r.case_category_id, name=r.lookup_value) for r in rows]
    finally:
        db.close()


@router.get("/gravity-offences", response_model=list[IdName])
def gravity_offences() -> list[IdName]:
    if _use_catalog():
        return [IdName(**r) for r in catalog.id_name_list("gravity_offences")]
    db: Session = get_session_factory()()
    try:
        rows = db.scalars(
            select(GravityOffence).order_by(GravityOffence.gravity_offence_id)
        ).all()
        return [IdName(id=r.gravity_offence_id, name=r.lookup_value) for r in rows]
    finally:
        db.close()


@router.get("/crime-heads", response_model=list[IdName])
def crime_heads() -> list[IdName]:
    if _use_catalog():
        return [IdName(**r) for r in catalog.id_name_list("crime_heads")]
    db: Session = get_session_factory()()
    try:
        rows = db.scalars(select(CrimeHead).order_by(CrimeHead.crime_head_id)).all()
        return [IdName(id=r.crime_head_id, name=r.crime_group_name) for r in rows]
    finally:
        db.close()


@router.get("/districts", response_model=list[IdName])
def districts() -> list[IdName]:
    if _use_catalog():
        return [IdName(**r) for r in catalog.id_name_list("districts")]
    db: Session = get_session_factory()()
    try:
        rows = db.scalars(select(District).order_by(District.district_id)).all()
        return [IdName(id=r.district_id, name=r.district_name) for r in rows]
    finally:
        db.close()


@router.get("/stations", response_model=list[IdName])
def stations(district_id: int | None = None) -> list[IdName]:
    if _use_catalog():
        rows = catalog.load_lookups().get("stations") or []
        out = []
        for r in rows:
            if (
                district_id is not None
                and int(r.get("district_id") or 0) != district_id
            ):
                continue
            out.append(IdName(id=int(r["id"]), name=str(r["name"])))
        return out
    db: Session = get_session_factory()()
    try:
        stmt = select(Unit).order_by(Unit.unit_id)
        if district_id is not None:
            stmt = stmt.where(Unit.district_id == district_id)
        rows = db.scalars(stmt).all()
        return [IdName(id=r.unit_id, name=r.unit_name) for r in rows]
    finally:
        db.close()


@router.get("/courts", response_model=list[IdName])
def courts() -> list[IdName]:
    if _use_catalog():
        return [IdName(**r) for r in catalog.id_name_list("courts")]
    from app.models.geography.court import Court

    db: Session = get_session_factory()()
    try:
        rows = db.scalars(select(Court).order_by(Court.court_id)).all()
        return [IdName(id=r.court_id, name=r.court_name) for r in rows]
    finally:
        db.close()


@router.get("/employees", response_model=list[IdName])
def employees() -> list[IdName]:
    if _use_catalog():
        return [IdName(**r) for r in catalog.id_name_list("employees")]
    from app.models.personnel.employee import Employee

    db: Session = get_session_factory()()
    try:
        rows = db.scalars(select(Employee).order_by(Employee.employee_id)).all()
        return [IdName(id=r.employee_id, name=r.first_name) for r in rows]
    finally:
        db.close()
