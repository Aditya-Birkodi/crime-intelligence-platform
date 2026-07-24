"""Load AppSail lookup snapshot (no Postgres)."""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

from app.core.config import get_settings


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


@lru_cache(maxsize=1)
def load_lookups() -> dict[str, Any]:
    path = lookups_path()
    if not path.exists():
        return {}
    raw = json.loads(path.read_text(encoding="utf-8"))
    return raw if isinstance(raw, dict) else {}


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
