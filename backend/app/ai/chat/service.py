"""Officer chat via Catalyst QuickML RAG + optional NetworkX Graph RAG."""

from __future__ import annotations

from app.ai.graph.service import GraphService
from app.core.logging import get_ai_logger
from app.integrations.catalyst.quickml import CatalystQuickMLClient
from app.repositories.case.case_store import CaseStore
from app.schemas.ai.chat import ChatCitation, ChatRequest, ChatResponse
from app.schemas.ai.graph import GraphRagContext


class ChatService:
    """QuickML-backed FIR Q&A with optional in-process Graph RAG."""

    def __init__(
        self,
        store: CaseStore,
        quickml: CatalystQuickMLClient | None = None,
    ) -> None:
        self._logger = get_ai_logger()
        self._quickml = quickml or CatalystQuickMLClient()
        self._graph = GraphService(store)

    def run(self, request: ChatRequest) -> ChatResponse:
        self._logger.info(
            "chat_run case_master_id=%s accused_id=%s graph=%s",
            request.case_master_id,
            request.accused_id,
            request.use_graph_rag,
        )

        graph_ctx: GraphRagContext | None = None
        question = request.question
        if request.use_graph_rag and (
            request.case_master_id is not None or request.accused_id is not None
        ):
            try:
                graph_ctx = self._graph.context(
                    case_id=request.case_master_id,
                    accused_id=request.accused_id,
                    depth=request.graph_depth,
                )
                question = (
                    f"{request.question.strip()}\n\n"
                    f"[Graph RAG neighborhood — NetworkX on Catalyst AppSail]\n"
                    f"{graph_ctx.summary}"
                )
            except Exception:
                self._logger.exception("graph_rag_context_failed")
                graph_ctx = None

        # When graph neighborhood is available, search the full corpus (tokens
        # include linked CrimeNos) instead of locking to a single case id.
        scope_case_id = request.case_master_id
        if graph_ctx and graph_ctx.neighbor_case_ids:
            scope_case_id = None

        raw = self._quickml.rag_query(
            question,
            case_master_id=scope_case_id,
            top_k=request.top_k,
        )
        citations = [
            ChatCitation(
                case_master_id=c.get("case_master_id"),
                crime_no=c.get("crime_no"),
                doc_id=c.get("doc_id"),
                snippet=c.get("snippet"),
            )
            for c in (raw.get("citations") or [])
            if isinstance(c, dict)
        ]

        provider = str(raw.get("provider") or "catalyst_quickml")
        if graph_ctx:
            provider = f"{provider}+graph_rag"

        answer = str(raw.get("answer", ""))
        if graph_ctx and graph_ctx.neighbor_crime_nos:
            answer = (
                f"{answer}\n\n"
                f"— Graph links used: {', '.join(graph_ctx.neighbor_crime_nos[:8])}"
            )

        return ChatResponse(
            answer=answer,
            citations=citations,
            provider=provider,
            knowledge_base_id=raw.get("knowledge_base_id"),
            graph_context=graph_ctx,
        )
