"""Seed live Catalyst Data Store from appsail_datastore.json.

Creates Wave-2 FIR rows in:
  cip_case_master → cip_victim / cip_accused / cip_act_section_association

Prerequisites:
  1. Create tables in console — see catalyst_tables_checklist.md
  2. DATASTORE_MOCK=false (and CATALYST_DATASTORE_MOCK unset/false)
  3. Auth:
     - Local: CATALYST_INIT_MODE=third_party + Self Client OAuth
       (PROJECT_ID, ZAID, CLIENT_ID, CLIENT_SECRET, REFRESH_TOKEN)
       CATALYST_PROJECT_DOMAIN=https://api.catalyst.zoho.in  (India DC)
     - AppSail: ambient SDK init (CATALYST_INIT_MODE=function)

Usage:
  DATASTORE_MOCK=false PYTHONPATH=backend \\
    python database/seed/seed_catalyst_datastore_live.py --limit 5

  # wipe existing Wave-2 rows then full seed
  DATASTORE_MOCK=false PYTHONPATH=backend \\
    python database/seed/seed_catalyst_datastore_live.py --force
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
BACKEND = ROOT / "backend"
SEED_DIR = Path(__file__).resolve().parent
DEFAULT_SOURCE = SEED_DIR / "appsail_datastore.json"

if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

_SYSTEM_COLS = frozenset(
    {"ROWID", "CREATORID", "CREATEDTIME", "MODIFIEDTIME", "CREATORID".lower()}
)

_CASE_COLS = (
    "crime_no",
    "case_no",
    "crime_registered_date",
    "police_person_id",
    "police_station_id",
    "case_category_id",
    "gravity_offence_id",
    "crime_major_head_id",
    "crime_minor_head_id",
    "case_status_id",
    "court_id",
    "incident_from_date",
    "incident_to_date",
    "info_received_ps_date",
    "latitude",
    "longitude",
    "brief_facts",
)

_VICTIM_COLS = ("victim_name", "age_year", "gender_id", "victim_police")
_ACCUSED_COLS = ("accused_name", "age_year", "gender_id", "person_id")
_ACT_COLS = ("act_id", "section_id", "act_order_id", "section_order_id")

_WAVE2_TABLES = (
    "cip_case_master",
    "cip_victim",
    "cip_accused",
    "cip_act_section_association",
)


def _strip_system(row: dict[str, Any]) -> dict[str, Any]:
    return {
        k: v
        for k, v in row.items()
        if k not in _SYSTEM_COLS and k.upper() not in _SYSTEM_COLS
    }


def _pick(row: dict[str, Any], cols: tuple[str, ...]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for col in cols:
        if col in row and row[col] is not None:
            out[col] = row[col]
    return out


def _row_id(row: dict[str, Any]) -> int | None:
    raw = row.get("ROWID")
    if raw is None:
        return None
    return int(raw)


def load_tables(source: Path) -> dict[str, list[dict[str, Any]]]:
    payload = json.loads(source.read_text(encoding="utf-8"))
    tables = payload.get("tables") if isinstance(payload, dict) else None
    if not isinstance(tables, dict):
        raise SystemExit(f"Invalid datastore JSON (missing tables): {source}")
    return {k: list(v) for k, v in tables.items() if isinstance(v, list)}


def seed_live(
    ds: Any,
    tables: dict[str, list[dict[str, Any]]],
    *,
    limit: int | None = None,
    force: bool = False,
) -> dict[str, int]:
    """Insert Wave-2 rows; remap mock case ROWIDs to live ROWIDs."""
    cases = list(tables.get("cip_case_master") or [])
    if limit is not None:
        cases = cases[: max(0, limit)]
    allowed_old_ids = {_row_id(c) for c in cases if _row_id(c) is not None}

    existing = ds.get_paged_rows("cip_case_master", max_rows=5)
    if existing and not force:
        raise SystemExit(
            f"cip_case_master already has rows (sample ROWID={existing[0].get('ROWID')}). "
            "Empty tables in console or re-run with --force."
        )
    if force:
        # Children first, then parents
        for table in (
            "cip_act_section_association",
            "cip_accused",
            "cip_victim",
            "cip_case_master",
        ):
            n = ds.delete_all_rows(table)
            print(f"force: deleted {n} rows from {table}")

    id_map: dict[int, int] = {}
    counts = {
        "cip_case_master": 0,
        "cip_victim": 0,
        "cip_accused": 0,
        "cip_act_section_association": 0,
    }

    for case in cases:
        old_id = _row_id(case)
        payload = _pick(_strip_system(case), _CASE_COLS)
        inserted = ds.insert_row("cip_case_master", payload)
        new_id = _row_id(inserted if isinstance(inserted, dict) else {})
        if new_id is None and isinstance(inserted, dict):
            # Some SDK shapes nest under data
            new_id = _row_id(inserted.get("data") or inserted)
        if old_id is None or new_id is None:
            raise RuntimeError(
                f"Failed to map case insert: old={old_id} inserted={inserted!r}"
            )
        id_map[old_id] = new_id
        counts["cip_case_master"] += 1

    for row in tables.get("cip_victim") or []:
        old_case = row.get("case_master_id")
        if old_case is None:
            continue
        old_case_i = int(old_case)
        if old_case_i not in allowed_old_ids or old_case_i not in id_map:
            continue
        payload = _pick(_strip_system(row), _VICTIM_COLS)
        payload["case_master_id"] = id_map[old_case_i]
        ds.insert_row("victim", payload)
        counts["cip_victim"] += 1

    for row in tables.get("cip_accused") or []:
        old_case = row.get("case_master_id")
        if old_case is None:
            continue
        old_case_i = int(old_case)
        if old_case_i not in allowed_old_ids or old_case_i not in id_map:
            continue
        payload = _pick(_strip_system(row), _ACCUSED_COLS)
        payload["case_master_id"] = id_map[old_case_i]
        ds.insert_row("accused", payload)
        counts["cip_accused"] += 1

    for row in tables.get("cip_act_section_association") or []:
        old_case = row.get("case_master_id")
        if old_case is None:
            continue
        old_case_i = int(old_case)
        if old_case_i not in allowed_old_ids or old_case_i not in id_map:
            continue
        payload = _pick(_strip_system(row), _ACT_COLS)
        payload["case_master_id"] = id_map[old_case_i]
        # defaults for mandatory order fields
        payload.setdefault("act_order_id", 1)
        payload.setdefault("section_order_id", 1)
        ds.insert_row("act_section_association", payload)
        counts["cip_act_section_association"] += 1

    return counts


def _require_live_mode() -> None:
    mock = os.getenv("DATASTORE_MOCK", os.getenv("CATALYST_DATASTORE_MOCK", "true"))
    if str(mock).lower() in {"1", "true", "yes"}:
        raise SystemExit(
            "Refusing to run: DATASTORE_MOCK/CATALYST_DATASTORE_MOCK is true. "
            "Set DATASTORE_MOCK=false to seed live Data Store."
        )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--source",
        type=Path,
        default=DEFAULT_SOURCE,
        help="Path to appsail_datastore.json",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Seed only the first N cases (smoke test)",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Delete existing Wave-2 rows before seeding",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Parse source and print counts only (no Catalyst calls)",
    )
    args = parser.parse_args(argv)

    tables = load_tables(args.source)
    n_cases = len(tables.get("cip_case_master") or [])
    print(f"source={args.source} cases={n_cases} limit={args.limit}")
    for t in _WAVE2_TABLES:
        print(f"  {t}: {len(tables.get(t) or [])}")

    if args.dry_run:
        print("dry-run: OK")
        return 0

    _require_live_mode()

    # Ensure settings pick up env before first get_settings()
    os.environ.setdefault("PERSISTENCE_BACKEND", "catalyst")
    os.environ["DATASTORE_MOCK"] = "false"
    os.environ["CATALYST_DATASTORE_MOCK"] = "false"

    from app.core.config import get_settings
    from app.integrations.catalyst import app_factory as af
    from app.integrations.catalyst.datastore import CatalystDataStoreClient

    get_settings.cache_clear()
    af._cached_catalyst_app.cache_clear()

    settings = get_settings()
    if settings.catalyst.datastore_mock:
        raise SystemExit("Settings still have datastore_mock=true — check env aliases.")

    ds = CatalystDataStoreClient(settings)
    try:
        counts = seed_live(ds, tables, limit=args.limit, force=args.force)
    except Exception as exc:
        print("SEED FAILED:", type(exc).__name__, exc)
        print(
            "Confirm tables exist (catalyst_tables_checklist.md) and OAuth/AppSail "
            "init is configured. Probe: PYTHONPATH=backend python scripts/probe_catalyst_table.py"
        )
        return 1

    print("seeded:", counts)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
