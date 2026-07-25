"""Catalyst Zia — Face Analytics, Face Comparison, OCR, objects."""

from __future__ import annotations

import tempfile
from io import BufferedReader
from pathlib import Path
from typing import Any

from app.core.config import Settings, get_settings
from app.core.logging import get_ai_logger
from app.exceptions.base import ValidationError
from app.integrations.catalyst.app_factory import (
    CatalystNotConfiguredError,
    get_catalyst_app,
)


class CatalystZiaClient:
    """Adapter for Zia Face Analytics / Comparison / OCR / objects."""

    def __init__(self, settings: Settings | None = None) -> None:
        self._settings = settings or get_settings()
        self._logger = get_ai_logger()

    @property
    def mock(self) -> bool:
        return bool(getattr(self._settings.catalyst, "zia_mock", True))

    def _as_temp_file(self, data: bytes, filename: str) -> tuple[BufferedReader, str]:
        suffix = Path(filename).suffix or ".jpg"
        with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
            tmp.write(data)
            path = tmp.name
        # SDK requires a real BufferedReader from open(); caller closes + unlinks.
        return open(path, "rb"), path  # noqa: SIM115

    def analyse_face(
        self,
        image_bytes: bytes,
        *,
        mode: str = "moderate",
        age: bool = True,
        emotion: bool = True,
        gender: bool = True,
        filename: str = "face.jpg",
    ) -> dict[str, Any]:
        """Run Zia Face Analytics (age / emotion / gender / landmarks)."""
        if not image_bytes:
            raise ValidationError("Empty image")
        self._logger.info(
            "zia_analyse_face bytes=%s mode=%s mock=%s",
            len(image_bytes),
            mode,
            self.mock,
        )
        if self.mock:
            return self._mock_analyse_face(
                mode=mode, age=age, emotion=emotion, gender=gender
            )

        path = None
        try:
            app = get_catalyst_app(self._settings)
            zia = app.zia()
            fh, path = self._as_temp_file(image_bytes, filename)
            try:
                opts = {
                    "mode": mode or "moderate",
                    "age": age,
                    "emotion": emotion,
                    "gender": gender,
                }
                result = zia.analyse_face(fh, opts)
            finally:
                fh.close()
            return dict(result) if isinstance(result, dict) else {"raw": result}
        except CatalystNotConfiguredError:
            self._logger.warning("zia_analyse_face: Catalyst not configured — mock")
            return self._mock_analyse_face(
                mode=mode, age=age, emotion=emotion, gender=gender
            )
        except Exception:
            self._logger.exception("zia_analyse_face failed — falling back to mock")
            out = self._mock_analyse_face(
                mode=mode, age=age, emotion=emotion, gender=gender
            )
            out["provider_note"] = "zia_sdk_error_fallback_mock"
            return out
        finally:
            if path:
                Path(path).unlink(missing_ok=True)

    def compare_face(
        self,
        source_bytes: bytes,
        query_bytes: bytes,
        *,
        source_name: str = "source.jpg",
        query_name: str = "query.jpg",
    ) -> dict[str, Any]:
        """Zia Face Comparison — match probe image against a gallery/source face."""
        if not source_bytes or not query_bytes:
            raise ValidationError("Both source and query images are required")
        self._logger.info(
            "zia_compare_face source=%s query=%s mock=%s",
            len(source_bytes),
            len(query_bytes),
            self.mock,
        )
        if self.mock:
            return self._mock_compare_face()

        src_path = qry_path = None
        try:
            app = get_catalyst_app(self._settings)
            zia = app.zia()
            src, src_path = self._as_temp_file(source_bytes, source_name)
            qry, qry_path = self._as_temp_file(query_bytes, query_name)
            try:
                result = zia.compare_face(src, qry)
            finally:
                src.close()
                qry.close()
            return dict(result) if isinstance(result, dict) else {"raw": result}
        except CatalystNotConfiguredError:
            return self._mock_compare_face()
        except Exception:
            self._logger.exception("zia_compare_face failed — mock fallback")
            out = self._mock_compare_face()
            out["provider_note"] = "zia_sdk_error_fallback_mock"
            return out
        finally:
            if src_path:
                Path(src_path).unlink(missing_ok=True)
            if qry_path:
                Path(qry_path).unlink(missing_ok=True)

    def detect_object(
        self, image_bytes: bytes, *, filename: str = "scene.jpg"
    ) -> dict[str, Any]:
        """Zia object detection (vehicles, weapons cues, scene tags)."""
        if not image_bytes:
            raise ValidationError("Empty image")
        if self.mock:
            return {
                "provider": "catalyst_zia_mock",
                "objects": [
                    {"name": "person", "confidence": 0.91},
                    {"name": "motorcycle", "confidence": 0.74},
                ],
            }
        path = None
        try:
            app = get_catalyst_app(self._settings)
            fh, path = self._as_temp_file(image_bytes, filename)
            try:
                result = app.zia().detect_object(fh)
            finally:
                fh.close()
            return dict(result) if isinstance(result, dict) else {"raw": result}
        except Exception:
            self._logger.exception("zia_detect_object failed")
            return {
                "provider": "catalyst_zia_mock",
                "objects": [],
                "provider_note": "zia_sdk_error_fallback_mock",
            }
        finally:
            if path:
                Path(path).unlink(missing_ok=True)

    def ocr_extract_text(
        self, image_or_pdf_bytes: bytes, *, filename: str = "doc.jpg"
    ) -> dict[str, Any]:
        """OCR scanned FIR / ID via Catalyst Zia."""
        self._logger.info(
            "zia_ocr bytes=%s mock=%s", len(image_or_pdf_bytes), self.mock
        )
        if self.mock:
            return {
                "provider": "catalyst_zia_mock",
                "text": "MOCK OCR — FIR sample text extracted from scan.",
            }
        path = None
        try:
            app = get_catalyst_app(self._settings)
            fh, path = self._as_temp_file(image_or_pdf_bytes, filename)
            try:
                result = app.zia().extract_optical_characters(fh)
            finally:
                fh.close()
            if isinstance(result, dict):
                return {"provider": "catalyst_zia", **result}
            return {"provider": "catalyst_zia", "raw": result}
        except Exception:
            self._logger.exception("zia_ocr failed")
            return {
                "provider": "catalyst_zia_mock",
                "text": "",
                "provider_note": "zia_sdk_error_fallback_mock",
            }
        finally:
            if path:
                Path(path).unlink(missing_ok=True)

    def automl_predict(self, features: dict[str, Any]) -> dict[str, Any]:
        self._logger.info("zia_automl_predict keys=%s", list(features.keys()))
        raise NotImplementedError("TODO: Invoke Catalyst Zia AutoML")

    def _mock_analyse_face(
        self,
        *,
        mode: str,
        age: bool,
        emotion: bool,
        gender: bool,
    ) -> dict[str, Any]:
        faces: list[dict[str, Any]] = [
            {
                "confidence": 0.94,
                "coordinates": {"x": 120, "y": 80, "width": 180, "height": 210},
            }
        ]
        if age:
            faces[0]["age"] = {"range": "25-34", "confidence": 0.81}
        if emotion:
            faces[0]["emotion"] = {"prediction": "neutral", "confidence": 0.72}
        if gender:
            faces[0]["gender"] = {"prediction": "male", "confidence": 0.88}
        return {
            "provider": "catalyst_zia_mock",
            "mode": mode,
            "faces": faces,
            "face_count": 1,
        }

    def _mock_compare_face(self) -> dict[str, Any]:
        return {
            "provider": "catalyst_zia_mock",
            "matched": True,
            "confidence": 0.86,
            "message": "Mock face match — use a real face photo for live Zia.",
        }
