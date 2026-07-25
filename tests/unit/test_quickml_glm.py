"""Unit tests for Catalyst QuickML GLM client (mocked HTTP)."""

from __future__ import annotations

import json
from pathlib import Path

import httpx
import pytest

from app.core.config import Settings, get_settings
from app.integrations.catalyst.quickml import CatalystQuickMLClient


@pytest.fixture(autouse=True)
def _clear_settings_cache() -> None:
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()


def test_mock_rag_still_works(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    docs = [
        {
            "doc_id": "case:1",
            "case_master_id": 1,
            "crime_no": "104430006202600001",
            "brief_facts": "Snatching near MG Road metro; bike getaway",
            "text_blob": "Snatching theft bike metro",
        }
    ]
    path = tmp_path / "rag.json"
    path.write_text(json.dumps(docs), encoding="utf-8")
    monkeypatch.setenv("QUICKML_MOCK", "true")
    monkeypatch.setenv("RAG_DOCS_PATH", str(path))
    get_settings.cache_clear()
    client = CatalystQuickMLClient(Settings())
    out = client.rag_query("snatching bike", top_k=2)
    assert out["provider"] == "catalyst_quickml_mock"
    assert out["citations"]


def test_live_glm_hybrid(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    docs = [
        {
            "doc_id": "case:1",
            "case_master_id": 1,
            "crime_no": "104430006202600001",
            "brief_facts": "Snatching near MG Road",
            "text_blob": "Snatching theft bike",
        }
    ]
    path = tmp_path / "rag.json"
    path.write_text(json.dumps(docs), encoding="utf-8")
    monkeypatch.setenv("QUICKML_MOCK", "false")
    monkeypatch.setenv("RAG_DOCS_PATH", str(path))
    monkeypatch.setenv(
        "QUICKML_ENDPOINT",
        "https://api.catalyst.zoho.in/quickml/v1/project/50116000000022364/glm/chat",
    )
    monkeypatch.setenv("QUICKML_MODEL_ID", "crm-di-glm47b_30b_it")
    monkeypatch.setenv("QUICKML_ORG", "60078759306")
    monkeypatch.setenv("QUICKML_ACCESS_TOKEN", "test-token")
    get_settings.cache_clear()

    def handler(request: httpx.Request) -> httpx.Response:
        assert request.headers.get("Authorization") == "Bearer test-token"
        assert request.headers.get("CATALYST-ORG") == "60078759306"
        body = json.loads(request.content.decode())
        assert body["model"] == "crm-di-glm47b_30b_it"
        assert body["stream"] is False
        return httpx.Response(
            200,
            json={
                "choices": [
                    {
                        "message": {
                            "role": "assistant",
                            "content": "Linked snatching MO near MG Road (CrimeNo 104430006202600001).",
                        }
                    }
                ]
            },
        )

    transport = httpx.MockTransport(handler)
    real_client = httpx.Client

    def client_factory(*args: object, **kwargs: object) -> httpx.Client:
        kwargs = dict(kwargs)
        kwargs["transport"] = transport
        return real_client(*args, **kwargs)

    monkeypatch.setattr(httpx, "Client", client_factory)

    client = CatalystQuickMLClient(Settings())
    out = client.rag_query("snatching bike", top_k=2)
    assert out["provider"] == "catalyst_quickml_glm"
    assert "MG Road" in out["answer"]
    assert out["citations"]


def test_configured_requires_auth(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("QUICKML_MOCK", "false")
    monkeypatch.setenv(
        "QUICKML_ENDPOINT",
        "https://api.catalyst.zoho.in/quickml/v1/project/1/glm/chat",
    )
    monkeypatch.delenv("QUICKML_ACCESS_TOKEN", raising=False)
    monkeypatch.delenv("CATALYST_ACCESS_TOKEN", raising=False)
    monkeypatch.setenv("CATALYST_REFRESH_TOKEN", "")
    monkeypatch.setenv("CATALYST_CLIENT_ID", "")
    monkeypatch.setenv("CATALYST_CLIENT_SECRET", "")
    get_settings.cache_clear()
    client = CatalystQuickMLClient(Settings())
    assert client.configured is False
    assert client.mock_enabled is True
