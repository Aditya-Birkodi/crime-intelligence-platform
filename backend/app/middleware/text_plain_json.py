"""Normalize CORS-safelisted request bodies for AppSail / browser clients.

Catalyst AppSail's edge answers OPTIONS without Access-Control-* headers, so
browser preflights for `Content-Type: application/json` fail with Failed to fetch.

Clients can send JSON as `text/plain` (CORS-safelisted → no preflight). This
middleware rewrites that Content-Type to `application/json` before FastAPI parsing.
"""

from __future__ import annotations

from starlette.datastructures import MutableHeaders
from starlette.types import ASGIApp, Receive, Scope, Send


class TextPlainJsonContentTypeMiddleware:
    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] == "http" and scope.get("method") in {
            "POST",
            "PUT",
            "PATCH",
        }:
            headers = MutableHeaders(scope=scope)
            content_type = headers.get("content-type", "")
            if content_type.lower().startswith("text/plain"):
                headers["content-type"] = "application/json"
        await self.app(scope, receive, send)
