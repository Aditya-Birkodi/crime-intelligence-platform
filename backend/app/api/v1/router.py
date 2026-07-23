"""API v1 router aggregator."""

from __future__ import annotations

from fastapi import APIRouter

from app.api.v1.analytics import router as analytics_router
from app.api.v1.cases import router as cases_router
from app.api.v1.lookups import router as lookups_router
from app.api.v1.network import router as network_router

api_router = APIRouter()
api_router.include_router(cases_router)
api_router.include_router(lookups_router)
api_router.include_router(analytics_router)
api_router.include_router(network_router)


@api_router.get("/status", tags=["infrastructure"])
async def api_status() -> dict[str, str]:
    """Versioned API liveness (not a domain endpoint)."""
    return {"api": "v1", "status": "ready"}
