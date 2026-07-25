"""Person / case name search schemas."""

from __future__ import annotations

from pydantic import BaseModel, Field


class SearchHit(BaseModel):
    entity_type: str = Field(description="accused | victim | complainant | case")
    entity_id: int
    name: str
    case_master_id: int | None = None
    crime_no: str | None = None
    person_id: str | None = None
    match_field: str = ""
    score: float = 1.0


class SearchResponse(BaseModel):
    query: str
    total: int
    items: list[SearchHit]
    provider: str = "catalyst_name_search"
