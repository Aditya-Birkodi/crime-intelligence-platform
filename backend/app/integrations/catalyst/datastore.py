"""Catalyst Data Store + ZCQL thin client.

Resolve tables by:
  1. CATALYST_TABLE_* IDs from console (preferred), or
  2. name = CATALYST_DATASTORE_TABLE_PREFIX + logical (e.g. cip_case_master)

When CATALYST_DATASTORE_MOCK=true, uses a local JSON file store.
"""

from __future__ import annotations

import json
import threading
from pathlib import Path
from typing import Any

from app.core.config import Settings, get_settings
from app.core.logging import get_application_logger
from app.integrations.catalyst.app_factory import get_catalyst_app

# logical key → Settings field holding optional Table ID
_TABLE_ID_FIELDS = {
    "case_master": "table_case_master",
    "cip_case_master": "table_case_master",
    "victim": "table_victim",
    "cip_victim": "table_victim",
    "accused": "table_accused",
    "cip_accused": "table_accused",
    "act_section_association": "table_act_section",
    "cip_act_section_association": "table_act_section",
}


class CatalystDataStoreClient:
    """High-level Data Store operations used by CaseStore."""

    def __init__(self, settings: Settings | None = None) -> None:
        self._settings = settings or get_settings()
        self._logger = get_application_logger()
        self._prefix = self._settings.catalyst.datastore_table_prefix
        self._mock = self._settings.catalyst.datastore_mock
        self._lock = threading.Lock()
        self._mock_path = Path(
            self._settings.catalyst.datastore_mock_path
            or ".data/catalyst_datastore.json"
        )

    def table_ref(self, table: str) -> str | int:
        """Return Table ID if configured, else table name string."""
        cat = self._settings.catalyst
        field = _TABLE_ID_FIELDS.get(table) or _TABLE_ID_FIELDS.get(
            table.removeprefix(self._prefix)
        )
        if field:
            table_id = getattr(cat, field, "") or ""
            if str(table_id).strip():
                raw = str(table_id).strip()
                return int(raw) if raw.isdigit() else raw
        return self.table_name(table)

    def table_name(self, logical: str) -> str:
        """logical e.g. 'case_master' → 'cip_case_master'."""
        if logical.startswith(self._prefix):
            return logical
        return f"{self._prefix}{logical}"

    def _table_service(self, table: str) -> Any:
        ref = self.table_ref(table)
        app = get_catalyst_app(self._settings)
        self._logger.info("datastore_table ref=%s (logical=%s)", ref, table)
        return app.datastore().table(ref)

    def insert_row(self, table: str, row: dict[str, Any]) -> dict[str, Any]:
        if self._mock:
            return self._mock_insert(self.table_name(table), row)
        table_svc = self._table_service(table)
        return dict(table_svc.insert_row(row))

    def get_row(self, table: str, row_id: int | str) -> dict[str, Any] | None:
        if self._mock:
            return self._mock_get(self.table_name(table), int(row_id))
        table_svc = self._table_service(table)
        try:
            return dict(table_svc.get_row(int(row_id)))
        except Exception:
            self._logger.exception(
                "datastore_get_row failed table=%s id=%s", table, row_id
            )
            return None

    def get_paged_rows(
        self, table: str, *, max_rows: int = 200
    ) -> list[dict[str, Any]]:
        if self._mock:
            return self._mock_all(self.table_name(table))[:max_rows]
        table_svc = self._table_service(table)
        rows: list[dict[str, Any]] = []
        next_token = None
        more = True
        while more and len(rows) < max_rows:
            page = table_svc.get_paged_rows(
                next_token, max_rows=min(100, max_rows - len(rows))
            )
            batch = page.get("content") or page.get("data") or page.get("rows") or []
            if isinstance(batch, list):
                rows.extend(dict(r) for r in batch)
            more = bool(page.get("more_records"))
            next_token = page.get("next_token")
            if not more:
                break
        return rows

    def zcql(self, query: str) -> list[dict[str, Any]]:
        """Execute ZCQL. Returns flattened row dicts when possible."""
        if self._mock:
            return self._mock_zcql_unsupported(query)
        app = get_catalyst_app(self._settings)
        raw = app.zcql().execute_query(query)
        self._logger.info("zcql rows=%s", len(raw) if isinstance(raw, list) else "?")
        if not isinstance(raw, list):
            return []
        flat: list[dict[str, Any]] = []
        for item in raw:
            if isinstance(item, dict) and len(item) == 1:
                flat.append(dict(next(iter(item.values()))))
            elif isinstance(item, dict):
                flat.append(dict(item))
        return flat

    def _mock_load(self) -> dict[str, Any]:
        if not self._mock_path.exists():
            return {"seq": 1, "tables": {}}
        data = json.loads(self._mock_path.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {"seq": 1, "tables": {}}

    def _mock_save(self, data: dict[str, Any]) -> None:
        self._mock_path.parent.mkdir(parents=True, exist_ok=True)
        self._mock_path.write_text(
            json.dumps(data, indent=2, default=str), encoding="utf-8"
        )

    def _mock_insert(self, table: str, row: dict[str, Any]) -> dict[str, Any]:
        with self._lock:
            data = self._mock_load()
            tables: dict[str, list[dict[str, Any]]] = data.setdefault("tables", {})
            seq = int(data.get("seq", 1))
            stored = {"ROWID": seq, **row}
            tables.setdefault(table, []).append(stored)
            data["seq"] = seq + 1
            self._mock_save(data)
            return stored

    def _mock_get(self, table: str, row_id: int) -> dict[str, Any] | None:
        with self._lock:
            data = self._mock_load()
            for row in data.get("tables", {}).get(table, []):
                if int(row.get("ROWID", -1)) == row_id:
                    return dict(row)
            return None

    def _mock_all(self, table: str) -> list[dict[str, Any]]:
        with self._lock:
            data = self._mock_load()
            return [dict(r) for r in data.get("tables", {}).get(table, [])]

    def _mock_zcql_unsupported(self, query: str) -> list[dict[str, Any]]:
        self._logger.debug("mock_zcql ignored: %s", query[:120])
        return []
