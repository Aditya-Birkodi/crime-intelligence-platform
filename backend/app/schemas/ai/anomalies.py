"""Pydantic contracts for B4 anomaly detection."""

from __future__ import annotations

from pydantic import BaseModel, Field


class AnomalyItem(BaseModel):
    anomaly_id: str
    kind: str
    severity: str
    title: str
    detail: str
    district_id: int | None = None
    police_station_id: int | None = None
    case_master_ids: list[int] = Field(default_factory=list)
    score: float = 0.0


class AnomaliesResponse(BaseModel):
    items: list[AnomalyItem]
    provider: str = "catalyst_heuristic"
    total: int = 0
