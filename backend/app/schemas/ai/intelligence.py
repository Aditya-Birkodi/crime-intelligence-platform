"""MO cluster + intelligence brief schemas."""

from __future__ import annotations

from pydantic import BaseModel, Field


class MoClusterMember(BaseModel):
    case_master_id: int
    crime_no: str
    brief_facts: str | None = None
    police_station_id: int | None = None
    district_id: int | None = None
    crime_major_head_id: int | None = None


class MoCluster(BaseModel):
    cluster_id: str
    label: str
    mo_signature: str
    size: int
    districts: list[str] = Field(default_factory=list)
    act_sections: list[str] = Field(default_factory=list)
    members: list[MoClusterMember] = Field(default_factory=list)
    similarity_note: str = ""


class MoClustersResponse(BaseModel):
    clusters: list[MoCluster]
    provider: str = "catalyst_mo_heuristic"
    total_cases_clustered: int = 0


class IntelligenceBriefSection(BaseModel):
    title: str
    body: str


class IntelligenceBriefResponse(BaseModel):
    title: str
    generated_at: str
    horizon_days: int = 7
    headline: str
    sections: list[IntelligenceBriefSection] = Field(default_factory=list)
    recommended_actions: list[str] = Field(default_factory=list)
    provider: str = "catalyst_intel_brief_v1"
