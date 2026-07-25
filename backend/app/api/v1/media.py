"""Media upload / gallery + Zia vision helpers."""

from __future__ import annotations

import base64
import binascii
from typing import Annotated, Any

from fastapi import APIRouter, Depends, File, Form, Query, UploadFile
from fastapi.responses import Response
from pydantic import BaseModel

from app.exceptions.base import ValidationError
from app.integrations.catalyst.zia import CatalystZiaClient
from app.schemas.media import (
    FaceAnalyseResponse,
    FaceCompareResponse,
    MediaListResponse,
    MediaUploadResponse,
)
from app.services.media.service import MediaService

router = APIRouter(prefix="/media", tags=["media"])


def _media() -> MediaService:
    return MediaService()


def _zia() -> CatalystZiaClient:
    return CatalystZiaClient()


def _decode_b64(data: str) -> bytes:
    raw = data.strip()
    if "," in raw and raw.lower().startswith("data:"):
        raw = raw.split(",", 1)[1]
    try:
        return base64.b64decode(raw, validate=False)
    except binascii.Error as exc:
        raise ValidationError("Invalid base64 image") from exc


class AnalyseFaceJsonRequest(BaseModel):
    image_base64: str
    filename: str = "face.jpg"
    mode: str = "moderate"
    age: bool = True
    emotion: bool = True
    gender: bool = True
    persist: bool = False
    case_master_id: int | None = None
    entity_type: str = "probe"
    entity_id: int | None = None


class CompareFaceJsonRequest(BaseModel):
    source_base64: str
    query_base64: str
    source_filename: str = "source.jpg"
    query_filename: str = "query.jpg"


class UploadMediaJsonRequest(BaseModel):
    image_base64: str
    filename: str = "upload.jpg"
    content_type: str = "image/jpeg"
    entity_type: str = "probe"
    entity_id: int | None = None
    case_master_id: int | None = None
    label: str | None = None
    analyse_face: bool = False
    face_mode: str = "moderate"


@router.get("", response_model=MediaListResponse)
def list_media(
    service: Annotated[MediaService, Depends(_media)],
    case_master_id: int | None = None,
    entity_type: str | None = None,
    entity_id: int | None = None,
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
) -> MediaListResponse:
    items = service.list_media(
        case_master_id=case_master_id,
        entity_type=entity_type,
        entity_id=entity_id,
        limit=limit,
    )
    return MediaListResponse(items=items, total=len(items))


@router.get("/{media_id}/content")
def media_content(
    media_id: str,
    service: Annotated[MediaService, Depends(_media)],
) -> Response:
    data, content_type, filename = service.get_bytes(media_id)
    return Response(
        content=data,
        media_type=content_type or "application/octet-stream",
        headers={"Content-Disposition": f'inline; filename="{filename}"'},
    )


@router.post("/upload", response_model=MediaUploadResponse)
async def upload_media(
    service: Annotated[MediaService, Depends(_media)],
    file: UploadFile = File(...),
    entity_type: str = Form("probe"),
    entity_id: int | None = Form(None),
    case_master_id: int | None = Form(None),
    label: str | None = Form(None),
    analyse_face: bool = Form(False),
    face_mode: str = Form("moderate"),
) -> MediaUploadResponse:
    data = await file.read()
    return service.upload(
        data,
        filename=file.filename or "upload.jpg",
        content_type=file.content_type or "image/jpeg",
        entity_type=entity_type,
        entity_id=entity_id,
        case_master_id=case_master_id,
        label=label,
        analyse_face=analyse_face,
        face_mode=face_mode,
    )


@router.post("/upload-json", response_model=MediaUploadResponse)
def upload_media_json(
    payload: UploadMediaJsonRequest,
    service: Annotated[MediaService, Depends(_media)],
) -> MediaUploadResponse:
    """Base64 upload (Slate-safe: text/plain JSON, no multipart preflight)."""
    data = _decode_b64(payload.image_base64)
    return service.upload(
        data,
        filename=payload.filename,
        content_type=payload.content_type,
        entity_type=payload.entity_type,
        entity_id=payload.entity_id,
        case_master_id=payload.case_master_id,
        label=payload.label,
        analyse_face=payload.analyse_face,
        face_mode=payload.face_mode,
    )


