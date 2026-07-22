"""Case / FIR HTTP routes (B1) — Postgres or Catalyst Data Store via CaseStore."""

from __future__ import annotations

from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends, Query, status

from app.repositories.case.case_store import CaseStore
from app.repositories.case.factory import get_case_store
from app.schemas.case.case_master import (
    AccusedCreate,
    ActSectionCreate,
    CaseMasterCreate,
    CaseMasterDetail,
    CaseMasterListResponse,
    VictimCreate,
)
from app.services.case.case_master import CaseMasterService

router = APIRouter(prefix="/cases", tags=["cases"])


def _service(
    store: Annotated[CaseStore, Depends(get_case_store)],
) -> CaseMasterService:
    return CaseMasterService(store)


@router.get("", response_model=CaseMasterListResponse)
def list_cases(
    service: Annotated[CaseMasterService, Depends(_service)],
    police_station_id: int | None = None,
    case_status_id: int | None = None,
    crime_major_head_id: int | None = None,
    registered_from: date | None = None,
    registered_to: date | None = None,
    limit: Annotated[int, Query(ge=1, le=200)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> CaseMasterListResponse:
    """List FIRs with optional station/status/crime-head/date filters."""
    return service.list_cases(
        police_station_id=police_station_id,
        case_status_id=case_status_id,
        crime_major_head_id=crime_major_head_id,
        registered_from=registered_from,
        registered_to=registered_to,
        limit=limit,
        offset=offset,
    )


@router.get("/{case_master_id}", response_model=CaseMasterDetail)
def get_case(
    case_master_id: int,
    service: Annotated[CaseMasterService, Depends(_service)],
) -> CaseMasterDetail:
    """Get one FIR with victims, accused, and act-sections."""
    return service.get_case(case_master_id)


@router.post("", response_model=CaseMasterDetail, status_code=status.HTTP_201_CREATED)
def create_case(
    payload: CaseMasterCreate,
    service: Annotated[CaseMasterService, Depends(_service)],
) -> CaseMasterDetail:
    """Create a FIR (CaseMaster) with optional nested parties/sections."""
    return service.create_case(payload)


@router.post(
    "/{case_master_id}/victims",
    response_model=CaseMasterDetail,
    status_code=status.HTTP_201_CREATED,
)
def add_victim(
    case_master_id: int,
    payload: VictimCreate,
    service: Annotated[CaseMasterService, Depends(_service)],
) -> CaseMasterDetail:
    return service.add_victim(case_master_id, payload)


@router.post(
    "/{case_master_id}/accused",
    response_model=CaseMasterDetail,
    status_code=status.HTTP_201_CREATED,
)
def add_accused(
    case_master_id: int,
    payload: AccusedCreate,
    service: Annotated[CaseMasterService, Depends(_service)],
) -> CaseMasterDetail:
    return service.add_accused(case_master_id, payload)


@router.post(
    "/{case_master_id}/act-sections",
    response_model=CaseMasterDetail,
    status_code=status.HTTP_201_CREATED,
)
def add_act_section(
    case_master_id: int,
    payload: ActSectionCreate,
    service: Annotated[CaseMasterService, Depends(_service)],
) -> CaseMasterDetail:
    return service.add_act_section(case_master_id, payload)
