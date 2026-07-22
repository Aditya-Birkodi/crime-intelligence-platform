"""Pydantic contracts for Catalyst QuickML chat / RAG APIs."""

from __future__ import annotations

from pydantic import BaseModel, Field


class ChatCitation(BaseModel):
    """Grounding reference returned from QuickML RAG."""

    case_master_id: int | None = None
    crime_no: str | None = None
    doc_id: str | None = None
    snippet: str | None = None


class ChatRequest(BaseModel):
    """Officer question — answered only via Catalyst QuickML RAG."""

    question: str = Field(..., min_length=1, max_length=4000)
    case_master_id: int | None = Field(
        default=None,
        description="Optional: scope retrieval to one FIR",
    )
    top_k: int = Field(default=5, ge=1, le=20)


class ChatResponse(BaseModel):
    """Answer + citations from Catalyst QuickML (never a third-party LLM)."""

    answer: str
    citations: list[ChatCitation] = Field(default_factory=list)
    provider: str = "catalyst_quickml"
    knowledge_base_id: str | None = None
