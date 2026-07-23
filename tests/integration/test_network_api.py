"""Network API integration tests (CaseStore / SQLite)."""

from __future__ import annotations

import sys
from collections.abc import Generator
from datetime import date
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
from app.models.geography.district import District
from app.models.geography.state import State
from app.models.geography.unit import Unit
from app.models.geography.unit_type import UnitType
from app.models.lookups.case_category import CaseCategory
from app.models.lookups.case_status_master import CaseStatusMaster
from app.repositories.case.factory import get_case_store
from app.repositories.case.postgres_case_store import PostgresCaseStore
from app.schemas.case.case_master import AccusedCreate, CaseMasterCreate, VictimCreate
from main import app


@pytest.fixture()
def client() -> Generator[TestClient, None, None]:
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

    def override_get_case_store() -> Generator[PostgresCaseStore, None, None]:
        db = TestingSession()
        try:
            yield PostgresCaseStore(db)
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_case_store] = override_get_case_store

    db = TestingSession()
    state = State(state_name="Karnataka")
    db.add(state)
    db.flush()
    db.add(
        District(
            district_id=443, district_name="Bengaluru City", state_id=state.state_id
        )
    )
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
            unit_id=12,
            unit_name="Koramangala PS",
            type_id=ut.unit_type_id,
            state_id=state.state_id,
            district_id=443,
        )
    )
    db.add(CaseCategory(lookup_value="FIR", category_code="1"))
    db.add(CaseStatusMaster(case_status_name="Under Investigation"))
    db.commit()
    db.close()

    store_db = TestingSession()
    store = PostgresCaseStore(store_db)
    store.create(
        CaseMasterCreate(
            crime_no="104430006202600001",
            case_no="202600001",
            crime_registered_date=date(2026, 1, 15),
            police_station_id=6,
            case_category_id=1,
            case_status_id=1,
            brief_facts="Snatching near MG Road",
            victims=[VictimCreate(victim_name="Ravi")],
            accused=[
                AccusedCreate(accused_name="Ramesh K", person_id="P100"),
                AccusedCreate(accused_name="Helper", person_id="H1"),
            ],
        ),
        case_no="202600001",
    )
    store.create(
        CaseMasterCreate(
            crime_no="104430006202600003",
            case_no="202600003",
            crime_registered_date=date(2026, 3, 12),
            police_station_id=12,
            case_category_id=1,
            case_status_id=1,
            brief_facts="Repeat snatching MO",
            victims=[VictimCreate(victim_name="Priya")],
            accused=[AccusedCreate(accused_name="Ramesh K", person_id="P100")],
        ),
        case_no="202600003",
    )
    store_db.close()

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


def test_network_graph_by_case(client: TestClient) -> None:
    response = client.get("/api/v1/network/graph", params={"case_id": 1, "depth": 2})
    assert response.status_code == 200
    body = response.json()
    assert body["seed"] == "case:1"
    types = {n["type"] for n in body["nodes"]}
    assert "case" in types
    assert "accused" in types
    assert "victim" in types
    relations = {e["relation"] for e in body["edges"]}
    assert "accused_of" in relations
    assert "same_person" in relations


def test_network_graph_requires_seed(client: TestClient) -> None:
    response = client.get("/api/v1/network/graph")
    assert response.status_code == 422


def test_offender_profile_repeat(client: TestClient) -> None:
    response = client.get("/api/v1/network/offenders/1")
    assert response.status_code == 200
    body = response.json()
    assert body["accused_name"] == "Ramesh K"
    assert body["case_count"] == 2
    assert len(body["linked_accused_ids"]) >= 1
