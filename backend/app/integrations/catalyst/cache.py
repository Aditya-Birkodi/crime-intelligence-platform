"""Catalyst Cache — prompt / retrieval result caching (catalyst.txt #9)."""

from __future__ import annotations

from typing import Any

from app.core.config import Settings, get_settings
from app.core.logging import get_ai_logger


class CatalystCacheClient:
    """Cache adapter. Local Redis is dev-only; prod MUST use Catalyst Cache."""

    def __init__(self, settings: Settings | None = None) -> None:
        self._settings = settings or get_settings()
        self._logger = get_ai_logger()

    def get(self, key: str) -> Any | None:
        self._logger.info("cache_get key=%s", key)
        raise NotImplementedError("TODO: Catalyst Cache get (or Redis in local dev)")

    def set(self, key: str, value: Any, *, ttl_seconds: int = 300) -> None:
        self._logger.info("cache_set key=%s ttl=%s", key, ttl_seconds)
        raise NotImplementedError("TODO: Catalyst Cache set")
