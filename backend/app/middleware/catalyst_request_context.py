"""Bind ASGI request for Catalyst SDK initialize(req=...)."""

from __future__ import annotations

from collections.abc import Awaitable, Callable

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from app.integrations.catalyst.request_context import (
    reset_catalyst_request,
    set_catalyst_request,
)


class CatalystRequestContextMiddleware(BaseHTTPMiddleware):  # type: ignore[misc]
    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        token = set_catalyst_request(request)
        try:
            return await call_next(request)
        finally:
            reset_catalyst_request(token)
