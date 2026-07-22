"""Catalyst QuickML — LLM Serving + RAG (catalyst.txt #11–12).

TODO: Wire official Catalyst QuickML SDK / REST once project credentials exist.
"""

from __future__ import annotations

from typing import Any

from app.core.config import Settings, get_settings
from app.core.logging import get_ai_logger


class CatalystQuickMLClient:
    """Adapter for Catalyst QuickML LLM and RAG endpoints."""

    def __init__(self, settings: Settings | None = None) -> None:
        self._settings = settings or get_settings()
        self._logger = get_ai_logger()

    @property
    def configured(self) -> bool:
        c = self._settings.catalyst
        return bool(c.quickml_endpoint and c.rag_knowledge_base_id)

    def rag_query(
        self,
        question: str,
        *,
        case_master_id: int | None = None,
        top_k: int = 5,
    ) -> dict[str, Any]:
        """Query Catalyst QuickML RAG knowledge base.

        TODO: POST to CATALYST_RAG_ENDPOINT / QuickML RAG API.
        """
        self._logger.info(
            "quickml_rag_query case_master_id=%s top_k=%s configured=%s",
            case_master_id,
            top_k,
            self.configured,
        )
        if not self.configured:
            raise NotImplementedError(
                "TODO: Set CATALYST_QUICKML_ENDPOINT and "
                "CATALYST_RAG_KNOWLEDGE_BASE_ID, then call QuickML RAG"
            )
        raise NotImplementedError("TODO: Invoke Catalyst QuickML RAG HTTP/SDK")

    def llm_complete(self, prompt: str, *, max_tokens: int = 512) -> str:
        """Catalyst QuickML LLM Serving (non-RAG).

        TODO: Prefer rag_query for FIR Q&A; use this only when KB is empty.
        """
        _ = (prompt, max_tokens)
        self._logger.info("quickml_llm_complete configured=%s", self.configured)
        raise NotImplementedError("TODO: Invoke Catalyst QuickML LLM Serving")

    def index_document(self, document: dict[str, Any]) -> None:
        """Push/update a document into the QuickML RAG knowledge base.

        TODO: Use QuickML indexing API with CATALYST_RAG_KNOWLEDGE_BASE_ID.
        """
        self._logger.info(
            "quickml_index_document doc_id=%s",
            document.get("doc_id"),
        )
        if not self.configured:
            raise NotImplementedError("TODO: Configure QuickML RAG before indexing")
        raise NotImplementedError("TODO: Index document into Catalyst QuickML RAG")
