# API Documentation

Version prefix: `/api/v1`.

## For frontend teammates

Start here: **[`frontend_handoff.md`](frontend_handoff.md)**

- Swagger: `http://127.0.0.1:8000/docs`
- Postman: [`../../postman/CIP_Backend.postman_collection.json`](../../postman/CIP_Backend.postman_collection.json)
- Export schema: `./scripts/export_openapi.sh` → `openapi/openapi.json`

## Current endpoints

| Method | Path | Status |
|--------|------|--------|
| GET | `/health` | Live |
| GET | `/api/v1/status` | Live |
| GET | `/api/v1/cases` | Planned B1 |
| GET | `/api/v1/analytics/*` | Planned B2 |
| GET | `/api/v1/network/*` | Planned B3 |
| POST | `/api/v1/ai/chat` | Planned B4 |

## Data backend

- Local Postgres for development; Catalyst Data Store for submission — see
  [`../database/datastore_strategy.md`](../database/datastore_strategy.md).
- Table create order: [`../database/catalyst_datastore_plan.md`](../database/catalyst_datastore_plan.md).
