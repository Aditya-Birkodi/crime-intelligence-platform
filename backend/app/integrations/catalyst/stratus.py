"""Catalyst Stratus — FIR scans / person photos (with local fallback)."""

from __future__ import annotations

import io
from pathlib import Path

from app.core.config import Settings, get_settings
from app.core.logging import get_ai_logger
from app.integrations.catalyst.app_factory import (
    CatalystNotConfiguredError,
    get_catalyst_app,
)


class CatalystStratusClient:
    """S3-style object storage via Catalyst Stratus + local disk fallback."""

    def __init__(self, settings: Settings | None = None) -> None:
        self._settings = settings or get_settings()
        self._logger = get_ai_logger()

    @property
    def configured(self) -> bool:
        return bool(self._settings.catalyst.stratus_bucket)

    @property
    def _local_root(self) -> Path:
        root = Path(
            getattr(self._settings.catalyst, "media_path", None) or ".data/media"
        )
        root.mkdir(parents=True, exist_ok=True)
        return root

    def upload_bytes(self, key: str, data: bytes, *, content_type: str) -> str:
        """Upload object; return stratus:// or local:// URI."""
        self._logger.info(
            "stratus_upload key=%s bytes=%s configured=%s",
            key,
            len(data),
            self.configured,
        )
        safe_key = key.lstrip("/").replace("..", "_")
        if self.configured:
            try:
                app = get_catalyst_app(self._settings)
                bucket_name = self._settings.catalyst.stratus_bucket
                bucket = app.stratus().bucket(bucket_name)
                buf = io.BytesIO(data)
                buf.name = safe_key.split("/")[-1]
                options = {
                    "overwrite": "true",
                    "content-type": content_type,
                }
                bucket.put_object(safe_key, buf, options)
                return f"stratus://{bucket_name}/{safe_key}"
            except CatalystNotConfiguredError:
                self._logger.warning(
                    "stratus: Catalyst not configured — local fallback"
                )
            except Exception:
                self._logger.exception("stratus_upload failed — local fallback")

        path = self._local_root / safe_key
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
        return f"local://{safe_key}"

    def download_bytes(self, uri_or_key: str) -> bytes:
        """Download object bytes from Stratus URI or local key."""
        self._logger.info("stratus_download key=%s", uri_or_key)
        if uri_or_key.startswith("local://"):
            key = uri_or_key.removeprefix("local://")
            path = self._local_root / key
            if not path.is_file():
                raise FileNotFoundError(uri_or_key)
            return path.read_bytes()

        key = uri_or_key
        bucket_name = self._settings.catalyst.stratus_bucket
        if uri_or_key.startswith("stratus://"):
            rest = uri_or_key.removeprefix("stratus://")
            bucket_name, _, key = rest.partition("/")
        if not bucket_name:
            # try local
            path = self._local_root / key.lstrip("/")
            if path.is_file():
                return path.read_bytes()
            raise FileNotFoundError(uri_or_key)

        app = get_catalyst_app(self._settings)
        bucket = app.stratus().bucket(bucket_name)
        # SDK get_object patterns vary — try common shapes
        try:
            obj = bucket.get_object(key)
            if isinstance(obj, bytes | bytearray):
                return bytes(obj)
            if hasattr(obj, "read"):
                raw = obj.read()
                return raw if isinstance(raw, bytes) else bytes(raw)
            if isinstance(obj, dict) and "content" in obj:
                content = obj["content"]
                return content if isinstance(content, bytes) else bytes(content)
        except Exception:
            self._logger.exception("stratus_download SDK path failed")
        # local mirror fallback
        path = self._local_root / key
        if path.is_file():
            return path.read_bytes()
        raise FileNotFoundError(uri_or_key)
