"""Catalyst NoSQL — unstructured RAG documents (catalyst.txt #7)."""

from __future__ import annotations

from typing import Any

from app.core.config import Settings, get_settings
from app.core.logging import get_ai_logger


class CatalystNoSQLClient:
    """Adapter for Catalyst NoSQL table used as RAG document store."""

    def __init__(self, settings: Settings | None = None) -> None:
        self._settings = settings or get_settings()
        self._logger = get_ai_logger()

    @property
    def configured(self) -> bool:
        c = self._settings.catalyst
        return bool(c.nosql_table and c.nosql_endpoint)

    def upsert_rag_document(self, document: dict[str, Any]) -> None:
        """Insert or replace a RAG document by doc_id.

        TODO: Catalyst NoSQL putItem / SDK upsert.
        """
        self._logger.info(
            "nosql_upsert doc_id=%s configured=%s",
            document.get("doc_id"),
            self.configured,
        )
        if not self.configured:
            raise NotImplementedError(
                "TODO: Set CATALYST_NOSQL_TABLE and CATALYST_NOSQL_ENDPOINT"
            )
        raise NotImplementedError("TODO: Upsert into Catalyst NoSQL")

    def get_rag_document(self, doc_id: str) -> dict[str, Any] | None:
        """Fetch a RAG document by id."""
        self._logger.info("nosql_get doc_id=%s", doc_id)
        raise NotImplementedError("TODO: GetItem from Catalyst NoSQL")
