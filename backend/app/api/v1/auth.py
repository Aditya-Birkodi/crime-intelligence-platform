"""Auth HTTP routes — SCRB desk login / session."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Header

from app.schemas.auth import LoginRequest, LoginResponse, MeResponse
from app.services.auth import service as auth_service

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=LoginResponse)
def login(payload: LoginRequest) -> LoginResponse:
    """Sign in with SCRB desk credentials (demo users for Catalyst Slate)."""
    auth_service.validate_login_payload(payload.username, payload.password)
    return auth_service.login(payload.username, payload.password)


@router.get("/me", response_model=MeResponse)
def me(
    authorization: Annotated[str | None, Header()] = None,
) -> MeResponse:
    """Return the current session user."""
    user = auth_service.require_user_from_header(authorization)
    return MeResponse(user=user)


@router.post("/logout")
def logout() -> dict[str, str]:
    """Client discards token; endpoint kept for desk UX completeness."""
    return {"status": "ok"}
