"""Graph context schemas for Graph RAG (NetworkX on AppSail)."""

from __future__ import annotations

from pydantic import BaseModel, Field


class GraphCentralNode(BaseModel):
    id: str
    type: str | None = None
    label: str | None = None
    score: float = 0.0


class GraphRagContext(BaseModel):
    """Neighborhood summary injected into QuickML / local RAG prompts."""

    seed: str
    depth: int
    node_count: int
    edge_count: int
    neighbor_crime_nos: list[str] = Field(default_factory=list)
    neighbor_case_ids: list[int] = Field(default_factory=list)
    linked_persons: list[str] = Field(default_factory=list)
    central_nodes: list[GraphCentralNode] = Field(default_factory=list)
    summary: str = ""
    engine: str = "networkx"


class GraphContextRequest(BaseModel):
    case_id: int | None = None
    accused_id: int | None = None
    depth: int = Field(default=2, ge=1, le=3)
