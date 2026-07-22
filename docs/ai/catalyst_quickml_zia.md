# Catalyst QuickML / Zia / SmartBrowz — AI engineer map

From [`catalyst.txt`](../../catalyst.txt). **Use these services; do not substitute.**

| # | Capability | Required service | Code entrypoint |
|---|------------|------------------|-----------------|
| 11 | Text LLMs / RAG / KB | Catalyst QuickML | `integrations/catalyst/quickml.py`, `ai/chat`, `ai/rag` |
| 12 | No-code ML pipelines | Catalyst QuickML | `ai/prediction` |
| 13 | Tabular AutoML | Catalyst Zia AutoML | `integrations/catalyst/zia.py`, `etl/feature_engineering` |
| 14 | OCR / vision / ID | Catalyst Zia Services | `integrations/catalyst/zia.py` |
| 15 | Speech / translation | Catalyst Zia Services | later |
| 16 | PDF / headless reports | Catalyst SmartBrowz | `integrations/catalyst/smartbrowz.py` |
| 7 | Semi-structured docs | Catalyst NoSQL | `integrations/catalyst/nosql.py` |
| 8 | Blobs / FIR scans | Catalyst Stratus | `integrations/catalyst/stratus.py` |
| 9 | Cache | Catalyst Cache | `integrations/catalyst/cache.py` |
| 21–22 | Reindex events | Catalyst Signals | `catalyst/signals/`, workers |
| 23 | ETL workflow | Catalyst Circuits | `catalyst/circuits/` |
| 20 | Nightly jobs | Catalyst Cron | `app/workers/` |

## Env vars (fill in Catalyst console)

```bash
CATALYST_QUICKML_ENDPOINT=
CATALYST_QUICKML_MODEL_ID=
CATALYST_RAG_KNOWLEDGE_BASE_ID=
CATALYST_RAG_ENDPOINT=
CATALYST_NOSQL_TABLE=
CATALYST_NOSQL_ENDPOINT=
CATALYST_STRATUS_BUCKET=
CATALYST_ZIA_ENDPOINT=
CATALYST_ZIA_AUTOML_ENDPOINT=
CATALYST_SMARTBROWZ_ENDPOINT=
CATALYST_SIGNALS_TOPIC=
CATALYST_CIRCUITS_ID=
CATALYST_CACHE_SEGMENT=
```

## Integration pattern

```text
Service (ai/chat) → CatalystQuickMLClient → QuickML HTTP/SDK
                 ↘ CatalystNoSQLClient   → document fetch
Worker / Signals  → DocumentBuilderPipeline → NoSQL + RAG index
```

Never call a public LLM API from `ai/*` services in production paths.
