"""Catalyst QuickML — LLM Serving + RAG (catalyst.txt #11–12).

Browser must never call api.catalyst.zoho.in directly (CORS → fetch failed).
Ask AI goes: Vue → AppSail /api/v1/ai/chat → this client → QuickML GLM.

When QuickML is not configured or QUICKML_MOCK=true, falls back to local RAG over
`database/seed/fir_rag_documents.json` (AppSail / hackathon demo).
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

import httpx

from app.core.config import Settings, get_settings
from app.core.logging import get_ai_logger

_TOKEN_RE = re.compile(r"[a-z0-9]{3,}")

_DEFAULT_GLM_ENDPOINT = (
    "https://api.catalyst.zoho.in/quickml/v1/project/" "{project_id}/glm/chat"
)
_DEFAULT_MODEL = "crm-di-glm47b_30b_it"
_SYSTEM_PROMPT = (
    "You are an investigative assistant for Karnataka State Police officers. "
    "Answer using only the FIR context provided. Be concise, factual, and cite "
    "CrimeNos when relevant. If the context is insufficient, say so clearly."
)


def _default_rag_path() -> Path:
    # backend/app/integrations/catalyst/quickml.py → repo root
    return (
        Path(__file__).resolve().parents[4]
        / "database"
        / "seed"
        / "fir_rag_documents.json"
    )


class CatalystQuickMLClient:
    """Adapter for Catalyst QuickML LLM (GLM chat) and local RAG citations."""

    def __init__(self, settings: Settings | None = None) -> None:
        self._settings = settings or get_settings()
        self._logger = get_ai_logger()
        self._cached_access_token: str | None = None

    @property
    def configured(self) -> bool:
        """True when live GLM chat can be attempted (endpoint resolvable + auth)."""
        c = self._settings.catalyst
        has_endpoint = bool(c.quickml_endpoint or c.project_id)
        has_auth = bool(
            c.quickml_access_token
            or (c.refresh_token and c.client_id and c.client_secret)
        )
        return has_endpoint and has_auth

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
        """Retrieve FIR citations (local) and optionally synthesize via QuickML GLM."""
        self._logger.info(
            "quickml_rag_query case_master_id=%s top_k=%s configured=%s mock=%s",
            case_master_id,
            top_k,
            self.configured,
            self.mock_enabled,
        )
        local = self._local_rag(question, case_master_id=case_master_id, top_k=top_k)
        if self.mock_enabled:
            return local

        try:
            answer = self._glm_chat_from_rag(question, local.get("citations") or [])
            return {
                "answer": answer,
                "citations": local.get("citations") or [],
                "provider": "catalyst_quickml_glm",
                "knowledge_base_id": local.get("knowledge_base_id")
                or "local:fir_rag_documents",
            }
        except Exception:
            self._logger.exception("quickml_glm_chat_failed falling_back_to_local_rag")
            local = dict(local)
            local["provider"] = "catalyst_quickml_mock+glm_fallback"
            return local

    def llm_complete(self, prompt: str, *, max_tokens: int = 512) -> str:
        if self.mock_enabled:
            return (
                "Local QuickML mock — use rag_query for grounded FIR answers. "
                f"Prompt received ({len(prompt)} chars)."
            )
        return self._glm_chat(
            messages=[
                {"role": "system", "content": _SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
            max_tokens=max_tokens,
        )

    def index_document(self, document: dict[str, Any]) -> None:
        self._logger.info(
            "quickml_index_document doc_id=%s mock=%s",
            document.get("doc_id"),
            self.mock_enabled,
        )
        if self.mock_enabled:
            return
        # Live KB indexing is optional; Ask AI uses local FIR corpus for citations.
        self._logger.warning(
            "quickml_index_document skipped — live RAG KB indexing not configured"
        )

    def _chat_endpoint(self) -> str:
        c = self._settings.catalyst
        if c.quickml_endpoint:
            return c.quickml_endpoint.rstrip("/")
        project_id = c.project_id or "50116000000022364"
        return _DEFAULT_GLM_ENDPOINT.format(project_id=project_id)

    def _org_id(self) -> str:
        c = self._settings.catalyst
        return (c.quickml_org_id or c.org_id or "").strip()

    def _model_id(self) -> str:
        return (self._settings.catalyst.quickml_model_id or _DEFAULT_MODEL).strip()

    def _resolve_access_token(self) -> str:
        c = self._settings.catalyst
        if self._cached_access_token:
            return self._cached_access_token
        if c.quickml_access_token:
            self._cached_access_token = c.quickml_access_token.strip()
            return self._cached_access_token
        if not (c.refresh_token and c.client_id and c.client_secret):
            raise RuntimeError(
                "QuickML auth missing: set QUICKML_ACCESS_TOKEN or "
                "CATALYST_REFRESH_TOKEN + CATALYST_CLIENT_ID + CATALYST_CLIENT_SECRET"
            )
        token = self._refresh_oauth_access_token()
        self._cached_access_token = token
        return token

    def _refresh_oauth_access_token(self) -> str:
        c = self._settings.catalyst
        base = (c.oauth_accounts_url or "https://accounts.zoho.in").rstrip("/")
        url = f"{base}/oauth/v2/token"
        data = {
            "refresh_token": c.refresh_token,
            "client_id": c.client_id,
            "client_secret": c.client_secret,
            "grant_type": "refresh_token",
        }
        with httpx.Client(timeout=30.0) as client:
            res = client.post(url, data=data)
        if res.status_code >= 400:
            raise RuntimeError(
                f"OAuth token refresh failed HTTP {res.status_code}: {res.text[:300]}"
            )
        payload = res.json()
        token = payload.get("access_token")
        if not token:
            raise RuntimeError(f"OAuth response missing access_token: {payload!r}")
        return str(token)

    def _glm_chat_from_rag(self, question: str, citations: list[dict[str, Any]]) -> str:
        context_lines: list[str] = []
        for c in citations:
            crime = c.get("crime_no") or c.get("case_master_id") or "?"
            snippet = (c.get("snippet") or "").strip()
            context_lines.append(f"- CrimeNo {crime}: {snippet}")
        context = "\n".join(context_lines) if context_lines else "(no FIR snippets)"
        user_content = (
            f"Officer question:\n{question.strip()}\n\n"
            f"FIR context (use only this):\n{context}"
        )
        return self._glm_chat(
            messages=[
                {"role": "system", "content": _SYSTEM_PROMPT},
                {"role": "user", "content": user_content},
            ],
            max_tokens=700,
        )

    def _glm_chat(
        self,
        *,
        messages: list[dict[str, str]],
        max_tokens: int = 500,
        temperature: float = 0.3,
    ) -> str:
        endpoint = self._chat_endpoint()
        org = self._org_id()
        token = self._resolve_access_token()
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}",
        }
        if org:
            headers["CATALYST-ORG"] = org

        body: dict[str, Any] = {
            "model": self._model_id(),
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "stream": False,
            "chat_template_kwargs": {"enable_thinking": False},
        }

        self._logger.info(
            "quickml_glm_chat endpoint=%s model=%s org_set=%s",
            endpoint,
            body["model"],
            bool(org),
        )
        with httpx.Client(timeout=90.0) as client:
            res = client.post(endpoint, headers=headers, json=body)

        if res.status_code == 401 and self._settings.catalyst.refresh_token:
            # Access token expired — refresh once and retry.
            self._cached_access_token = None
            headers["Authorization"] = f"Bearer {self._resolve_access_token()}"
            with httpx.Client(timeout=90.0) as client:
                res = client.post(endpoint, headers=headers, json=body)

        if res.status_code >= 400:
            raise RuntimeError(f"QuickML GLM HTTP {res.status_code}: {res.text[:500]}")

        payload = res.json()
        return self._extract_assistant_text(payload)

    @staticmethod
    def _extract_assistant_text(payload: Any) -> str:
        if not isinstance(payload, dict):
            return str(payload)

        # OpenAI-style chat completion
        choices = payload.get("choices")
        if isinstance(choices, list) and choices:
            msg = choices[0].get("message") if isinstance(choices[0], dict) else None
            if isinstance(msg, dict):
                content = msg.get("content")
                if isinstance(content, str) and content.strip():
                    return content.strip()
                if isinstance(content, list):
                    parts = [
                        str(p.get("text") or p.get("content") or "")
                        for p in content
                        if isinstance(p, dict)
                    ]
                    joined = "\n".join(p for p in parts if p).strip()
                    if joined:
                        return joined

        for key in ("answer", "output", "response", "text", "content"):
            val = payload.get(key)
            if isinstance(val, str) and val.strip():
                return val.strip()

        data = payload.get("data")
        if isinstance(data, dict):
            return CatalystQuickMLClient._extract_assistant_text(data)

        return json.dumps(payload, ensure_ascii=False)[:2000]

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
