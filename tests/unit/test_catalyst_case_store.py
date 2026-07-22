"""Unit tests for Catalyst Data Store mock CaseStore."""

from __future__ import annotations

import sys
from datetime import date
from pathlib import Path

import pytest

BACKEND = Path(__file__).resolve().parents[2] / "backend"
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

from app.core.config import Settings, get_settings
from app.integrations.catalyst.datastore import CatalystDataStoreClient
from app.repositories.case.catalyst_case_store import CatalystCaseStore
from app.schemas.case.case_master import CaseMasterCreate, VictimCreate


@pytest.fixture()
def mock_store(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> CatalystCaseStore:
    mock_file = tmp_path / "ds.json"
    monkeypatch.setenv("PERSISTENCE_BACKEND", "catalyst")
    monkeypatch.setenv("CATALYST_DATASTORE_MOCK", "true")
    monkeypatch.setenv("CATALYST_DATASTORE_MOCK_PATH", str(mock_file))
    get_settings.cache_clear()
    settings = Settings()
    client = CatalystDataStoreClient(settings)
    return CatalystCaseStore(client)


def test_catalyst_mock_create_and_list(mock_store: CatalystCaseStore) -> None:
    payload = CaseMasterCreate(
        crime_no="104430006202600099",
        case_no="202600099",
        crime_registered_date=date(2026, 3, 1),
        police_station_id=6,
        case_category_id=1,
        case_status_id=1,
        brief_facts="mock FIR",
        victims=[VictimCreate(victim_name="Mock Victim", gender_id="M")],
    )
    created = mock_store.create(payload, case_no=payload.case_no)
    assert created.case_master_id > 0
    assert created.victims[0].victim_name == "Mock Victim"

    items, total = mock_store.list_filtered(limit=10, offset=0)
    assert total == 1
    assert items[0].crime_no == "104430006202600099"

    detail = mock_store.get_detail(created.case_master_id)
    assert detail is not None
    assert detail.brief_facts == "mock FIR"
