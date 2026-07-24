# Frontend handoff — Vue 3 + OpenAPI

## Stack

Vue 3 + Vite + TypeScript + TailwindCSS + Vue Router.

## Point FE at ngrok backend

1. Backend (your machine):
```bash
uv run uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000 --app-dir .
ngrok http 8000
```

2. Frontend `.env`:
```bash
# frontend/.env  (copy from .env.example)
VITE_API_BASE_URL=https://YOUR_SUBDOMAIN.ngrok-free.app
```
No trailing slash. Restart `npm run dev` after changing env.

3. Teammates:
```bash
cd frontend
npm install
npm run dev
```

Header bar shows the active API base URL.

## Pages

| Route | Page | APIs used |
|-------|------|-----------|
| `/` | Home | `/health`, `/analytics/overview` |
| `/cases` | Case list + filters | `/api/v1/cases`, lookups |
| `/cases/:id` | Case detail | `/api/v1/cases/{id}` or `/by-crime-no/{crime_no}` |
| `/map` | Map / hotspots | `/analytics/geo/incidents`, `/geo/districts`, `/hotspots` |
| `/network` | Link analysis graph | `/api/v1/network/graph`, `/network/offenders/{id}` |

## Live OpenAPI

| URL | Use |
|-----|-----|
| `{base}/docs` | Swagger |
| `{base}/openapi.json` | Contract |

Postman: [`../../postman/CIP_Backend.postman_collection.json`](../../postman/CIP_Backend.postman_collection.json) — single collection; set `baseUrl` variable for AppSail or local.

## B1 — Cases

| Method | Path |
|--------|------|
| GET | `/api/v1/cases` (filters: `police_station_id`, `case_status_id`, `crime_major_head_id`, `crime_no`, dates) |
| GET | `/api/v1/cases/{id}` (detail: victims, accused, complainants, occurrence, arrests, chargesheets) |
| GET | `/api/v1/cases/by-crime-no/{crime_no}` |
| POST | `/api/v1/cases` |
| POST | `/api/v1/cases/{id}/victims` / `accused` / `complainants` / `act-sections` |
| GET | `/api/v1/lookups/*` (statuses, categories, gravity, crime-heads, districts, stations, courts, employees) |

## B2 — Analytics (map / KPIs)

| Method | Path | FE use |
|--------|------|--------|
| GET | `/api/v1/analytics/overview` | Home KPIs |
| GET | `/api/v1/analytics/geo/districts` | District choropleth |
| GET | `/api/v1/analytics/geo/incidents` | Map pins |
| GET | `/api/v1/analytics/hotspots?grain=hour` | Heatmap bins |
| GET | `/api/v1/analytics/alerts/trends` | Spike badges |

## B3 — Network

| Method | Path | FE use |
|--------|------|--------|
| GET | `/api/v1/network/graph?case_id=` or `?accused_id=` | Force graph (`nodes`, `edges`, `score`) |
| GET | `/api/v1/network/offenders/{id}` | Repeat-offender profile + MO |

## B4 — AI

| Method | Path | FE use |
|--------|------|--------|
| POST | `/api/v1/ai/chat` | Ask AI (QuickML RAG + optional NetworkX Graph RAG on AppSail) |
| GET | `/api/v1/ai/graph/context` | Ego-graph summary for Graph RAG (`case_id` or `accused_id`) |
| POST | `/api/v1/ai/predict/risk` | District/station risk cards |
| GET | `/api/v1/ai/anomalies` | Anomaly / spike call-outs |

Seed: `fir_full_dataset.yaml` = 18 curated + 100 KSP Excel cases (118 total).

## CORS

Backend `DEBUG=true` allows all origins (needed for Vite → ngrok).
