"""Network / link-analysis HTTP routes (B3)."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Query

from app.repositories.case.factory import CaseStoreDep
from app.schemas.network import NetworkGraphResponse, OffenderProfile
from app.services.network import NetworkService

router = APIRouter(prefix="/network", tags=["network"])


def _service(store: CaseStoreDep) -> NetworkService:
    return NetworkService(store)


@router.get("/graph", response_model=NetworkGraphResponse)
def network_graph(
    service: Annotated[NetworkService, Depends(_service)],
    case_id: int | None = None,
    accused_id: int | None = None,
    depth: Annotated[int, Query(ge=1, le=3)] = 1,
) -> NetworkGraphResponse:
    """Ego network: cases ↔ accused ↔ victims ↔ stations."""
    return service.graph(case_id=case_id, accused_id=accused_id, depth=depth)


@router.get("/offenders/{accused_id}", response_model=OffenderProfile)
def offender_profile(
    accused_id: int,
    service: Annotated[NetworkService, Depends(_service)],
) -> OffenderProfile:
    """Repeat-offender profile (same person_id / name across cases)."""
    return service.offender_profile(accused_id)
