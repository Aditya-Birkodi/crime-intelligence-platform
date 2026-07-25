"""Analytics & geo HTTP routes (B2) — Postgres or Catalyst mock."""

from __future__ import annotations

from collections.abc import Generator
from datetime import date
from typing import Annotated, Literal, Protocol

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.database.session import get_session_factory
from app.schemas.analytics import (
    AnalyticsOverview,
    DistrictGeoSummary,
    HotspotsResponse,
    IncidentPointsResponse,
    TrendAlertsResponse,
)
from app.schemas.analytics_socio import SocioEconomicOverlayResponse
from app.services.analytics import AnalyticsService
from app.services.analytics.mock_service import MockAnalyticsService

router = APIRouter(prefix="/analytics", tags=["analytics"])


class AnalyticsPort(Protocol):
    def overview(self) -> AnalyticsOverview: ...

    def geo_districts(self) -> list[DistrictGeoSummary]: ...

    def geo_incidents(
        self,
        *,
        district_id: int | None = None,
        police_station_id: int | None = None,
        case_status_id: int | None = None,
        crime_major_head_id: int | None = None,
        registered_from: date | None = None,
        registered_to: date | None = None,
        limit: int = 500,
    ) -> IncidentPointsResponse: ...

    def hotspots(
        self,
        *,
        cell_size_degrees: float = 0.05,
        grain: str = "hour",
        registered_from: date | None = None,
        registered_to: date | None = None,
        district_id: int | None = None,
    ) -> HotspotsResponse: ...

    def trend_alerts(
        self,
        *,
        recent_days: int = 7,
        baseline_days: int = 28,
        threshold: float = 1.5,
    ) -> TrendAlertsResponse: ...

    def socio_economic_overlay(self) -> SocioEconomicOverlayResponse: ...


def get_analytics_service() -> Generator[AnalyticsPort, None, None]:
    """Catalyst mock skips Postgres entirely (required for AppSail)."""
    settings = get_settings()
    if settings.persistence_backend == "catalyst":
        yield MockAnalyticsService()
        return

    db: Session = get_session_factory()()
    try:
        yield AnalyticsService(db)
    finally:
        db.close()


@router.get("/overview", response_model=AnalyticsOverview)
def analytics_overview(
    service: Annotated[AnalyticsPort, Depends(get_analytics_service)],
) -> AnalyticsOverview:
    """KPI tiles: totals, status breakdown, crime-head breakdown."""
    return service.overview()


@router.get("/geo/districts", response_model=list[DistrictGeoSummary])
def geo_districts(
    service: Annotated[AnalyticsPort, Depends(get_analytics_service)],
) -> list[DistrictGeoSummary]:
    """District-level case counts for choropleth / drill-down."""
    return service.geo_districts()


@router.get("/geo/incidents", response_model=IncidentPointsResponse)
def geo_incidents(
    service: Annotated[AnalyticsPort, Depends(get_analytics_service)],
    district_id: int | None = None,
    police_station_id: int | None = None,
    case_status_id: int | None = None,
    crime_major_head_id: int | None = None,
    registered_from: date | None = None,
    registered_to: date | None = None,
    limit: Annotated[int, Query(ge=1, le=2000)] = 500,
) -> IncidentPointsResponse:
    """Lat/long incident pins for the map."""
    return service.geo_incidents(
        district_id=district_id,
        police_station_id=police_station_id,
        case_status_id=case_status_id,
        crime_major_head_id=crime_major_head_id,
        registered_from=registered_from,
        registered_to=registered_to,
        limit=limit,
    )


@router.get("/hotspots", response_model=HotspotsResponse)
def hotspots(
    service: Annotated[AnalyticsPort, Depends(get_analytics_service)],
    cell_size_degrees: Annotated[float, Query(ge=0.01, le=1.0)] = 0.05,
    grain: Literal["hour", "day"] = "hour",
    registered_from: date | None = None,
    registered_to: date | None = None,
    district_id: int | None = None,
) -> HotspotsResponse:
    """Spatiotemporal hotspot bins (location × optional hour-of-day)."""
    return service.hotspots(
        cell_size_degrees=cell_size_degrees,
        grain=grain,
        registered_from=registered_from,
        registered_to=registered_to,
        district_id=district_id,
    )


@router.get("/alerts/trends", response_model=TrendAlertsResponse)
def trend_alerts(
    service: Annotated[AnalyticsPort, Depends(get_analytics_service)],
    recent_days: Annotated[int, Query(ge=1, le=90)] = 7,
    baseline_days: Annotated[int, Query(ge=7, le=365)] = 28,
    threshold: Annotated[float, Query(ge=1.0, le=10.0)] = 1.5,
) -> TrendAlertsResponse:
    """Emerging trend alerts: recent volume vs baseline by district + crime head."""
    return service.trend_alerts(
        recent_days=recent_days,
        baseline_days=baseline_days,
        threshold=threshold,
    )


@router.get("/socio-economic", response_model=SocioEconomicOverlayResponse)
def socio_economic_overlay(
    service: Annotated[AnalyticsPort, Depends(get_analytics_service)],
) -> SocioEconomicOverlayResponse:
    """District crime joined to socio-economic indicators (urbanization, density, etc.)."""
    return service.socio_economic_overlay()
