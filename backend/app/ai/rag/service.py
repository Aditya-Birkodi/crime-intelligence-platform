"""RAG indexing via Catalyst NoSQL + QuickML.

TODO: Call from Signals Event Function when CaseMaster is written.
"""

from __future__ import annotations

from typing import Any

from app.core.config import get_settings
from app.core.logging import get_ai_logger
from app.integrations.catalyst.nosql import CatalystNoSQLClient
from app.integrations.catalyst.quickml import CatalystQuickMLClient
from etl.document_builder.pipeline import DocumentBuilderPipeline


class RagService:
    """Index FIR documents into Catalyst NoSQL + QuickML RAG KB."""

    def __init__(
        self,
        *,
        builder: DocumentBuilderPipeline | None = None,
        nosql: CatalystNoSQLClient | None = None,
        quickml: CatalystQuickMLClient | None = None,
    ) -> None:
        self._logger = get_ai_logger()
        self._builder = builder or DocumentBuilderPipeline()
        self._nosql = nosql or CatalystNoSQLClient()
        self._quickml = quickml or CatalystQuickMLClient()

    def index_case(
        self, case: dict[str, Any], *, stratus_uri: str | None = None
    ) -> dict[str, Any]:
        """Build and publish one case to Catalyst NoSQL + QuickML."""
        settings = get_settings()
        self._logger.info(
            "rag_index_case case_master_id=%s",
            case.get("case_master_id") or case.get("CaseMasterID"),
        )
        return self._builder.run_and_publish(
            case,
            nosql_client=self._nosql,
            quickml_client=self._quickml,
            stratus_uri=stratus_uri,
            nosql_table=settings.catalyst.nosql_table or None,
            rag_knowledge_base_id=settings.catalyst.rag_knowledge_base_id or None,
        )
