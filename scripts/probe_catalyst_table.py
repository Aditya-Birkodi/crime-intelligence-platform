"""Probe Catalyst Data Store get_table_details(table_id).

Usage:
  PYTHONPATH=backend ./env/bin/python scripts/probe_catalyst_table.py [TABLE_ID]

Requires in .env (third-party mode):
  CATALYST_PROJECT_ID, CATALYST_ZAID, CATALYST_CLIENT_ID,
  CATALYST_CLIENT_SECRET, CATALYST_REFRESH_TOKEN
Optional: CATALYST_TABLE_CASE_MASTER as default TABLE_ID
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

from app.core.config import get_settings
from app.integrations.catalyst.app_factory import (
    CatalystNotConfiguredError,
    get_catalyst_app,
)


def main() -> int:
    get_settings.cache_clear()
    from app.integrations.catalyst import app_factory as af

    af._cached_catalyst_app.cache_clear()
    settings = get_settings()
    cat = settings.catalyst

    missing = [
        name
        for name, ok in (
            ("CATALYST_PROJECT_ID", bool(cat.project_id)),
            ("CATALYST_ZAID", bool(cat.zaid)),
            ("CATALYST_CLIENT_ID", bool(cat.client_id)),
            ("CATALYST_CLIENT_SECRET", bool(cat.client_secret)),
            ("CATALYST_REFRESH_TOKEN", bool(cat.refresh_token)),
        )
        if not ok
    ]
    if missing:
        print("Missing .env for live Data Store:", ", ".join(missing))
        print("Fill those, set CATALYST_INIT_MODE=third_party, then re-run:")
        print(
            "  PYTHONPATH=backend ./env/bin/python scripts/probe_catalyst_table.py <TABLE_ID>"
        )
        return 1

    table_id: str | int
    if len(sys.argv) > 1:
        table_id = sys.argv[1]
    elif cat.table_case_master:
        table_id = cat.table_case_master
    else:
        print("Pass your table ID: scripts/probe_catalyst_table.py <TABLE_ID>")
        return 1

    if str(table_id).isdigit():
        table_id = int(table_id)

    print(f"project_id set env={cat.env!r}")
    print(f"calling get_table_details({table_id!r})")

    try:
        app = get_catalyst_app(settings)
        datastore_service = app.datastore()
        table_data = datastore_service.get_table_details(table_id)
    except CatalystNotConfiguredError as exc:
        print("CONFIG ERROR:", exc)
        return 1
    except Exception as exc:
        print("SDK ERROR:", type(exc).__name__, exc)
        return 2

    print(json.dumps(table_data, indent=2, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
