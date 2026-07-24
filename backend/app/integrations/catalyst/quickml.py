"""Catalyst QuickML — LLM Serving + RAG (catalyst.txt #11–12).

When QuickML is not configured, falls back to local RAG over
`database/seed/fir_rag_documents.json` (AppSail / hackathon demo).
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from app.core.config import Settings, get_settings
from app.core.logging import get_ai_logger

_TOKEN_RE = re.compile(r"[a-z0-9]{3,}")


def _default_rag_path() -> Path:
    # backend/app/integrations/catalyst/quickml.py → repo root
    return (
        Path(__file__).resolve().parents[4]
        / "database"
        / "seed"
        / "fir_rag_documents.json"
    )


class CatalystQuickMLClient:
    """Adapter for Catalyst QuickML LLM and RAG endpoints."""

    def __init__(self, settings: Settings | None = None) -> None:
        self._settings = settings or get_settings()
        self._logger = get_ai_logger()

    @property
    def configured(self) -> bool:
        c = self._settings.catalyst
        return bool(c.quickml_endpoint and c.rag_knowledge_base_id)

    @property
    def mock_enabled(self) -> bool:
        c = self._settings.catalyst
        return bool(getattr(c, "quickml_mock", True)) or not self.configured

    def rag_query(
        self,
        question: str,
        *,
        case_master_id: int | None = None,
        top_k: int = 5,
    ) -> dict[str, Any]:
        """Query Catalyst QuickML RAG knowledge base (or local FIR docs)."""
        self._logger.info(
            "quickml_rag_query case_master_id=%s top_k=%s configured=%s mock=%s",
            case_master_id,
            top_k,
            self.configured,
            self.mock_enabled,
        )
        if self.configured and not self.mock_enabled:
            # Live QuickML path reserved for when OAuth + endpoint are provisioned.
            raise NotImplementedError(
                "TODO: Invoke Catalyst QuickML RAG HTTP/SDK "
                "(set QUICKML_MOCK=false when endpoint is ready)"
            )
        return self._local_rag(question, case_master_id=case_master_id, top_k=top_k)

    def llm_complete(self, prompt: str, *, max_tokens: int = 512) -> str:
        _ = max_tokens
        if self.mock_enabled or not self.configured:
            return (
                "Local QuickML mock — use rag_query for grounded FIR answers. "
                f"Prompt received ({len(prompt)} chars)."
            )
        raise NotImplementedError("TODO: Invoke Catalyst QuickML LLM Serving")

    def index_document(self, document: dict[str, Any]) -> None:
        self._logger.info(
            "quickml_index_document doc_id=%s mock=%s",
            document.get("doc_id"),
            self.mock_enabled,
        )
        if self.mock_enabled or not self.configured:
            return
        raise NotImplementedError("TODO: Index document into Catalyst QuickML RAG")

    def _rag_docs_path(self) -> Path:
        configured = getattr(self._settings.catalyst, "rag_docs_path", "") or ""
        path = Path(configured) if configured else _default_rag_path()
        return path

    def _load_docs(self) -> list[dict[str, Any]]:
        path = self._rag_docs_path()
        if not path.exists():
            self._logger.warning("rag_docs_missing path=%s", path)
            return []
        raw = json.loads(path.read_text(encoding="utf-8"))
        return raw if isinstance(raw, list) else []

    def _local_rag(
        self,
        question: str,
        *,
        case_master_id: int | None,
        top_k: int,
    ) -> dict[str, Any]:
        docs = self._load_docs()
        if case_master_id is not None:
            docs = [
                d
                for d in docs
                if int(d.get("case_master_id") or 0) == case_master_id
                or str(d.get("doc_id") or "").endswith(f":{case_master_id}")
            ]
        q_tokens = set(_TOKEN_RE.findall(question.lower()))
        scored: list[tuple[float, dict[str, Any]]] = []
        for doc in docs:
            blob = str(doc.get("text_blob") or doc.get("brief_facts") or "").lower()
            tokens = set(_TOKEN_RE.findall(blob))
            if not q_tokens:
                score = 0.1
            else:
                overlap = q_tokens & tokens
                score = len(overlap) / max(len(q_tokens), 1)
                # boost crime_no / head hits
                if any(t in blob for t in q_tokens if t.isdigit() and len(t) >= 5):
                    score += 0.5
            if score > 0:
                scored.append((score, doc))
        scored.sort(key=lambda x: x[0], reverse=True)
        top = scored[:top_k]
        if not top and docs:
            top = [(0.05, d) for d in docs[:top_k]]

        citations = []
        snippets = []
        for score, doc in top:
            crime_no = str(doc.get("crime_no") or "")
            brief = str(doc.get("brief_facts") or "")[:240]
            citations.append(
                {
                    "case_master_id": doc.get("case_master_id"),
                    "crime_no": crime_no or None,
                    "doc_id": doc.get("doc_id"),
                    "snippet": brief,
                    "score": round(score, 4),
                }
            )
            snippets.append(f"- {crime_no}: {brief}")

        if snippets:
            answer = (
                "Based on indexed FIR documents (local QuickML RAG mock):\n"
                + "\n".join(snippets)
            )
        else:
            answer = (
                "No matching FIR documents found in the local RAG corpus. "
                "Seed fir_rag_documents.json and retry."
            )
        return {
            "answer": answer,
            "citations": citations,
            "provider": "catalyst_quickml_mock",
            "knowledge_base_id": "local:fir_rag_documents",
        }
