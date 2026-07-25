"""Analytics & geospatial aggregations for SCRB dashboards (B2)."""

from __future__ import annotations

from collections import defaultdict
from datetime import date, timedelta
from decimal import Decimal

from sqlalchemy import and_, func, select
from sqlalchemy.orm import Session

from app.models.case.case_master import CaseMaster
from app.models.geography.district import District
from app.models.geography.unit import Unit
from app.models.legal.crime_head import CrimeHead
from app.models.lookups.case_status_master import CaseStatusMaster
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
from app.schemas.analytics_socio import SocioEconomicOverlayResponse
from app.utils.ttl_cache import cache_get, cache_set


class AnalyticsService:
    def __init__(self, session: Session) -> None:
        self._session = session

    def overview(self) -> AnalyticsOverview:
        cache_key = "analytics:overview"
        cached = cache_get(cache_key)
        if isinstance(cached, AnalyticsOverview):
            return cached

        total = int(
            self._session.scalar(select(func.count()).select_from(CaseMaster)) or 0
        )
        with_coords = int(
            self._session.scalar(
                select(func.count())
                .select_from(CaseMaster)
                .where(
                    CaseMaster.latitude.is_not(None),
                    CaseMaster.longitude.is_not(None),
                )
            )
            or 0
        )

        status_rows = self._session.execute(
            select(
                CaseMaster.case_status_id,
                CaseStatusMaster.case_status_name,
                func.count(),
            )
            .join(
                CaseStatusMaster,
                CaseStatusMaster.case_status_id == CaseMaster.case_status_id,
            )
            .group_by(CaseMaster.case_status_id, CaseStatusMaster.case_status_name)
            .order_by(func.count().desc())
        ).all()

        head_rows = self._session.execute(
            select(
                CaseMaster.crime_major_head_id,
                CrimeHead.crime_group_name,
                func.count(),
            )
            .outerjoin(
                CrimeHead,
                CrimeHead.crime_head_id == CaseMaster.crime_major_head_id,
            )
            .group_by(CaseMaster.crime_major_head_id, CrimeHead.crime_group_name)
            .order_by(func.count().desc())
        ).all()

        districts = int(
            self._session.scalar(
                select(func.count(func.distinct(Unit.district_id)))
                .select_from(CaseMaster)
                .join(Unit, Unit.unit_id == CaseMaster.police_station_id)
            )
            or 0
        )
        stations = int(
            self._session.scalar(
                select(func.count(func.distinct(CaseMaster.police_station_id)))
            )
            or 0
        )

        result = AnalyticsOverview(
            total_cases=total,
            cases_with_coordinates=with_coords,
            by_status=[
                StatusCount(case_status_id=r[0], name=r[1], count=int(r[2]))
                for r in status_rows
            ],
            by_crime_head=[
                CrimeHeadCount(
                    crime_major_head_id=r[0],
                    name=r[1] or "Unclassified",
                    count=int(r[2]),
                )
                for r in head_rows
            ],
            districts_covered=districts,
            stations_covered=stations,
        )
        cache_set(cache_key, result, ttl_seconds=30)
        return result

    def geo_districts(self) -> list[DistrictGeoSummary]:
        rows = self._session.execute(
            select(
                District.district_id,
                District.district_name,
                func.count(CaseMaster.case_master_id),
                func.avg(CaseMaster.latitude),
                func.avg(CaseMaster.longitude),
            )
            .join(Unit, Unit.district_id == District.district_id)
            .join(CaseMaster, CaseMaster.police_station_id == Unit.unit_id)
            .group_by(District.district_id, District.district_name)
            .order_by(func.count(CaseMaster.case_master_id).desc())
        ).all()
        return [
            DistrictGeoSummary(
                district_id=int(r[0]),
                district_name=str(r[1]),
                case_count=int(r[2]),
                avg_latitude=Decimal(str(r[3])) if r[3] is not None else None,
                avg_longitude=Decimal(str(r[4])) if r[4] is not None else None,
            )
            for r in rows
        ]

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
        stmt = (
            select(
                CaseMaster.case_master_id,
                CaseMaster.crime_no,
                CaseMaster.case_no,
                CaseMaster.police_station_id,
                Unit.district_id,
                CaseMaster.case_status_id,
                CaseMaster.crime_major_head_id,
                CaseMaster.latitude,
                CaseMaster.longitude,
                CaseMaster.incident_from_date,
                CaseMaster.crime_registered_date,
            )
            .join(Unit, Unit.unit_id == CaseMaster.police_station_id)
            .where(
                CaseMaster.latitude.is_not(None),
                CaseMaster.longitude.is_not(None),
            )
        )
        if district_id is not None:
            stmt = stmt.where(Unit.district_id == district_id)
        if police_station_id is not None:
            stmt = stmt.where(CaseMaster.police_station_id == police_station_id)
        if case_status_id is not None:
            stmt = stmt.where(CaseMaster.case_status_id == case_status_id)
        if crime_major_head_id is not None:
            stmt = stmt.where(CaseMaster.crime_major_head_id == crime_major_head_id)
        if registered_from is not None:
            stmt = stmt.where(CaseMaster.crime_registered_date >= registered_from)
        if registered_to is not None:
            stmt = stmt.where(CaseMaster.crime_registered_date <= registered_to)

        rows = self._session.execute(
            stmt.order_by(CaseMaster.case_master_id.desc()).limit(limit)
        ).all()

        items = [
            IncidentPoint(
                case_master_id=int(r[0]),
                crime_no=str(r[1]),
                case_no=str(r[2]),
                police_station_id=int(r[3]),
                district_id=int(r[4]) if r[4] is not None else None,
                case_status_id=int(r[5]),
                crime_major_head_id=int(r[6]) if r[6] is not None else None,
                latitude=Decimal(str(r[7])),
                longitude=Decimal(str(r[8])),
                incident_from_date=r[9],
                crime_registered_date=r[10],
            )
            for r in rows
        ]
        return IncidentPointsResponse(items=items, total=len(items))

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

        stmt = (
            select(
                CaseMaster.case_master_id,
                CaseMaster.latitude,
                CaseMaster.longitude,
                CaseMaster.incident_from_date,
            )
            .join(Unit, Unit.unit_id == CaseMaster.police_station_id)
            .where(
                CaseMaster.latitude.is_not(None),
                CaseMaster.longitude.is_not(None),
            )
        )
        if registered_from is not None:
            stmt = stmt.where(CaseMaster.crime_registered_date >= registered_from)
        if registered_to is not None:
            stmt = stmt.where(CaseMaster.crime_registered_date <= registered_to)
        if district_id is not None:
            stmt = stmt.where(Unit.district_id == district_id)

        rows = self._session.execute(stmt).all()
        buckets: dict[tuple[float, float, int | None], list[int]] = defaultdict(list)

        for case_id, lat, lon, incident_at in rows:
            lat_f = float(lat)
            lon_f = float(lon)
            lat_bin = round(lat_f / cell) * cell
            lon_bin = round(lon_f / cell) * cell
            hour: int | None = None
            if grain == "hour" and incident_at is not None:
                hour = int(incident_at.hour)
            buckets[(lat_bin, lon_bin, hour)].append(int(case_id))

        bins = [
            HotspotBin(
                lat_bin=key[0],
                lon_bin=key[1],
                hour_of_day=key[2],
                case_count=len(ids),
                sample_case_ids=ids[:5],
            )
            for key, ids in buckets.items()
        ]
        bins.sort(key=lambda b: b.case_count, reverse=True)
        return HotspotsResponse(grain=grain, cell_size_degrees=cell, bins=bins)

    def trend_alerts(
        self,
        *,
        recent_days: int = 7,
        baseline_days: int = 28,
        threshold: float = 1.5,
    ) -> TrendAlertsResponse:
        today = date.today()
        recent_start = today - timedelta(days=recent_days)
        baseline_start = today - timedelta(days=baseline_days)

        def _counts(start: date, end: date) -> dict[tuple[int, int | None], int]:
            rows = self._session.execute(
                select(
                    Unit.district_id,
                    CaseMaster.crime_major_head_id,
                    func.count(),
                )
                .join(Unit, Unit.unit_id == CaseMaster.police_station_id)
                .where(
                    and_(
                        CaseMaster.crime_registered_date.is_not(None),
                        CaseMaster.crime_registered_date >= start,
                        CaseMaster.crime_registered_date <= end,
                    )
                )
                .group_by(Unit.district_id, CaseMaster.crime_major_head_id)
            ).all()
            return {
                (int(r[0]), None if r[1] is None else int(r[1])): int(r[2])
                for r in rows
            }

        recent = _counts(recent_start, today)
        baseline = _counts(baseline_start, recent_start - timedelta(days=1))

        if not recent and not baseline:
            all_rows = self._session.execute(
                select(
                    Unit.district_id,
                    District.district_name,
                    CaseMaster.crime_major_head_id,
                    CrimeHead.crime_group_name,
                    func.count(),
                )
                .join(Unit, Unit.unit_id == CaseMaster.police_station_id)
                .join(District, District.district_id == Unit.district_id)
                .outerjoin(
                    CrimeHead,
                    CrimeHead.crime_head_id == CaseMaster.crime_major_head_id,
                )
                .group_by(
                    Unit.district_id,
                    District.district_name,
                    CaseMaster.crime_major_head_id,
                    CrimeHead.crime_group_name,
                )
            ).all()
            if not all_rows:
                return TrendAlertsResponse(
                    recent_days=recent_days,
                    baseline_days=baseline_days,
                    threshold=threshold,
                    alerts=[],
                )
            values = [int(r[4]) for r in all_rows]
            mean = sum(values) / len(values)
            alerts = [
                TrendAlert(
                    district_id=int(r[0]),
                    district_name=str(r[1]),
                    crime_major_head_id=int(r[2]) if r[2] is not None else None,
                    crime_head_name=str(r[3] or "Unclassified"),
                    recent_count=int(r[4]),
                    baseline_avg=round(mean, 2),
                    spike_ratio=round(int(r[4]) / mean, 2) if mean else 0.0,
                    is_alert=(int(r[4]) / mean) >= threshold if mean else False,
                )
                for r in all_rows
            ]
            alerts.sort(key=lambda a: a.spike_ratio, reverse=True)
            return TrendAlertsResponse(
                recent_days=recent_days,
                baseline_days=baseline_days,
                threshold=threshold,
                alerts=alerts,
            )

        district_names = {
            int(r[0]): str(r[1])
            for r in self._session.execute(
                select(District.district_id, District.district_name)
            ).all()
        }
        head_names = {
            int(r[0]): str(r[1])
            for r in self._session.execute(
                select(CrimeHead.crime_head_id, CrimeHead.crime_group_name)
            ).all()
        }

        keys = set(recent) | set(baseline)
        baseline_window = max(baseline_days - recent_days, 1)
        alerts = []
        for district_id, head_id in keys:
            recent_count = recent.get((district_id, head_id), 0)
            baseline_total = baseline.get((district_id, head_id), 0)
            baseline_avg = baseline_total / baseline_window
            if baseline_avg > 0:
                ratio = recent_count / baseline_avg
            else:
                ratio = float(recent_count) if recent_count else 0.0
            alerts.append(
                TrendAlert(
                    district_id=district_id,
                    district_name=district_names.get(district_id, str(district_id)),
                    crime_major_head_id=head_id,
                    crime_head_name=(
                        head_names.get(head_id, "Unclassified")
                        if head_id is not None
                        else "Unclassified"
                    ),
                    recent_count=recent_count,
                    baseline_avg=round(baseline_avg, 2),
                    spike_ratio=round(ratio, 2),
                    is_alert=ratio >= threshold and recent_count > 0,
                )
            )
        alerts.sort(key=lambda a: a.spike_ratio, reverse=True)
        return TrendAlertsResponse(
            recent_days=recent_days,
            baseline_days=baseline_days,
            threshold=threshold,
            alerts=alerts,
        )

    def socio_economic_overlay(self) -> SocioEconomicOverlayResponse:
        """Postgres path: reuse Catalyst mock join (file-based indicators)."""
        from app.services.analytics.mock_service import MockAnalyticsService

        return MockAnalyticsService().socio_economic_overlay()
