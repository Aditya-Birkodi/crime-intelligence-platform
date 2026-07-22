"""Catalyst SmartBrowz — PDF / HTML reports (catalyst.txt #16)."""

from __future__ import annotations

from typing import Any

from app.core.config import Settings, get_settings
from app.core.logging import get_ai_logger


class CatalystSmartBrowzClient:
    """Generate case summary PDFs via SmartBrowz templates."""

    def __init__(self, settings: Settings | None = None) -> None:
        self._settings = settings or get_settings()
        self._logger = get_ai_logger()

    def render_case_report(self, case_payload: dict[str, Any]) -> bytes:
        """Render PDF bytes for a case dossier.

        TODO: Call CATALYST_SMARTBROWZ_ENDPOINT with template id.
        """
        self._logger.info(
            "smartbrowz_render case_master_id=%s",
            case_payload.get("case_master_id"),
        )
        raise NotImplementedError("TODO: Invoke Catalyst SmartBrowz")
