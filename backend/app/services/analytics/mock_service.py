"""Analytics over Catalyst Data Store rows (live or JSON mock)."""

from __future__ import annotations

from collections import defaultdict
from datetime import date, datetime, timedelta
from decimal import Decimal
from typing import Any

from app.integrations.catalyst.datastore import CatalystDataStoreClient
from app.schemas.analytics import (
    AnalyticsOverview,
    CrimeHeadCount,
    DistrictGeoSummary,
    HotspotBin,
    HotspotsResponse,
    IncidentPoint,
    IncidentPointsResponse,
    StatusCount,
    TrendAlert,
    TrendAlertsResponse,
)
from app.services import lookups_catalog as lookups
from app.utils.ttl_cache import cache_get, cache_set

_CASE = "case_master"


def _opt_int(value: Any) -> int | None:
    if value is None or value == "":
        return None
    return int(value)


def _opt_decimal(value: Any) -> Decimal | None:
    if value is None or value == "":
        return None
    return Decimal(str(value))


def _parse_date(value: Any) -> date | None:
    if value is None or value == "":
        return None
    if isinstance(value, date) and not isinstance(value, datetime):
        return value
    return date.fromisoformat(str(value)[:10])


def _parse_dt(value: Any) -> datetime | None:
    if value is None or value == "":
        return None
    if isinstance(value, datetime):
        return value
    text = str(value).replace("Z", "+00:00")
    try:
        return datetime.fromisoformat(text)
    except ValueError:
        return None


