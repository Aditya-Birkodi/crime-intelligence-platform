"""Catalyst app initialization.

Install (official setup):
  pip install zcatalyst-sdk
  https://docs.catalyst.zoho.com/en/sdk/python/v1/setup/

Init modes:
  - function: ``zcatalyst_sdk.initialize(scope=...)`` when code runs inside
    Catalyst Functions / AppSail (ambient project context).
  - third_party: ``initialize_app`` + RefreshTokenCredential when FastAPI runs
    outside Catalyst (local, ngrok, non-Catalyst host).
    https://docs.catalyst.zoho.com/en/sdk/python/v1/integrate-sdk-in-third-party-apps/
"""

from __future__ import annotations

from functools import lru_cache
from typing import Any, Literal

from app.core.config import Settings, get_settings
from app.core.logging import get_application_logger

InitMode = Literal["auto", "function", "third_party"]


class CatalystNotConfiguredError(RuntimeError):
    """Raised when Catalyst credentials are incomplete."""


def _import_sdk() -> Any:
    try:
        import zcatalyst_sdk
    except ImportError as exc:
        raise CatalystNotConfiguredError(
            "Install zcatalyst-sdk per Catalyst docs: pip install zcatalyst-sdk"
        ) from exc
    return zcatalyst_sdk


def _init_function_scope(settings: Settings) -> Any:
    """In-Catalyst Functions / AppSail init (setup docs)."""
    zcatalyst_sdk = _import_sdk()
    scope = (settings.catalyst.sdk_scope or "admin").lower()
    if scope not in {"admin", "user"}:
        scope = "admin"
    app = zcatalyst_sdk.initialize(scope=scope)
    get_application_logger().info(
        "Catalyst SDK initialize() scope=%s (function/AppSail mode)", scope
    )
    return app


def _init_third_party(settings: Settings) -> Any:
    """External host init (third-party apps docs)."""
    zcatalyst_sdk = _import_sdk()
    from zcatalyst_sdk import credentials, types

    cat = settings.catalyst
    if not (
        cat.project_id
        and cat.zaid
        and cat.refresh_token
        and cat.client_id
        and cat.client_secret
    ):
        raise CatalystNotConfiguredError(
            "Third-party Catalyst init needs CATALYST_PROJECT_ID, CATALYST_ZAID, "
            "CATALYST_REFRESH_TOKEN, CATALYST_CLIENT_ID, CATALYST_CLIENT_SECRET "
            "(or set CATALYST_INIT_MODE=function inside Catalyst Functions)"
        )

    cred = credentials.RefreshTokenCredential(
        {
            "refresh_token": cat.refresh_token,
            "client_id": cat.client_id,
            "client_secret": cat.client_secret,
        }
    )
    options = types.ICatalystOptions(
        project_id=cat.project_id,
        project_key=cat.zaid,
        project_domain=cat.project_domain,
        environment=cat.env,
    )
    app = zcatalyst_sdk.initialize_app(
        credential=cred,
        options=options,
        name="cip-backend",
    )
    get_application_logger().info(
        "Catalyst SDK initialize_app() project_id=%s env=%s",
        cat.project_id,
        cat.env,
    )
    return app


def get_catalyst_app(settings: Settings | None = None, *, req: Any = None) -> Any:
    """Return a Catalyst app instance for Data Store / ZCQL / other components.

    On AppSail, pass (or context-bind) the HTTP request so
    ``initialize(req=request)`` can read Catalyst gateway headers.
    """
    cfg = settings or get_settings()
    from app.integrations.catalyst.request_context import get_catalyst_request

    request = req if req is not None else get_catalyst_request()

    # Prefer per-request init when a web request is available (AppSail).
    if request is not None and not (
        cfg.catalyst.refresh_token
        and cfg.catalyst.client_id
        and cfg.catalyst.client_secret
        and cfg.catalyst.zaid
        and cfg.catalyst.init_mode == "third_party"
    ):
        # Cache on request.state to avoid re-init within the same request.
        state = getattr(request, "state", None)
        if state is not None and getattr(state, "zc_app", None) is not None:
            return state.zc_app
        try:
            import zcatalyst_sdk

            scope = (cfg.catalyst.sdk_scope or "admin").lower()
            if scope not in {"admin", "user"}:
                scope = "admin"
            app = zcatalyst_sdk.initialize(req=request, scope=scope)
            if state is not None:
                state.zc_app = app
            get_application_logger().info(
                "Catalyst SDK initialize(req=...) scope=%s", scope
            )
            return app
        except Exception:
            get_application_logger().exception(
                "Catalyst initialize(req=...) failed; falling back to cached init"
            )

    return _cached_catalyst_app(
        cfg.catalyst.init_mode,
        cfg.catalyst.sdk_scope,
        cfg.catalyst.project_id,
        cfg.catalyst.zaid,
        cfg.catalyst.env,
        cfg.catalyst.project_domain,
        cfg.catalyst.client_id,
        cfg.catalyst.client_secret,
        cfg.catalyst.refresh_token,
    )


@lru_cache
def _cached_catalyst_app(
    init_mode: str,
    sdk_scope: str,
    project_id: str,
    zaid: str,
    env: str,
    project_domain: str,
    client_id: str,
    client_secret: str,
    refresh_token: str,
) -> Any:
    cfg = get_settings()
    mode: InitMode = init_mode  # type: ignore[assignment]

    if mode == "function":
        return _init_function_scope(cfg)
    if mode == "third_party":
        return _init_third_party(cfg)

    # auto: prefer third-party when OAuth creds exist; else function ambient init
    if refresh_token and client_id and client_secret and project_id and zaid:
        return _init_third_party(cfg)
    try:
        return _init_function_scope(cfg)
    except Exception as exc:
        raise CatalystNotConfiguredError(
            "Could not initialize Catalyst SDK. Either run inside Catalyst Functions "
            "(CATALYST_INIT_MODE=function) or set Self-Client OAuth env vars. "
            "Setup: https://docs.catalyst.zoho.com/en/sdk/python/v1/setup/ "
            "Third-party: https://docs.catalyst.zoho.com/en/sdk/python/v1/integrate-sdk-in-third-party-apps/"
        ) from exc
