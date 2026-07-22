"""Officer chat via Catalyst QuickML RAG only.

TODO: Mount POST /api/v1/ai/chat when FS B is ready; keep provider=catalyst_quickml.
"""

from __future__ import annotations

from app.core.logging import get_ai_logger
from app.integrations.catalyst.quickml import CatalystQuickMLClient
from app.schemas.ai.chat import ChatRequest, ChatResponse


class ChatService:
    """Placeholder for `chat` AI capability — QuickML-backed."""

    def __init__(self, quickml: CatalystQuickMLClient | None = None) -> None:
        self._logger = get_ai_logger()
        self._quickml = quickml or CatalystQuickMLClient()

    def run(self, request: ChatRequest) -> ChatResponse:
        """Answer using Catalyst QuickML RAG (not OpenAI/etc.)."""
        self._logger.info(
            "chat_run case_master_id=%s",
            request.case_master_id,
        )
        raw = self._quickml.rag_query(
            request.question,
            case_master_id=request.case_master_id,
            top_k=request.top_k,
        )
        # TODO: Map QuickML response JSON → ChatResponse
        return ChatResponse(
            answer=str(raw.get("answer", "")),
            citations=[],
            provider="catalyst_quickml",
            knowledge_base_id=None,
        )