class MockAnalyticsService:
    """B2 analytics from Catalyst Data Store (+ lookups for display names)."""

    def __init__(self, client: CatalystDataStoreClient | None = None) -> None:
        self._ds = client or CatalystDataStoreClient()

    def _cases(self) -> list[dict[str, Any]]:
        return self._ds.get_paged_rows(_CASE, max_rows=5000)

    def overview(self) -> AnalyticsOverview:
        cache_key = "analytics:overview:mock"
        cached = cache_get(cache_key)
        if isinstance(cached, AnalyticsOverview):
            return cached

        rows = self._cases()
        total = len(rows)
        with_coords = sum(
            1
            for r in rows
            if r.get("latitude") not in (None, "") and r.get("longitude")
        )
        by_status: dict[int, int] = defaultdict(int)
        by_head: dict[int | None, int] = defaultdict(int)
        districts: set[int] = set()
        stations: set[int] = set()
        for r in rows:
            sid = int(r.get("case_status_id") or 0)
            by_status[sid] += 1
            hid = _opt_int(r.get("crime_major_head_id"))
            by_head[hid] += 1
            st = int(r.get("police_station_id") or 0)
            stations.add(st)
            did = lookups.station_district_id(st)
            if did is not None:
                districts.add(did)

        result = AnalyticsOverview(
            total_cases=total,
            cases_with_coordinates=with_coords,
            by_status=[
                StatusCount(
                    case_status_id=sid,
                    name=lookups.status_name(sid),
                    count=count,
                )
                for sid, count in sorted(by_status.items(), key=lambda x: -x[1])
            ],
            by_crime_head=[
                CrimeHeadCount(
                    crime_major_head_id=hid,
                    name=lookups.crime_head_name(hid),
                    count=count,
                )
                for hid, count in sorted(by_head.items(), key=lambda x: -x[1])
            ],
            districts_covered=len(districts),
            stations_covered=len(stations),
        )
        cache_set(cache_key, result, ttl_seconds=30)
        return result

    def geo_districts(self) -> list[DistrictGeoSummary]:
        buckets: dict[int, list[tuple[float, float]]] = defaultdict(list)
        for r in self._cases():
            st = int(r.get("police_station_id") or 0)
            did = lookups.station_district_id(st)
            lat = _opt_decimal(r.get("latitude"))
            lon = _opt_decimal(r.get("longitude"))
            if did is None or lat is None or lon is None:
                continue
            buckets[did].append((float(lat), float(lon)))

        out: list[DistrictGeoSummary] = []
        for did, pts in buckets.items():
            avg_lat = sum(p[0] for p in pts) / len(pts)
            avg_lon = sum(p[1] for p in pts) / len(pts)
            out.append(
                DistrictGeoSummary(
                    district_id=did,
                    district_name=lookups.district_name(did),
                    case_count=len(pts),
                    avg_latitude=Decimal(str(round(avg_lat, 7))),
                    avg_longitude=Decimal(str(round(avg_lon, 7))),
                )
            )
        out.sort(key=lambda d: d.case_count, reverse=True)
        return out

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
    ) -> IncidentPointsResponse:
        items: list[IncidentPoint] = []
        for r in self._cases():
            lat = _opt_decimal(r.get("latitude"))
            lon = _opt_decimal(r.get("longitude"))
            if lat is None or lon is None:
                continue
            st = int(r.get("police_station_id") or 0)
            did = lookups.station_district_id(st)
            if district_id is not None and did != district_id:
                continue
            if police_station_id is not None and st != police_station_id:
                continue
            status = int(r.get("case_status_id") or 0)
            if case_status_id is not None and status != case_status_id:
                continue
            head = _opt_int(r.get("crime_major_head_id"))
            if crime_major_head_id is not None and head != crime_major_head_id:
                continue
            reg = _parse_date(r.get("crime_registered_date"))
            if registered_from is not None and (reg is None or reg < registered_from):
                continue
            if registered_to is not None and (reg is None or reg > registered_to):
                continue
            case_id = int(r.get("ROWID") or r.get("case_master_id") or 0)
            items.append(
                IncidentPoint(
                    case_master_id=case_id,
                    crime_no=str(r.get("crime_no") or ""),
                    case_no=str(r.get("case_no") or ""),
                    police_station_id=st,
                    district_id=did,
                    case_status_id=status,
                    crime_major_head_id=head,
                    latitude=lat,
                    longitude=lon,
                    incident_from_date=_parse_dt(r.get("incident_from_date")),
                    crime_registered_date=reg,
                )
            )
        items.sort(key=lambda i: i.case_master_id, reverse=True)
        trimmed = items[:limit]
        return IncidentPointsResponse(items=trimmed, total=len(trimmed))

    def hotspots(
        self,
        *,
        cell_size_degrees: float = 0.05,
        grain: str = "hour",
        registered_from: date | None = None,
        registered_to: date | None = None,
        district_id: int | None = None,
    ) -> HotspotsResponse:
        if grain not in {"hour", "day"}:
            grain = "hour"
        cell = max(0.01, min(cell_size_degrees, 1.0))
        buckets: dict[tuple[float, float, int | None], list[int]] = defaultdict(list)

        for r in self._cases():
            lat = _opt_decimal(r.get("latitude"))
            lon = _opt_decimal(r.get("longitude"))
            if lat is None or lon is None:
                continue
            st = int(r.get("police_station_id") or 0)
            did = lookups.station_district_id(st)
            if district_id is not None and did != district_id:
                continue
            reg = _parse_date(r.get("crime_registered_date"))
            if registered_from is not None and (reg is None or reg < registered_from):
                continue
            if registered_to is not None and (reg is None or reg > registered_to):
                continue
            lat_f, lon_f = float(lat), float(lon)
            lat_bin = round(lat_f / cell) * cell
            lon_bin = round(lon_f / cell) * cell
            hour: int | None = None
            incident_at = _parse_dt(r.get("incident_from_date"))
            if grain == "hour" and incident_at is not None:
                hour = int(incident_at.hour)
            case_id = int(r.get("ROWID") or r.get("case_master_id") or 0)
            buckets[(lat_bin, lon_bin, hour)].append(case_id)

        bins = [
            HotspotBin(
                lat_bin=k[0],
                lon_bin=k[1],
                hour_of_day=k[2],
                case_count=len(ids),
                sample_case_ids=ids[:5],
            )
            for k, ids in buckets.items()
        ]
        bins.sort(key=lambda b: b.case_count, reverse=True)
        return HotspotsResponse(grain=grain, cell_size_degrees=cell, bins=bins[:200])

    def trend_alerts(
        self,
        *,
        recent_days: int = 7,
        baseline_days: int = 28,
        threshold: float = 1.5,
    ) -> TrendAlertsResponse:
        today = date.today()
        recent_start = today - timedelta(days=recent_days)
        baseline_start = recent_start - timedelta(days=baseline_days)

        recent: dict[tuple[int, int | None], int] = defaultdict(int)
        baseline: dict[tuple[int, int | None], int] = defaultdict(int)

        for r in self._cases():
            reg = _parse_date(r.get("crime_registered_date"))
            if reg is None:
                continue
            st = int(r.get("police_station_id") or 0)
            did = lookups.station_district_id(st)
            if did is None:
                continue
            head = _opt_int(r.get("crime_major_head_id"))
            key = (did, head)
            if reg >= recent_start:
                recent[key] += 1
            elif baseline_start <= reg < recent_start:
                baseline[key] += 1

        alerts: list[TrendAlert] = []
        keys = set(recent) | set(baseline)
        for did, head in keys:
            recent_count = recent.get((did, head), 0)
            baseline_count = baseline.get((did, head), 0)
            baseline_avg = baseline_count / max(baseline_days / recent_days, 1)
            if baseline_avg <= 0:
                spike = float(recent_count) if recent_count else 0.0
            else:
                spike = recent_count / baseline_avg
            alerts.append(
                TrendAlert(
                    district_id=did,
                    district_name=lookups.district_name(did),
                    crime_major_head_id=head,
                    crime_head_name=lookups.crime_head_name(head),
                    recent_count=recent_count,
                    baseline_avg=round(baseline_avg, 2),
                    spike_ratio=round(spike, 2),
                    is_alert=spike >= threshold and recent_count > 0,
                )
            )
        alerts.sort(key=lambda a: a.spike_ratio, reverse=True)
        return TrendAlertsResponse(
            recent_days=recent_days,
            baseline_days=baseline_days,
            threshold=threshold,
            alerts=alerts,
        )
