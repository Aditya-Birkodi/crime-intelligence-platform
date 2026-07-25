"""One-shot admin routes (AppSail function-scope Data Store seed)."""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Any

from fastapi import APIRouter, Header, Query

from app.exceptions.base import UnauthorizedError, ValidationError

router = APIRouter(prefix="/admin", tags=["infrastructure"])


@router.post("/seed-datastore")
def seed_datastore(
    force: bool = Query(False),
    limit: int | None = Query(None, ge=1, le=500),
    x_cip_seed_token: str | None = Header(default=None, alias="X-CIP-SEED-TOKEN"),
) -> dict[str, Any]:
    """Seed Wave-2 Data Store tables from bundled appsail_datastore.json.

    Requires env CIP_SEED_TOKEN and matching X-CIP-SEED-TOKEN header.
    Uses ambient Catalyst SDK on AppSail (function init).
    """
    expected = (os.getenv("CIP_SEED_TOKEN") or "").strip()
    if not expected:
        raise ValidationError(
            "CIP_SEED_TOKEN is not configured on AppSail — set it in console env, "
            "then call with header X-CIP-SEED-TOKEN"
        )
    if not x_cip_seed_token or x_cip_seed_token.strip() != expected:
        raise UnauthorizedError("Invalid or missing X-CIP-SEED-TOKEN")

    os.environ["DATASTORE_MOCK"] = "false"
    os.environ["CATALYST_DATASTORE_MOCK"] = "false"
    os.environ.setdefault("CATALYST_INIT_MODE", "function")

    root = Path(__file__).resolve().parents[4]
    seed_dir = root / "database" / "seed"
    if str(seed_dir) not in sys.path:
        sys.path.insert(0, str(seed_dir))

    from seed_catalyst_datastore_live import load_tables, seed_live

    from app.core.config import get_settings
    from app.integrations.catalyst import app_factory as af
    from app.integrations.catalyst.datastore import CatalystDataStoreClient

    get_settings.cache_clear()
    af._cached_catalyst_app.cache_clear()

    source = seed_dir / "appsail_datastore.json"
    if not source.exists():
        # AppSail cwd is usually repo root
        alt = Path("database/seed/appsail_datastore.json")
        source = alt if alt.exists() else source
    if not source.exists():
        raise ValidationError(f"Seed file missing on AppSail: {source}")

    tables = load_tables(source)
    settings = get_settings()
    ds = CatalystDataStoreClient(settings)
    if settings.catalyst.datastore_mock:
        raise ValidationError(
            "Datastore still in mock mode — set DATASTORE_MOCK=false on AppSail"
        )

    try:
        counts = seed_live(ds, tables, limit=limit, force=force)
    except SystemExit as exc:
        raise ValidationError(str(exc) or "Seed aborted") from exc
    except Exception as exc:
        raise ValidationError(
            f"Seed failed (create Wave-2 tables first per "
            f"database/seed/catalyst_tables_checklist.md): {type(exc).__name__}: {exc}"
        ) from exc
    return {"status": "ok", "counts": counts, "limit": limit, "force": force}
