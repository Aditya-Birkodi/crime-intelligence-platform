"""Analytics + lookups on Catalyst mock (AppSail path)."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[2]
BACKEND = ROOT / "backend"
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))


@pytest.fixture()
def client(monkeypatch: pytest.MonkeyPatch) -> TestClient:
    monkeypatch.setenv("PERSISTENCE_BACKEND", "catalyst")
    monkeypatch.setenv("DATASTORE_MOCK", "true")
    monkeypatch.setenv(
        "DATASTORE_MOCK_PATH", str(ROOT / "database/seed/appsail_datastore.json")
    )
    monkeypatch.setenv("LOOKUPS_PATH", str(ROOT / "database/seed/appsail_lookups.json"))
    monkeypatch.setenv("QUICKML_MOCK", "true")
    monkeypatch.setenv(
        "RAG_DOCS_PATH", str(ROOT / "database/seed/fir_rag_documents.json")
    )
    monkeypatch.setenv(
        "AI_FEATURES_PATH", str(ROOT / "database/seed/ai_case_features.json")
    )
    from app.core.config import get_settings
    from app.services.lookups_catalog import clear_lookups_cache

    get_settings.cache_clear()
    clear_lookups_cache()
    from main import app

    with TestClient(app) as test_client:
        yield test_client
    get_settings.cache_clear()
    clear_lookups_cache()


def test_mock_analytics_overview(client: TestClient) -> None:
    res = client.get("/api/v1/analytics/overview")
    assert res.status_code == 200, res.text
    body = res.json()
    assert body["total_cases"] >= 100
    assert body["cases_with_coordinates"] >= 1


def test_mock_lookups_districts(client: TestClient) -> None:
    res = client.get("/api/v1/lookups/districts")
    assert res.status_code == 200, res.text
    assert len(res.json()) >= 3


def test_mock_geo_incidents(client: TestClient) -> None:
    res = client.get("/api/v1/analytics/geo/incidents?limit=10")
    assert res.status_code == 200, res.text
    assert res.json()["total"] >= 1
