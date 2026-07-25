"""Unit tests for live Data Store seed remapping (uses JSON mock client)."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
BACKEND = ROOT / "backend"
SEED = ROOT / "database" / "seed"
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))
if str(SEED) not in sys.path:
    sys.path.insert(0, str(SEED))

from seed_catalyst_datastore_live import load_tables, seed_live  # noqa: E402

from app.core.config import Settings, get_settings  # noqa: E402
from app.integrations.catalyst.datastore import CatalystDataStoreClient  # noqa: E402


@pytest.fixture()
def mock_ds(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> CatalystDataStoreClient:
    path = tmp_path / "ds.json"
    path.write_text(json.dumps({"seq": 1, "tables": {}}), encoding="utf-8")
    monkeypatch.setenv("DATASTORE_MOCK", "true")
    monkeypatch.setenv("DATASTORE_MOCK_PATH", str(path))
    get_settings.cache_clear()
    # Force mock even if Settings cached differently
    settings = Settings()
    # pydantic may still read DATASTORE_MOCK
    client = CatalystDataStoreClient(settings)
    client._mock = True
    client._mock_path = path
    return client


def test_seed_live_remaps_case_ids(mock_ds: CatalystDataStoreClient) -> None:
    tables = {
        "cip_case_master": [
            {
                "ROWID": 10,
                "crime_no": "104430006202600001",
                "case_no": "202600001",
                "police_station_id": 6,
                "case_category_id": 1,
                "case_status_id": 1,
                "brief_facts": "test",
            }
        ],
        "cip_victim": [
            {
                "ROWID": 1,
                "case_master_id": 10,
                "victim_name": "A",
                "age_year": 30,
                "gender_id": "M",
            }
        ],
        "cip_accused": [
            {
                "ROWID": 1,
                "case_master_id": 10,
                "accused_name": "B",
                "person_id": "P1",
            }
        ],
        "cip_act_section_association": [
            {
                "ROWID": 1,
                "case_master_id": 10,
                "act_id": "IPC",
                "section_id": "379",
                "act_order_id": 1,
                "section_order_id": 1,
            }
        ],
    }
    counts = seed_live(mock_ds, tables, limit=1, force=False)
    assert counts["cip_case_master"] == 1
    assert counts["cip_victim"] == 1
    assert counts["cip_accused"] == 1
    assert counts["cip_act_section_association"] == 1

    cases = mock_ds.get_paged_rows("cip_case_master", max_rows=10)
    assert len(cases) == 1
    new_id = int(cases[0]["ROWID"])
    assert new_id != 10  # remapped away from mock id space ideally; mock seq starts 1
    victims = mock_ds.get_paged_rows("cip_victim", max_rows=10)
    assert int(victims[0]["case_master_id"]) == new_id


def test_load_tables_from_appsail_json() -> None:
    path = ROOT / "database" / "seed" / "appsail_datastore.json"
    if not path.exists():
        pytest.skip("appsail_datastore.json missing")
    tables = load_tables(path)
    assert len(tables["cip_case_master"]) >= 1
