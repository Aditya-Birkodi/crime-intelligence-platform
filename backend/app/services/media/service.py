"""Media registry: Stratus/local storage + optional Zia face enrich."""

from __future__ import annotations

import json
import threading
import uuid
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from app.core.config import Settings, get_settings
from app.core.logging import get_application_logger
from app.exceptions.base import NotFoundError, ValidationError
from app.integrations.catalyst.stratus import CatalystStratusClient
from app.integrations.catalyst.zia import CatalystZiaClient
from app.schemas.media import MediaAttachment, MediaUploadResponse


class MediaService:
    def __init__(self, settings: Settings | None = None) -> None:
        self._settings = settings or get_settings()
        self._logger = get_application_logger()
        self._stratus = CatalystStratusClient(self._settings)
        self._zia = CatalystZiaClient(self._settings)
        self._lock = threading.Lock()
        media_root = Path(
            self._settings.catalyst.media_path
            if hasattr(self._settings.catalyst, "media_path")
            else ".data/media"
        )
        # Prefer /tmp on AppSail when default relative path may be read-only
        if str(media_root) == ".data/media":
            try:
                media_root.mkdir(parents=True, exist_ok=True)
            except OSError:
                media_root = Path("/tmp/cip-media")
                media_root.mkdir(parents=True, exist_ok=True)
        else:
            media_root.mkdir(parents=True, exist_ok=True)
        self._root = media_root
        self._index_path = media_root / "index.json"

    def _load_index(self) -> list[dict[str, Any]]:
        if not self._index_path.is_file():
            return []
        try:
            raw = json.loads(self._index_path.read_text(encoding="utf-8"))
            if isinstance(raw, list):
                return [r for r in raw if isinstance(r, dict)]
            return []
        except Exception:
            return []

    def _save_index(self, rows: list[dict[str, Any]]) -> None:
        self._index_path.parent.mkdir(parents=True, exist_ok=True)
        self._index_path.write_text(
            json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8"
        )

    def list_media(
        self,
        *,
        case_master_id: int | None = None,
        entity_type: str | None = None,
        entity_id: int | None = None,
        limit: int = 50,
    ) -> list[MediaAttachment]:
        rows = self._load_index()
        out: list[MediaAttachment] = []
        for r in reversed(rows):
            if case_master_id is not None and r.get("case_master_id") != case_master_id:
                continue
            if entity_type and r.get("entity_type") != entity_type:
                continue
            if entity_id is not None and r.get("entity_id") != entity_id:
                continue
            out.append(MediaAttachment.model_validate(r))
            if len(out) >= limit:
                break
        return out

    def get(self, media_id: str) -> MediaAttachment:
        for r in self._load_index():
            if r.get("media_id") == media_id:
                return MediaAttachment.model_validate(r)
        raise NotFoundError(f"Media {media_id} not found")

    def get_bytes(self, media_id: str) -> tuple[bytes, str, str]:
        att = self.get(media_id)
        data = self._stratus.download_bytes(att.uri)
        return data, att.content_type, att.filename

    def upload(
        self,
        data: bytes,
        *,
        filename: str,
        content_type: str,
        entity_type: str = "probe",
        entity_id: int | None = None,
        case_master_id: int | None = None,
        label: str | None = None,
        analyse_face: bool = False,
        face_mode: str = "moderate",
    ) -> MediaUploadResponse:
        if not data:
            raise ValidationError("Empty file")
        if len(data) > 8 * 1024 * 1024:
            raise ValidationError("Image too large (max 8 MB)")
        allowed = {
            "image/jpeg",
            "image/jpg",
            "image/png",
            "image/webp",
            "application/octet-stream",
        }
        ct = (content_type or "application/octet-stream").lower()
        if ct not in allowed and not ct.startswith("image/"):
            raise ValidationError("Only image uploads are supported (jpeg/png/webp)")

        media_id = uuid.uuid4().hex[:16]
        safe_name = (
            "".join(c if c.isalnum() or c in "._-" else "_" for c in filename)[:80]
            or "upload.jpg"
        )
        key = f"cip/{entity_type}/{entity_id or 0}/{media_id}_{safe_name}"
        uri = self._stratus.upload_bytes(key, data, content_type=ct or "image/jpeg")

        face_result: dict[str, Any] | None = None
        if analyse_face:
            face_result = self._zia.analyse_face(
                data, mode=face_mode, filename=safe_name
            )

        now = datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
        row = {
            "media_id": media_id,
            "entity_type": entity_type,
            "entity_id": entity_id,
            "case_master_id": case_master_id,
            "filename": safe_name,
            "content_type": ct if ct != "application/octet-stream" else "image/jpeg",
            "uri": uri,
            "size_bytes": len(data),
            "label": label,
            "zia_face": face_result,
            "created_at": now,
        }
        with self._lock:
            rows = self._load_index()
            rows.append(row)
            self._save_index(rows)

        return MediaUploadResponse(
            attachment=MediaAttachment.model_validate(row),
            face_analysis=face_result,
            provider="cip_media",
        )

    def attach_face_analysis(
        self, media_id: str, face: dict[str, Any]
    ) -> MediaAttachment:
        with self._lock:
            rows = self._load_index()
            for r in rows:
                if r.get("media_id") == media_id:
                    r["zia_face"] = face
                    self._save_index(rows)
                    return MediaAttachment.model_validate(r)
        raise NotFoundError(f"Media {media_id} not found")
