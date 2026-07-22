"""Backend-local pytest samples."""

from __future__ import annotations

from fastapi.testclient import TestClient

from main import app


def test_app_imports() -> None:
    assert app.title == "crime-intelligence-platform"


def test_health() -> None:
    with TestClient(app) as client:
        response = client.get("/health")
        assert response.status_code == 200
