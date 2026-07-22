# Getting started — AI engineer (Catalyst-first)

## Day 1 checklist

- [ ] **Catalyst console setup** — follow [`../deployment/catalyst_console_setup.md`](../deployment/catalyst_console_setup.md) (create project → NoSQL → Stratus → QuickML RAG)
- [ ] Catalyst project access (Dev env)
- [ ] Enable / note IDs for: **QuickML**, **NoSQL**, **Stratus**, **Cache**, **Signals**, **Zia**
- [ ] Copy values into `.env` from `.env.example` (`CATALYST_QUICKML_*`, `CATALYST_RAG_*`, `CATALYST_NOSQL_*`, `CATALYST_STRATUS_*`, …)
- [ ] Prove RAG works **in the Catalyst web UI** (upload sample FIR text → ask a question) before coding the client
- [ ] Run local API: `uv run uvicorn backend.main:app --reload --app-dir .`
- [ ] Read adapters under `backend/app/integrations/catalyst/`

## First PR (do this next)

1. **Document builder** — `etl/document_builder`: FIR case dict → RAG document (`docs/ai/rag_document_schema.md`).
2. **NoSQL upsert stub** — `CatalystNoSQLClient.upsert_rag_document` (real SDK when available).
3. **QuickML chat stub** — `CatalystQuickMLClient.rag_query` used by `backend/app/ai/chat`.
4. **Schemas** — `backend/app/schemas/ai/` ChatRequest / ChatResponse with `citations`.
5. **Tests** — mock Catalyst clients; never call third-party LLMs in CI.

## Demo path (target)

```text
CaseMaster (Data Store)
    → document_builder
    → Stratus (optional PDF) + NoSQL document
    → QuickML RAG knowledge base
    → POST /api/v1/ai/chat  (API Gateway + Auth)
    → Case detail "Ask AI" (FS B)
```

Reindex: **Signals** on case insert/update → Event Function → document_builder.

## Forbidden for submission-critical paths

OpenAI / Anthropic / Gemini APIs, Pinecone, Weaviate, cloud OCR vendors, S3 as primary blob store,
self-hosted vector DB as the production RAG store.

Local fakes/mocks in unit tests are fine.
