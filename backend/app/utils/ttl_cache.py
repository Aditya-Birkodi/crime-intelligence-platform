"""Simple in-memory TTL cache for analytics (dev).

TODO: Swap to Catalyst Cache (prod) / Redis (local) via integrations/catalyst/cache.py.
"""

from __future__ import annotations

import time
from threading import Lock
from typing import Any, TypeVar

T = TypeVar("T")

_lock = Lock()
_store: dict[str, tuple[float, Any]] = {}


def cache_get(key: str) -> Any | None:
    now = time.monotonic()
    with _lock:
        item = _store.get(key)
        if item is None:
            return None
        expires_at, value = item
        if expires_at < now:
            del _store[key]
            return None
        return value


def cache_set(key: str, value: Any, *, ttl_seconds: int = 60) -> None:
    with _lock:
        _store[key] = (time.monotonic() + ttl_seconds, value)


def cache_clear() -> None:
    with _lock:
        _store.clear()
