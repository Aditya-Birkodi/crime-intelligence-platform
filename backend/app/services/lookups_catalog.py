"""Lookup catalog for AppSail / Catalyst.

Prefer live Data Store master tables when ``PERSISTENCE_BACKEND=catalyst`` and
``DATASTORE_MOCK=false``. Fall back to ``appsail_lookups.json`` (or LOOKUPS_PATH)
for keys that are not in Data Store yet (crime heads, courts, etc.).
"""

from __future__ import annotations

import contextlib
import json
from functools import lru_cache
from pathlib import Path
from typing import Any

from app.core.config import get_settings
from app.core.logging import get_application_logger

# logical DS table → (id column, name column, optional extra fields)
_DS_LOOKUPS: dict[str, tuple[str, str, str]] = {
    "case_statuses": ("case_status_master", "case_status_id", "case_status_name"),
    "districts": ("district", "district_id", "district_name"),
    "stations": ("unit", "unit_id", "unit_name"),
}


def _default_lookups_path() -> Path:
    return (
        Path(__file__).resolve().parents[3]
        / "database"
        / "seed"
        / "appsail_lookups.json"
    )


def lookups_path() -> Path:
    settings = get_settings()
    configured = getattr(settings.catalyst, "lookups_path", "") or ""
    return Path(configured) if configured else _default_lookups_path()


def _load_json_lookups() -> dict[str, Any]:
    path = lookups_path()
    if not path.exists():
        return {}
    raw = json.loads(path.read_text(encoding="utf-8"))
    return raw if isinstance(raw, dict) else {}


def _use_live_datastore() -> bool:
    settings = get_settings()
    return (
        settings.persistence_backend == "catalyst"
        and not settings.catalyst.datastore_mock
    )


def _rows_from_datastore(logical_table: str) -> list[dict[str, Any]]:
    from app.integrations.catalyst.datastore import CatalystDataStoreClient

    return CatalystDataStoreClient().get_paged_rows(logical_table, max_rows=5000)


def _overlay_datastore(base: dict[str, Any]) -> dict[str, Any]:
    """Replace districts / stations / case_statuses from live DS when non-empty."""
    log = get_application_logger()
    out = dict(base)
    for key, (logical, id_col, name_col) in _DS_LOOKUPS.items():
        try:
            rows = _rows_from_datastore(logical)
        except Exception:
            log.exception("lookups_ds_overlay_failed key=%s", key)
            continue
        if not rows:
            continue
        mapped: list[dict[str, Any]] = []
        for r in rows:
            try:
                rid = int(r.get(id_col) or 0)
            except (TypeError, ValueError):
                continue
            if not rid:
                continue
            item: dict[str, Any] = {
                "id": rid,
                "name": str(r.get(name_col) or rid),
            }
            if key == "stations":
                did = r.get("district_id")
                if did not in (None, ""):
                    with contextlib.suppress(TypeError, ValueError):
                        item["district_id"] = int(str(did))
            mapped.append(item)
        if mapped:
            out[key] = mapped
            log.info("lookups_ds_overlay key=%s rows=%s", key, len(mapped))

    # Rebuild station → district map from stations (JSON or DS)
    station_district: dict[str, int] = {}
    for s in out.get("stations") or []:
        sid = s.get("id")
        did = s.get("district_id")
        if sid is not None and did is not None:
            station_district[str(int(sid))] = int(did)
    if station_district:
        # Preserve any JSON-only mappings for stations not in DS
        merged = dict(out.get("station_district") or {})
        merged.update(station_district)
        out["station_district"] = merged
    return out


@lru_cache(maxsize=1)
def load_lookups() -> dict[str, Any]:
    base = _load_json_lookups()
    if _use_live_datastore():
        return _overlay_datastore(base)
    return base


def clear_lookups_cache() -> None:
    load_lookups.cache_clear()


def id_name_list(key: str) -> list[dict[str, Any]]:
    rows = load_lookups().get(key) or []
    return [{"id": int(r["id"]), "name": str(r["name"])} for r in rows if "id" in r]


def district_name(district_id: int) -> str:
    for d in load_lookups().get("districts") or []:
        if int(d.get("id") or 0) == district_id:
            return str(d.get("name") or district_id)
    return str(district_id)


def crime_head_name(head_id: int | None) -> str:
    if head_id is None:
        return "Unclassified"
    for h in load_lookups().get("crime_heads") or []:
        if int(h.get("id") or 0) == head_id:
            return str(h.get("name") or "Unclassified")
    return "Unclassified"


def status_name(status_id: int) -> str:
    for s in load_lookups().get("case_statuses") or []:
        if int(s.get("id") or 0) == status_id:
            return str(s.get("name") or status_id)
    return str(status_id)


def station_district_id(station_id: int) -> int | None:
    mapping = load_lookups().get("station_district") or {}
    value = mapping.get(str(station_id))
    return int(value) if value is not None else None
