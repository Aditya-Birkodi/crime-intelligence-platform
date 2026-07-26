"""Demo SCRB desk authentication (token session for Slate)."""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import time
from typing import Any

from app.core.config import Settings, get_settings
from app.exceptions.base import UnauthorizedError, ValidationError
from app.schemas.auth import AuthUser, LoginResponse


def _secret(settings: Settings) -> bytes:
    raw = (
        settings.auth_secret
        or settings.secret_key
        or settings.catalyst.client_secret
        or "cip-dev-auth-secret"
    )
    return str(raw).encode("utf-8")


def _demo_users(settings: Settings) -> dict[str, dict[str, str]]:
    """username → password + profile. Override via AUTH_DEMO_PASSWORD."""
    password = settings.auth_demo_password or "ksp2026"
    return {
        "scrb.analyst": {
            "password": password,
            "display_name": "SCRB Analyst",
            "role": "Intelligence Analyst",
            "unit": "State Crime Records Bureau",
        },
        "io.bengaluru": {
            "password": password,
            "display_name": "IO · Bengaluru City",
            "role": "Investigating Officer",
            "unit": "Bengaluru City Police",
        },
        "admin": {
            "password": password,
            "display_name": "CIP Administrator",
            "role": "System Admin",
            "unit": "SCRB · CIP",
        },
    }


def _b64url(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode("ascii").rstrip("=")


def _b64url_decode(data: str) -> bytes:
    pad = "=" * (-len(data) % 4)
    return base64.urlsafe_b64decode(data + pad)


def issue_token(user: AuthUser, settings: Settings | None = None) -> tuple[str, int]:
    settings = settings or get_settings()
    ttl = int(settings.auth_token_ttl_seconds or 86400)
    payload = {
        "sub": user.username,
        "name": user.display_name,
        "role": user.role,
        "unit": user.unit,
        "exp": int(time.time()) + ttl,
        "iat": int(time.time()),
    }
    body = _b64url(json.dumps(payload, separators=(",", ":")).encode("utf-8"))
    sig = _b64url(
        hmac.new(_secret(settings), body.encode("ascii"), hashlib.sha256).digest()
    )
    return f"{body}.{sig}", ttl


def verify_token(token: str, settings: Settings | None = None) -> AuthUser:
    settings = settings or get_settings()
    try:
        body, sig = token.split(".", 1)
    except ValueError as exc:
        raise UnauthorizedError("Invalid token") from exc
    expect = _b64url(
        hmac.new(_secret(settings), body.encode("ascii"), hashlib.sha256).digest()
    )
    if not hmac.compare_digest(sig, expect):
        raise UnauthorizedError("Invalid token signature")
    try:
        payload: dict[str, Any] = json.loads(_b64url_decode(body))
    except Exception as exc:
        raise UnauthorizedError("Malformed token") from exc
    if int(payload.get("exp") or 0) < int(time.time()):
        raise UnauthorizedError("Session expired")
    return AuthUser(
        username=str(payload.get("sub") or ""),
        display_name=str(payload.get("name") or ""),
        role=str(payload.get("role") or ""),
        unit=str(payload.get("unit") or "SCRB"),
    )


def login(
    username: str, password: str, settings: Settings | None = None
) -> LoginResponse:
    settings = settings or get_settings()
    users = _demo_users(settings)
    key = username.strip().lower()
    row = users.get(key)
    if row is None or not hmac.compare_digest(row["password"], password):
        raise UnauthorizedError("Invalid username or password")
    user = AuthUser(
        username=key,
        display_name=row["display_name"],
        role=row["role"],
        unit=row["unit"],
    )
    token, ttl = issue_token(user, settings)
    return LoginResponse(access_token=token, expires_in=ttl, user=user)


def require_user_from_header(authorization: str | None) -> AuthUser:
    if not authorization:
        raise UnauthorizedError("Missing Authorization header")
    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer" or not token.strip():
        raise UnauthorizedError("Expected Bearer token")
    return verify_token(token.strip())


def validate_login_payload(username: str, password: str) -> None:
    if not username.strip() or not password:
        raise ValidationError("Username and password are required")
