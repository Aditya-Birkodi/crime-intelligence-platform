"""Shared pytest fixtures for cross-cutting tests.

TODO: Add DB session fixtures and Catalyst client mocks.
"""

from __future__ import annotations

import sys
from collections.abc import Generator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

BACKEND = Path(__file__).resolve().parents[1] / "backend"
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))


@pytest.fixture
def client() -> Generator[TestClient, None, None]:
    """HTTP test client for the FastAPI app."""
    from main import app

    with TestClient(app) as test_client:
        yield test_client
