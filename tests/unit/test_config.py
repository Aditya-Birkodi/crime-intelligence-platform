"""Unit tests for configuration loading."""

from __future__ import annotations

from app.core.config import Settings, get_settings


def test_settings_defaults() -> None:
    """Settings load with expected default app name."""
    get_settings.cache_clear()
    settings = Settings()
    assert settings.app_name == "crime-intelligence-platform"
    assert settings.api_v1_prefix == "/api/v1"
    assert settings.catalyst.datastore_table_prefix == "cip_"


def test_get_settings_cached() -> None:
    """get_settings returns a cached singleton."""
    get_settings.cache_clear()
    a = get_settings()
    b = get_settings()
    assert a is b
