"""List Catalyst Data Store tables (live project).

Usage:
  PYTHONPATH=backend python scripts/list_catalyst_tables.py

Requires third-party OAuth in .env (same as probe_catalyst_table.py).
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
        return 1

    try:
        app = get_catalyst_app(settings)
        tables = app.datastore().get_all_tables()
    except CatalystNotConfiguredError as exc:
        print("CONFIG ERROR:", exc)
        return 1
    except Exception as exc:
        print("SDK ERROR:", type(exc).__name__, exc)
        return 2

    print(json.dumps(tables, indent=2, default=str))
    if isinstance(tables, list):
        names = []
        for t in tables:
            if isinstance(t, dict):
                names.append(
                    t.get("table_name") or t.get("name") or t.get("TABLE_NAME")
                )
            else:
                names.append(getattr(t, "table_name", None) or str(t))
        print("names:", names)
        needed = {
            "cip_case_master",
            "cip_victim",
            "cip_accused",
            "cip_act_section_association",
        }
        have = {str(n) for n in names if n}
        missing_t = sorted(needed - have)
        if missing_t:
            print("MISSING Wave-2 tables:", missing_t)
            print("Create them per database/seed/catalyst_tables_checklist.md")
            return 3
        print("Wave-2 tables: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
