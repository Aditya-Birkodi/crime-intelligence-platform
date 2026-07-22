"""Analytics API integration tests (SQLite)."""

from __future__ import annotations

import sys
from collections.abc import Generator
from datetime import UTC, date, datetime
from decimal import Decimal
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

BACKEND = Path(__file__).resolve().parents[2] / "backend"
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

import app.models  # noqa: F401
from app.database.base import Base
from app.database.session import get_db
from app.models.case.case_master import CaseMaster
from app.models.geography.district import District
from app.models.geography.state import State
from app.models.geography.unit import Unit
from app.models.geography.unit_type import UnitType
from app.models.legal.crime_head import CrimeHead
from app.models.lookups.case_category import CaseCategory
from app.models.lookups.case_status_master import CaseStatusMaster
from app.utils.ttl_cache import cache_clear
from main import app


@pytest.fixture()
def client() -> Generator[TestClient, None, None]:
    cache_clear()
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    TestingSession = sessionmaker(bind=engine, autoflush=False, autocommit=False)

    def override_get_db() -> Generator[Session, None, None]:
        db = TestingSession()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    db = TestingSession()
    state = State(state_name="Karnataka")
    db.add(state)
    db.flush()
    db.add(
        District(
            district_id=443, district_name="Bengaluru City", state_id=state.state_id
        )
    )
    db.add(District(district_id=444, district_name="Mysuru", state_id=state.state_id))
    ut = UnitType(unit_type_name="Police Station")
    db.add(ut)
    db.flush()
    db.add(
        Unit(
            unit_id=6,
            unit_name="MG Road PS",
            type_id=ut.unit_type_id,
            state_id=state.state_id,
            district_id=443,
        )
    )
    db.add(
        Unit(
            unit_id=11,
            unit_name="Mysuru North PS",
            type_id=ut.unit_type_id,
            state_id=state.state_id,
            district_id=444,
        )
    )
    db.add(CaseCategory(lookup_value="FIR", category_code="1"))
    db.add(CaseStatusMaster(case_status_name="Under Investigation"))
    head = CrimeHead(crime_group_name="Crimes Against Property")
    db.add(head)
    db.flush()

    db.add_all(
        [
            CaseMaster(
                crime_no="104430006202600001",
                case_no="202600001",
                crime_registered_date=date(2026, 1, 15),
                police_station_id=6,
                case_category_id=1,
                case_status_id=1,
                crime_major_head_id=head.crime_head_id,
                latitude=Decimal("12.9716000"),
                longitude=Decimal("77.5946000"),
                incident_from_date=datetime(2026, 1, 15, 21, 0, tzinfo=UTC),
                brief_facts="Theft A",
            ),
            CaseMaster(
                crime_no="104430006202600002",
                case_no="202600002",
                crime_registered_date=date(2026, 1, 16),
                police_station_id=6,
                case_category_id=1,
                case_status_id=1,
                crime_major_head_id=head.crime_head_id,
                latitude=Decimal("12.9720000"),
                longitude=Decimal("77.5950000"),
                incident_from_date=datetime(2026, 1, 16, 22, 0, tzinfo=UTC),
                brief_facts="Theft B",
            ),
            CaseMaster(
                crime_no="104440011202600001",
                case_no="202600003",
                crime_registered_date=date(2026, 1, 17),
                police_station_id=11,
                case_category_id=1,
                case_status_id=1,
                crime_major_head_id=head.crime_head_id,
                latitude=Decimal("12.2958000"),
                longitude=Decimal("76.6394000"),
                incident_from_date=datetime(2026, 1, 17, 10, 0, tzinfo=UTC),
                brief_facts="Mysuru case",
            ),
        ]
    )
    db.commit()
    db.close()

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()
    cache_clear()


def test_overview(client: TestClient) -> None:
    res = client.get("/api/v1/analytics/overview")
    assert res.status_code == 200
    body = res.json()
    assert body["total_cases"] == 3
    assert body["cases_with_coordinates"] == 3
    assert body["districts_covered"] == 2
    assert body["by_status"][0]["count"] == 3


def test_geo_districts(client: TestClient) -> None:
    res = client.get("/api/v1/analytics/geo/districts")
    assert res.status_code == 200
    body = res.json()
    assert len(body) == 2
    assert body[0]["case_count"] >= body[1]["case_count"]


def test_geo_incidents(client: TestClient) -> None:
    res = client.get("/api/v1/analytics/geo/incidents", params={"district_id": 443})
    assert res.status_code == 200
    body = res.json()
    assert body["total"] == 2
    assert all(p["district_id"] == 443 for p in body["items"])


def test_hotspots(client: TestClient) -> None:
    res = client.get("/api/v1/analytics/hotspots", params={"grain": "hour"})
    assert res.status_code == 200
    body = res.json()
    assert body["grain"] == "hour"
    assert len(body["bins"]) >= 1


def test_trend_alerts(client: TestClient) -> None:
    res = client.get("/api/v1/analytics/alerts/trends")
    assert res.status_code == 200
    body = res.json()
    assert "alerts" in body
    assert len(body["alerts"]) >= 1
