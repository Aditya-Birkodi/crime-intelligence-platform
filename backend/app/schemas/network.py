"""Network / link-analysis response schemas (B3)."""

from __future__ import annotations

from datetime import date
from typing import Any, Literal

from pydantic import BaseModel, Field

NodeType = Literal["case", "accused", "victim", "station"]
EdgeRelation = Literal[
    "accused_of",
    "victim_of",
    "filed_at",
    "same_person",
    "co_accused",
]


class GraphNode(BaseModel):
    id: str
    type: NodeType
    label: str
    meta: dict[str, Any] = Field(default_factory=dict)


class GraphEdge(BaseModel):
    id: str
    source: str
    target: str
    relation: EdgeRelation
    score: float = Field(ge=0.0, le=1.0, default=1.0)


class NetworkGraphResponse(BaseModel):
    seed: str
    nodes: list[GraphNode]
    edges: list[GraphEdge]


class OffenderCaseSummary(BaseModel):
    case_master_id: int
    crime_no: str
    case_no: str
    brief_facts: str | None = None
    crime_registered_date: date | None = None
    police_station_id: int
    crime_major_head_id: int | None = None
    accused_master_id: int


class OffenderProfile(BaseModel):
    accused_master_id: int
    accused_name: str
    person_id: str | None = None
    age_year: int | None = None
    gender_id: str | None = None
    case_count: int
    cases: list[OffenderCaseSummary]
    modus_operandi: list[str] = Field(default_factory=list)
    linked_accused_ids: list[int] = Field(default_factory=list)
