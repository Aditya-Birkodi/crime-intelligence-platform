"""Case API integration tests using in-memory SQLite."""

from __future__ import annotations

import sys
from collections.abc import Generator
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
from app.models.legal.act import Act
from app.models.legal.section import Section
from app.models.lookups.case_category import CaseCategory
from app.models.lookups.case_status_master import CaseStatusMaster
from app.repositories.case.factory import get_case_store
from app.repositories.case.postgres_case_store import PostgresCaseStore
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
    db.add(CaseCategory(lookup_value="FIR", category_code="1"))
    db.add(CaseStatusMaster(case_status_name="Under Investigation"))
    db.add(Act(act_code="IPC", act_description="Indian Penal Code"))
    db.flush()
    db.add(Section(act_code="IPC", section_code="379", section_description="Theft"))
    db.commit()
    db.close()

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


def test_create_and_list_case(client: TestClient) -> None:
    payload = {
        "crime_no": "104430006202600001",
        "case_no": "202600001",
        "police_station_id": 6,
        "case_category_id": 1,
        "case_status_id": 1,
        "brief_facts": "Test theft FIR",
        "victims": [{"victim_name": "Test Victim", "gender_id": "M"}],
        "accused": [{"accused_name": "Test Accused", "person_id": "A1"}],
        "act_sections": [{"act_id": "IPC", "section_id": "379"}],
    }
    created = client.post("/api/v1/cases", json=payload)
    assert created.status_code == 201, created.text
    body = created.json()
    assert body["crime_no"] == "104430006202600001"
    assert len(body["victims"]) == 1
    assert len(body["accused"]) == 1

    listed = client.get("/api/v1/cases")
    assert listed.status_code == 200
    assert listed.json()["total"] == 1

    detail = client.get(f"/api/v1/cases/{body['case_master_id']}")
    assert detail.status_code == 200
    assert detail.json()["brief_facts"] == "Test theft FIR"


def test_reject_bad_crime_no(client: TestClient) -> None:
    payload = {
        "crime_no": "123",
        "case_no": "202600001",
        "police_station_id": 6,
        "case_category_id": 1,
        "case_status_id": 1,
    }
    response = client.post("/api/v1/cases", json=payload)
    assert response.status_code in (422, 400)
