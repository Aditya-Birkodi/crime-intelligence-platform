# AI Subsystem — Catalyst-first

**Rule:** Prefer Zoho Catalyst for every AI/data capability. Third-party LLMs, vector DBs,
S3 clones, or Redis-as-prod-cache may invalidate the hackathon submission when a Catalyst
service already exists (`catalyst.txt`).

## Capability → Catalyst (mandatory)

| Your feature | Use this | Do **not** use |
|--------------|----------|----------------|
| Officer Q&A / LLM | **QuickML** LLM Serving | OpenAI, Gemini, local Ollama (prod) |
| RAG / knowledge base | **QuickML** RAG | Pinecone, Chroma, FAISS-as-prod |
| FIR / BriefFacts documents | **NoSQL** (+ RAG index) | MongoDB Atlas, Elastic |
| Scanned FIR PDF / images | **Stratus** object store | AWS S3, MinIO (prod) |
| OCR on scans | **Zia** Services | Tesseract/cloud OCR vendors |
| Tabular prediction | **Zia AutoML** / QuickML | sklearn-only prod serving |
| Case PDF / report | **SmartBrowz** | WeasyPrint-only prod path |
| Reindex on case update | **Signals** + Event Function | custom webhooks only |
| ETL orchestration | **Circuits** | Airflow/Prefect (prod) |
| Nightly reindex | **Cron** / Job Scheduling | system cron on a VM |
| Auth for AI routes | **Authentication** + **API Gateway** | custom JWT-only prod |
| Hot prompt/result cache | **Cache** | prod Redis (local Redis OK for dev) |

Local Postgres/Redis remain **dev mirrors** only.

## Packages

| Path | Catalyst target |
|------|-----------------|
| `backend/app/ai/chat` | QuickML LLM |
| `backend/app/ai/rag` | QuickML RAG + NoSQL docs |
| `backend/app/ai/prediction` | Zia AutoML / QuickML |
| `backend/app/ai/analytics` | Data Store queries (via FS A APIs) + Cache |
| `backend/app/ai/graph` | Derived from Data Store (optional) |
| `backend/app/integrations/catalyst/` | SDK/client adapters |
| `etl/document_builder` | Builds docs → NoSQL / RAG KB |
| `etl/feature_engineering` | Features → Zia AutoML |
| `catalyst/signals`, `circuits` | Event + workflow wiring |

## How you start (AI engineer)

1. Fill Catalyst env vars in `.env` (QuickML, RAG, NoSQL, Stratus, Zia, Signals).
2. Implement RAG document schema + `DocumentBuilderPipeline` → NoSQL-shaped JSON.
3. Wire `QuickMLClient` / `NoSQLClient` stubs → real Catalyst SDK calls.
4. Expose `POST /api/v1/ai/chat` that **only** calls QuickML RAG (mock in unit tests).
5. Add Signals/Cron reindex when FS A has CaseMaster writes.

See:

- [`catalyst_quickml_zia.md`](catalyst_quickml_zia.md) — service matrix
- [`getting_started_ai.md`](getting_started_ai.md) — day-1 steps
- [`../deployment/catalyst.md`](../deployment/catalyst.md) — full platform matrix
- [`rag_document_schema.md`](rag_document_schema.md) — document contract
