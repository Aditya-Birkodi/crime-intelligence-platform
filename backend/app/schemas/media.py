"""Media attachment + Zia vision response schemas."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class MediaAttachment(BaseModel):
    media_id: str
    entity_type: str = Field(
        description="case | accused | victim | complainant | probe"
    )
    entity_id: int | None = None
    case_master_id: int | None = None
    filename: str
    content_type: str
    uri: str
    size_bytes: int = 0
    label: str | None = None
    zia_face: dict[str, Any] | None = None
    created_at: str = ""


class MediaListResponse(BaseModel):
    items: list[MediaAttachment]
    total: int


class MediaUploadResponse(BaseModel):
    attachment: MediaAttachment
    face_analysis: dict[str, Any] | None = None
    provider: str = "cip_media"


class FaceAnalyseResponse(BaseModel):
    result: dict[str, Any]
    provider: str
    media_id: str | None = None


class FaceCompareResponse(BaseModel):
    result: dict[str, Any]
    provider: str
    matched: bool | None = None
    confidence: float | None = None