@router.post("/zia/analyse-face", response_model=FaceAnalyseResponse)
async def analyse_face(
    zia: Annotated[CatalystZiaClient, Depends(_zia)],
    media: Annotated[MediaService, Depends(_media)],
    file: UploadFile = File(...),
    mode: str = Form("moderate"),
    age: bool = Form(True),
    emotion: bool = Form(True),
    gender: bool = Form(True),
    persist: bool = Form(False),
    case_master_id: int | None = Form(None),
    entity_type: str = Form("probe"),
    entity_id: int | None = Form(None),
) -> FaceAnalyseResponse:
    """Zia Face Analytics — age, emotion, gender, landmarks."""
    data = await file.read()
    if not data:
        raise ValidationError("Empty image")
    result = zia.analyse_face(
        data,
        mode=mode,
        age=age,
        emotion=emotion,
        gender=gender,
        filename=file.filename or "face.jpg",
    )
    media_id = None
    if persist:
        up = media.upload(
            data,
            filename=file.filename or "face.jpg",
            content_type=file.content_type or "image/jpeg",
            entity_type=entity_type,
            entity_id=entity_id,
            case_master_id=case_master_id,
            label="face_probe",
            analyse_face=False,
        )
        media.attach_face_analysis(up.attachment.media_id, result)
        media_id = up.attachment.media_id
    provider = str(result.get("provider") or "catalyst_zia")
    return FaceAnalyseResponse(result=result, provider=provider, media_id=media_id)


@router.post("/zia/analyse-face-json", response_model=FaceAnalyseResponse)
def analyse_face_json(
    payload: AnalyseFaceJsonRequest,
    zia: Annotated[CatalystZiaClient, Depends(_zia)],
    media: Annotated[MediaService, Depends(_media)],
) -> FaceAnalyseResponse:
    data = _decode_b64(payload.image_base64)
    if not data:
        raise ValidationError("Empty image")
    result = zia.analyse_face(
        data,
        mode=payload.mode,
        age=payload.age,
        emotion=payload.emotion,
        gender=payload.gender,
        filename=payload.filename,
    )
    media_id = None
    if payload.persist:
        up = media.upload(
            data,
            filename=payload.filename,
            content_type="image/jpeg",
            entity_type=payload.entity_type,
            entity_id=payload.entity_id,
            case_master_id=payload.case_master_id,
            label="face_probe",
            analyse_face=False,
        )
        media.attach_face_analysis(up.attachment.media_id, result)
        media_id = up.attachment.media_id
    return FaceAnalyseResponse(
        result=result,
        provider=str(result.get("provider") or "catalyst_zia"),
        media_id=media_id,
    )


@router.post("/zia/compare-face", response_model=FaceCompareResponse)
async def compare_face(
    zia: Annotated[CatalystZiaClient, Depends(_zia)],
    source: UploadFile = File(..., description="Gallery / known face"),
    query: UploadFile = File(..., description="Probe / CCTV crop"),
) -> FaceCompareResponse:
    """Zia Face Comparison — match two faces (recognition)."""
    src = await source.read()
    qry = await query.read()
    result = zia.compare_face(
        src,
        qry,
        source_name=source.filename or "source.jpg",
        query_name=query.filename or "query.jpg",
    )
    return _compare_response(result)


@router.post("/zia/compare-face-json", response_model=FaceCompareResponse)
def compare_face_json(
    payload: CompareFaceJsonRequest,
    zia: Annotated[CatalystZiaClient, Depends(_zia)],
) -> FaceCompareResponse:
    result = zia.compare_face(
        _decode_b64(payload.source_base64),
        _decode_b64(payload.query_base64),
        source_name=payload.source_filename,
        query_name=payload.query_filename,
    )
    return _compare_response(result)


def _compare_response(result: dict[str, Any]) -> FaceCompareResponse:
    matched: bool | None = None
    confidence: float | None = None
    if isinstance(result, dict):
        if "matched" in result:
            matched = bool(result["matched"])
        elif "match" in result:
            matched = bool(result["match"])
        conf = result.get("confidence") or result.get("score")
        try:
            confidence = float(conf) if conf is not None else None
        except (TypeError, ValueError):
            confidence = None
    return FaceCompareResponse(
        result=result,
        provider=str(result.get("provider") or "catalyst_zia"),
        matched=matched,
        confidence=confidence,
    )


@router.post("/zia/detect-objects")
async def detect_objects(
    zia: Annotated[CatalystZiaClient, Depends(_zia)],
    file: UploadFile = File(...),
) -> dict[str, Any]:
    data = await file.read()
    return zia.detect_object(data, filename=file.filename or "scene.jpg")


@router.post("/zia/detect-objects-json")
def detect_objects_json(
    payload: dict[str, Any],
    zia: Annotated[CatalystZiaClient, Depends(_zia)],
) -> dict[str, Any]:
    b64 = str(payload.get("image_base64") or "")
    return zia.detect_object(
        _decode_b64(b64),
        filename=str(payload.get("filename") or "scene.jpg"),
    )


@router.post("/zia/ocr")
async def ocr_image(
    zia: Annotated[CatalystZiaClient, Depends(_zia)],
    file: UploadFile = File(...),
) -> dict[str, Any]:
    data = await file.read()
    return zia.ocr_extract_text(data, filename=file.filename or "doc.jpg")


@router.post("/zia/ocr-json")
def ocr_json(
    payload: dict[str, Any],
    zia: Annotated[CatalystZiaClient, Depends(_zia)],
) -> dict[str, Any]:
    return zia.ocr_extract_text(
        _decode_b64(str(payload.get("image_base64") or "")),
        filename=str(payload.get("filename") or "doc.jpg"),
    )
