"""Crime Intelligence Platform — FastAPI application entrypoint.

TODO: Mount domain routers, wire Catalyst Functions/AppSail adapters,
      and replace /health with readiness checks against Data Store / Cache.
"""

from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.core.config import get_settings
from app.core.logging import setup_logging
from app.exceptions.handlers import register_exception_handlers


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    """Application lifespan: startup / shutdown hooks.

    TODO: Initialize DB engine pool, Catalyst clients, and workers.
    """
    setup_logging()
    yield
    # TODO: Dispose engine / close Catalyst SDK clients.


def create_app() -> FastAPI:
    """Application factory (testable, DI-friendly)."""
    settings = get_settings()
    origins = [
        origin.strip() for origin in settings.cors_origins.split(",") if origin.strip()
    ]
    allow_all_origins = origins == ["*"] or settings.debug

    application = FastAPI(
        title=settings.app_name,
        version="0.1.0",
        description=(
            "Crime Intelligence Platform API for Karnataka State Police. "
            "Frontend contract: use /docs or /openapi.json. "
            "AI routes use Catalyst QuickML only."
        ),
        docs_url="/docs" if settings.debug else None,
        redoc_url="/redoc" if settings.debug else None,
        openapi_tags=[
            {"name": "infrastructure", "description": "Health and readiness"},
            {"name": "cases", "description": "FIR / CaseMaster (B1)"},
            {"name": "analytics", "description": "Geo, hotspots, trends (B2)"},
            {"name": "network", "description": "Link analysis graphs (B3)"},
            {"name": "ai", "description": "QuickML RAG, risk, anomalies (B4)"},
        ],
        lifespan=lifespan,
    )

    application.add_middleware(
        CORSMiddleware,
        allow_origins=["*"] if allow_all_origins else origins,
        allow_credentials=not allow_all_origins,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    register_exception_handlers(application)
    application.include_router(api_router, prefix=settings.api_v1_prefix)

    @application.get("/health", tags=["infrastructure"])
    async def health() -> dict[str, str]:
        """Infrastructure liveness probe — not a domain API."""
        return {"status": "ok", "service": settings.app_name}

    return application


app = create_app()
