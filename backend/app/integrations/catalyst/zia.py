"""Catalyst Zia — OCR, AutoML, vision, speech (catalyst.txt #13–15)."""

from __future__ import annotations

from typing import Any

from app.core.config import Settings, get_settings
from app.core.logging import get_ai_logger


class CatalystZiaClient:
    """Adapter for Zia Services + Zia AutoML."""

    def __init__(self, settings: Settings | None = None) -> None:
        self._settings = settings or get_settings()
        self._logger = get_ai_logger()

    def ocr_extract_text(self, image_or_pdf_bytes: bytes) -> str:
        """OCR scanned FIR via Catalyst Zia (not Tesseract-in-prod).

        TODO: Call CATALYST_ZIA_ENDPOINT OCR API.
        """
        self._logger.info("zia_ocr bytes=%s", len(image_or_pdf_bytes))
        raise NotImplementedError("TODO: Invoke Catalyst Zia OCR")

    def automl_predict(self, features: dict[str, Any]) -> dict[str, Any]:
        """Tabular prediction via Zia AutoML / QuickML trained model.

        TODO: Call CATALYST_ZIA_AUTOML_ENDPOINT with model id.
        """
        self._logger.info("zia_automl_predict keys=%s", list(features.keys()))
        raise NotImplementedError("TODO: Invoke Catalyst Zia AutoML")
