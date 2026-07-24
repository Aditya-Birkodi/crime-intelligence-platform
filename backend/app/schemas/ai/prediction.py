"""Pydantic contracts for B4 risk prediction."""

from __future__ import annotations

from pydantic import BaseModel, Field


class RiskPredictRequest(BaseModel):
    district_id: int | None = None
    police_station_id: int | None = None
    horizon_days: int = Field(default=7, ge=1, le=90)


class RiskScoreItem(BaseModel):
    scope: str
    scope_id: int
    scope_name: str | None = None
    risk_score: float
    case_count: int
    high_severity_share: float
    top_crime_heads: list[str] = Field(default_factory=list)


class RiskPredictResponse(BaseModel):
    horizon_days: int
    items: list[RiskScoreItem]
    provider: str = "catalyst_heuristic"
    model: str | None = "local_risk_v1"
