"""Catalyst Stratus — FIR PDFs / scans / exports (catalyst.txt #8)."""

from __future__ import annotations

from app.core.config import Settings, get_settings
from app.core.logging import get_ai_logger


class CatalystStratusClient:
    """S3-style object storage via Catalyst Stratus."""

    def __init__(self, settings: Settings | None = None) -> None:
        self._settings = settings or get_settings()
        self._logger = get_ai_logger()

    @property
    def configured(self) -> bool:
        c = self._settings.catalyst
        return bool(c.stratus_bucket)

    def upload_bytes(self, key: str, data: bytes, *, content_type: str) -> str:
        """Upload object; return Stratus URI.

        TODO: Catalyst Stratus put object SDK.
        """
        self._logger.info(
            "stratus_upload key=%s bytes=%s configured=%s",
            key,
            len(data),
            self.configured,
        )
        if not self.configured:
            raise NotImplementedError("TODO: Set CATALYST_STRATUS_BUCKET")
        raise NotImplementedError("TODO: Upload to Catalyst Stratus")

    def download_bytes(self, key: str) -> bytes:
        """Download object bytes for OCR / document_builder."""
        self._logger.info("stratus_download key=%s", key)
        raise NotImplementedError("TODO: Download from Catalyst Stratus")
