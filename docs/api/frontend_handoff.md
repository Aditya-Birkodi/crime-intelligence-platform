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
| `/cases/:id` | Case detail | `/api/v1/cases/{id}` |
| `/map` | Map / hotspots | `/analytics/geo/incidents`, `/geo/districts`, `/hotspots` |
| `/network` | Network placeholder | cases + detail (until B3) |

## Live OpenAPI

| URL | Use |
|-----|-----|
| `{base}/docs` | Swagger |
| `{base}/openapi.json` | Contract |

Postman: [`../../postman/CIP_Backend.postman_collection.json`](../../postman/CIP_Backend.postman_collection.json)

## B1 — Cases

| Method | Path |
|--------|------|
| GET | `/api/v1/cases` |
| GET | `/api/v1/cases/{id}` |
| GET | `/api/v1/lookups/*` |

## B2 — Analytics (map / KPIs)

| Method | Path | FE use |
|--------|------|--------|
| GET | `/api/v1/analytics/overview` | Home KPIs |
| GET | `/api/v1/analytics/geo/districts` | District choropleth |
| GET | `/api/v1/analytics/geo/incidents` | Map pins |
| GET | `/api/v1/analytics/hotspots?grain=hour` | Heatmap bins |
| GET | `/api/v1/analytics/alerts/trends` | Spike badges |

## CORS

Backend `DEBUG=true` allows all origins (needed for Vite → ngrok).
