"""GET /search — accused / victim / complainant / case by name."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Query

from app.schemas.search import SearchResponse
from app.services.search.service import SearchService

router = APIRouter(prefix="/search", tags=["search"])


@router.get("", response_model=SearchResponse)
def search_entities(
    q: Annotated[
        str,
        Query(min_length=2, max_length=120, description="Name / crime no / person id"),
    ],
    types: Annotated[
        str,
        Query(description="Comma list: accused,victim,complainant,case"),
    ] = "accused,victim,complainant,case",
    limit: Annotated[int, Query(ge=1, le=100)] = 40,
) -> SearchResponse:
    """Search FIR parties and cases by name / person id / crime number."""
    type_list = [t.strip() for t in types.split(",") if t.strip()]
    return SearchService().search(q, types=type_list, limit=limit)
