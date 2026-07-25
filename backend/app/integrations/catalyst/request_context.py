"""Request-scoped Catalyst context for AppSail SDK init."""

from __future__ import annotations

from contextvars import ContextVar
from typing import Any

_catalyst_request: ContextVar[Any] = ContextVar("catalyst_request", default=None)


def set_catalyst_request(request: Any) -> Any:
    return _catalyst_request.set(request)


def reset_catalyst_request(token: Any) -> None:
    _catalyst_request.reset(token)


def get_catalyst_request() -> Any:
    return _catalyst_request.get()
