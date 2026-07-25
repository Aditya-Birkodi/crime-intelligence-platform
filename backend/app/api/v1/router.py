"""API v1 router aggregator."""

from __future__ import annotations

from fastapi import APIRouter

from app.api.v1.admin import router as admin_router
from app.api.v1.ai import router as ai_router
from app.api.v1.analytics import router as analytics_router
from app.api.v1.cases import router as cases_router
from app.api.v1.lookups import router as lookups_router
from app.api.v1.media import router as media_router
from app.api.v1.network import router as network_router
from app.api.v1.search import router as search_router

api_router = APIRouter()
api_router.include_router(cases_router)
api_router.include_router(lookups_router)
api_router.include_router(analytics_router)
api_router.include_router(network_router)
api_router.include_router(ai_router)
api_router.include_router(search_router)
api_router.include_router(media_router)
api_router.include_router(admin_router)


@api_router.get("/status", tags=["infrastructure"])
async def api_status() -> dict[str, str]:
    """Versioned API liveness (not a domain endpoint)."""
    from app.core.config import get_settings

    settings = get_settings()
    live = (
        settings.persistence_backend == "catalyst"
        and not settings.catalyst.datastore_mock
    )
    return {
        "api": "v1",
        "status": "ready",
        "persistence": settings.persistence_backend,
        "datastore_mock": str(settings.catalyst.datastore_mock).lower(),
        "cases_source": "catalyst_datastore" if live else settings.persistence_backend,
        "lookups_source": "catalyst_datastore+json" if live else "json_or_postgres",
        "analytics_source": (
            "catalyst_datastore" if live else settings.persistence_backend
        ),
    }
