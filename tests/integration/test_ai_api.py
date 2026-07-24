"""B4 AI API integration tests (local QuickML mock + features file)."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

BACKEND = Path(__file__).resolve().parents[2] / "backend"
ROOT = Path(__file__).resolve().parents[2]
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

from main import app  # noqa: E402


@pytest.fixture()
def client(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> TestClient:
    docs = [
        {
            "doc_id": "case:104430006202600001",
            "case_master_id": 1,
            "crime_no": "104430006202600001",
            "brief_facts": "Snatching near MG Road metro; bike getaway",
            "text_blob": "CrimeNo: 104430006202600001 Brief Facts: Snatching theft bike",
            "district_id": 443,
            "crime_major_head": "property",
        },
        {
            "doc_id": "case:104430006202600002",
            "case_master_id": 2,
            "crime_no": "104430006202600002",
            "brief_facts": "Assault at bus stop",
            "text_blob": "CrimeNo: 104430006202600002 Brief Facts: Assault hurt",
            "district_id": 443,
            "crime_major_head": "body",
        },
    ]
    features = [
        {
            "case_master_id": 1,
            "crime_no": "104430006202600001",
            "district_id": 443,
            "police_station_id": 6,
            "crime_major_head": "property",
            "severity": "High",
            "risk_score": 92,
            "accused_count": 2,
            "arrest_count": 1,
            "has_chargesheet": False,
        },
        {
            "case_master_id": 2,
            "crime_no": "104430006202600002",
            "district_id": 443,
            "police_station_id": 6,
            "crime_major_head": "body",
            "severity": "Medium",
            "risk_score": 55,
            "accused_count": 1,
            "arrest_count": 0,
            "has_chargesheet": False,
        },
        {
            "case_master_id": 3,
            "crime_no": "110160001202500001",
            "district_id": 1016,
            "police_station_id": 2002,
            "crime_major_head": "property",
            "severity": "High",
            "risk_score": 88,
            "accused_count": 3,
            "arrest_count": 4,
            "has_chargesheet": False,
        },
    ]
    docs_path = tmp_path / "rag.json"
    feat_path = tmp_path / "feat.json"
    docs_path.write_text(json.dumps(docs), encoding="utf-8")
    feat_path.write_text(json.dumps(features), encoding="utf-8")
    monkeypatch.setenv("QUICKML_MOCK", "true")
    monkeypatch.setenv("RAG_DOCS_PATH", str(docs_path))
    monkeypatch.setenv("AI_FEATURES_PATH", str(feat_path))
    from app.core.config import get_settings

    get_settings.cache_clear()
    with TestClient(app) as test_client:
        yield test_client
    get_settings.cache_clear()


def test_ai_chat(client: TestClient) -> None:
    res = client.post(
        "/api/v1/ai/chat",
        json={"question": "snatching theft bike", "top_k": 3, "use_graph_rag": False},
    )
    assert res.status_code == 200, res.text
    body = res.json()
    assert "answer" in body
    assert body["citations"]
    assert body["provider"]


def test_ai_graph_rag_chat(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("PERSISTENCE_BACKEND", "catalyst")
    monkeypatch.setenv("DATASTORE_MOCK", "true")
    monkeypatch.setenv(
        "DATASTORE_MOCK_PATH", str(ROOT / "database/seed/appsail_datastore.json")
    )
    monkeypatch.setenv("QUICKML_MOCK", "true")
    monkeypatch.setenv(
        "RAG_DOCS_PATH", str(ROOT / "database/seed/fir_rag_documents.json")
    )
    from app.core.config import get_settings

    get_settings.cache_clear()
    from main import app

    with TestClient(app) as c:
        ctx = c.get("/api/v1/ai/graph/context?case_id=1&depth=2")
        assert ctx.status_code == 200, ctx.text
        body = ctx.json()
        assert body["engine"] == "networkx"
        assert body["node_count"] >= 1
        assert body["summary"]

        chat = c.post(
            "/api/v1/ai/chat",
            json={
                "question": "Who is linked to this snatching pattern?",
                "case_master_id": 1,
                "use_graph_rag": True,
                "graph_depth": 2,
                "top_k": 5,
            },
        )
        assert chat.status_code == 200, chat.text
        out = chat.json()
        assert out.get("graph_context") is not None
        assert "graph_rag" in out["provider"]
    get_settings.cache_clear()


def test_ai_predict_risk(client: TestClient) -> None:
    res = client.post("/api/v1/ai/predict/risk", json={"horizon_days": 7})
    assert res.status_code == 200, res.text
    body = res.json()
    assert body["items"]
    assert body["items"][0]["risk_score"] >= body["items"][-1]["risk_score"]


def test_ai_anomalies(client: TestClient) -> None:
    res = client.get("/api/v1/ai/anomalies?limit=10")
    assert res.status_code == 200, res.text
    body = res.json()
    assert body["total"] >= 1
    kinds = {i["kind"] for i in body["items"]}
    assert "high_risk_case" in kinds
