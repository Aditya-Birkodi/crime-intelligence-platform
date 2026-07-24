"""Pydantic contracts for Catalyst QuickML chat / Graph RAG APIs."""

from __future__ import annotations

from pydantic import BaseModel, Field

from app.schemas.ai.graph import GraphRagContext


class ChatCitation(BaseModel):
    """Grounding reference returned from QuickML RAG."""

    case_master_id: int | None = None
    crime_no: str | None = None
    doc_id: str | None = None
    snippet: str | None = None


class ChatRequest(BaseModel):
    """Officer question — QuickML RAG, optionally enriched with NetworkX graph."""

    question: str = Field(..., min_length=1, max_length=4000)
    case_master_id: int | None = Field(
        default=None,
        description="Optional: seed FIR for retrieval / Graph RAG",
    )
    accused_id: int | None = Field(
        default=None,
        description="Optional: seed accused for Graph RAG neighborhood",
    )
    use_graph_rag: bool = Field(
        default=True,
        description="Attach NetworkX ego-graph context (hosted on AppSail)",
    )
    graph_depth: int = Field(default=2, ge=1, le=3)
    top_k: int = Field(default=5, ge=1, le=20)


class ChatResponse(BaseModel):
    """Answer + citations from Catalyst QuickML (+ optional graph context)."""

    answer: str
    citations: list[ChatCitation] = Field(default_factory=list)
    provider: str = "catalyst_quickml"
    knowledge_base_id: str | None = None
    graph_context: GraphRagContext | None = None
