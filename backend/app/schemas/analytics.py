"""Analytics / geo response schemas (B2)."""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, Field


class StatusCount(BaseModel):
    case_status_id: int
    name: str
    count: int


class CrimeHeadCount(BaseModel):
    crime_major_head_id: int | None
    name: str
    count: int


class AnalyticsOverview(BaseModel):
    total_cases: int
    cases_with_coordinates: int
    by_status: list[StatusCount]
    by_crime_head: list[CrimeHeadCount]
    districts_covered: int
    stations_covered: int


class DistrictGeoSummary(BaseModel):
    district_id: int
    district_name: str
    case_count: int
    avg_latitude: Decimal | None = None
    avg_longitude: Decimal | None = None


class IncidentPoint(BaseModel):
    case_master_id: int
    crime_no: str
    case_no: str
    police_station_id: int
    district_id: int | None = None
    case_status_id: int
    crime_major_head_id: int | None = None
    latitude: Decimal
    longitude: Decimal
    incident_from_date: datetime | None = None
    crime_registered_date: date | None = None


class IncidentPointsResponse(BaseModel):
    items: list[IncidentPoint]
    total: int


class HotspotBin(BaseModel):
    """Spatiotemporal cluster cell."""

    lat_bin: float
    lon_bin: float
    hour_of_day: int | None = Field(
        default=None, description="0-23 when grain includes hour; null if day-only"
    )
    case_count: int
    sample_case_ids: list[int] = Field(default_factory=list)


class HotspotsResponse(BaseModel):
    grain: str
    cell_size_degrees: float
    bins: list[HotspotBin]


class TrendAlert(BaseModel):
    district_id: int
    district_name: str
    crime_major_head_id: int | None
    crime_head_name: str
    recent_count: int
    baseline_avg: float
    spike_ratio: float
    is_alert: bool
    avg_latitude: Decimal | None = None
    avg_longitude: Decimal | None = None


class TrendAlertsResponse(BaseModel):
    recent_days: int
    baseline_days: int
    threshold: float
    alerts: list[TrendAlert]
