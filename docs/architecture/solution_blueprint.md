# Solution Blueprint — AI-Driven Crime Analytics & Visualization Platform

Maps the **Karnataka State Police hackathon challenge** to this repo, Catalyst
services, and team ownership. Source challenge themes: silos → unified platform,
reactive → proactive, Excel → interactive intelligence.

## Problem → Platform mapping

| Challenge pain | Platform capability | Primary Catalyst services |
|----------------|---------------------|---------------------------|
| Data silos / Excel | Unified FIR domain (Case + parties + legal + geo) in one Data Store | **Data Store**, API Gateway, Auth |
| Limited SCRB statewide view | District / station drill-down dashboards + maps | Data Store aggregates, **Cache**, Slate UI |
| No AI / hidden patterns | RAG over BriefFacts, predictive risk, anomaly flags | **QuickML**, **Zia AutoML**, NoSQL |
| Fragmented offender view | Link/network graph (accused–victim–case–location) | Data Store graph query APIs + UI |
| Reactive policing | Hotspots, trend alerts, risk scores | QuickML/Zia + Cron/Signals refresh |

---

## Capability matrix (what to build)

### 1. Advanced visualization & geospatial intelligence

| Requirement | Backend | Frontend | Catalyst | Owner |
|-------------|---------|----------|----------|-------|
| District / station drill-down maps | `GET /api/v1/analytics/geo/summary` | Map + choropleth / markers | Data Store; Cache | **BE** + FE-1 |
| Spatiotemporal clusters / hotspots | `GET /api/v1/analytics/hotspots` | Heatmap + time slider | Data Store; QuickML optional | **BE** + FE-1 |
| Emerging trend alerts | `GET /api/v1/analytics/alerts/trends` | Red-zone / badge | Cron → Cache | **BE** + FE-1 |
| Dynamic intelligence reports | Aggregate APIs + narrative | Dashboard sections | SmartBrowz stretch | **BE** + FE-1 |

**Data needed from ER:** CaseMaster (`latitude`, `longitude`, `IncidentFromDate`, `PoliceStationID`, crime heads, status), Unit, District.

### 2. Criminological network & link analysis

| Requirement | Backend | Frontend | Catalyst | Owner |
|-------------|---------|----------|----------|-------|
| Relationship mapping | `GET /api/v1/network/graph` → nodes/edges | Force-directed graph | Data Store; Cache | **BE** + FE-2 |
| Repeat offender tracking | Offender profile API | Timeline UI | Data Store; QuickML MO optional | **BE** + FE-2 |
| Association detection | Edge scores / rules (+ ML stretch) | Highlight hidden links | QuickML/Zia stretch | **BE** + FE-2 |

**Data needed:** Accused, Victim, CaseMaster, ArrestSurrender, ActSectionAssociation, Unit.

**Code home:** `backend/app/ai/graph/` (scoring) + `backend/app/services/` network service + `frontend` Network page.

### 3. Sociological & AI-driven predictive dashboards

| Requirement | Backend | Frontend | Catalyst | Owner |
|-------------|---------|----------|----------|-------|
| Socio-economic overlays | Indicators join API | Dual-layer map | Data Store / NoSQL | **BE** + FE-1 |
| Predictive risk scoring | Features → model API | High-risk cards | **Zia AutoML** / **QuickML** | **BE** |
| Anomaly detection | Anomalies API | Dashboard call-outs | Cron + Cache | **BE** + FE-1 |

### 4–6. Patterns, networks, AI/ML (summary)

| # | Challenge line | MVP deliverable |
|---|----------------|-----------------|
| 4 | Pattern & trend discovery | Hotspots API + heatmap + trend alert badges |
| 5 | Network & behavioral / MO | Ego network graph + repeat-offender profile |
| 6 | AI/ML intelligence | QuickML **RAG** Q&A + one **risk/anomaly** model via Zia AutoML/QuickML |

---

## Recommended hackathon MVP (judge-ready demo)

Aim for a **5-minute demo** that hits all challenge themes without boiling the ocean:

1. **Login** (Catalyst Authentication) → SCRB analyst home
2. **Statewide map** — district drill-down → station → incident pins (lat/long)
3. **Hotspot + trend alert** — one district pulsing “spike vs 4-week average”
4. **Link graph** — open one accused → connected cases / victims / stations
5. **Ask AI** — QuickML RAG on BriefFacts (“summarize MO for this cluster”)
6. **Risk panel** — one predictive score or anomaly list for next period

**Stretch (if time):** socio-economic overlay, SmartBrowz PDF brief, OCR of scanned FIR via Zia.

---

## Architecture (solution view)

```text
                    Catalyst API Gateway + Authentication
                                    │
         ┌──────────────────────────┼──────────────────────────┐
         ▼                          ▼                          ▼
   Slate / Web Client         AppSail / Functions         Event Functions
   (dashboards, map,          (FastAPI: cases,            (Signals → reindex,
    network, Ask AI)           analytics, network,         Cron → features)
                               ai/chat, ai/predict)
         │                          │
         │              ┌───────────┴───────────┐
         │              ▼                       ▼
         │       Data Store (FIR ER)      NoSQL (RAG docs)
         │              │                       │
         │              ▼                       ▼
         │         Cache (aggregates)    QuickML RAG / LLM
         │                                      │
         │                              Zia AutoML (risk)
         │                              Stratus (FIR PDFs)
         │                              SmartBrowz (reports)
         └──────────────────────────────────────────────┘
```

FIR schema source of truth: [`Police_FIR_ER_Diagram.pdf`](../../Police_FIR_ER_Diagram.pdf).

---

## Team ownership

| Role | Owns | First milestone |
|------|------|-----------------|
| **You — Backend (all)** | FIR domain, analytics/geo/network APIs, ETL, QuickML/Zia/NoSQL/Stratus adapters, Seeds, OpenAPI | Seeded multi-district FIRs + Case + geo + network + AI APIs |
| **Frontend 1** | Dashboards, maps, charts, case screens | District map + KPI dashboard on your APIs |
| **Frontend 2** | Network graph UI, Auth UX, Catalyst Slate/Gateway deploy | Login + link graph + Ask AI panel |

You own every row in the capability matrix under **Backend**. Frontend owns UI only; they must not invent parallel business logic.


---

## Implementation phases (challenge-shaped)

### Phase 0 — Foundation (silos → one system)
- Catalyst project + Auth + Data Store tables (or local Postgres mirror)
- CaseMaster + Accused + Victim + District/Unit + crime heads
- Seed synthetic Karnataka-like data (multiple districts)

### Phase 1 — Visualization (capability 1 + 4)
- Geo summary + incident points APIs
- Map drill-down + time filter
- Hotspot aggregation + trend alert endpoint

### Phase 2 — Network (capability 2 + 5)
- Nodes/edges API from Accused/Victim/Case/Unit
- Graph page + repeat-offender profile
- Optional QuickML “describe MO” on selected subgraph

### Phase 3 — AI intelligence (capability 3 + 6)
- Document builder → NoSQL → QuickML Knowledge Base / RAG
- Feature engineering → Zia AutoML / QuickML risk scores
- Anomaly flags on unit-day series
- Dashboard widgets for risk + anomalies + Ask AI

### Phase 4 — Polish & Catalyst completeness
- Signals/Cron, Cache, Gateway, Slate/AppSail, demo script, `catalyst.txt` compliance

---

## API sketch (contract for FS A / AI / FS B)

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/api/v1/analytics/overview` | KPI cards (counts by status/head) |
| GET | `/api/v1/analytics/geo/districts` | District aggregates for choropleth |
| GET | `/api/v1/analytics/geo/incidents` | Lat/long points + filters |
| GET | `/api/v1/analytics/hotspots` | Spatiotemporal bins |
| GET | `/api/v1/analytics/alerts/trends` | Spike alerts |
| GET | `/api/v1/network/graph` | `{ nodes, edges }` |
| GET | `/api/v1/network/offenders/{id}` | Repeat offender profile |
| POST | `/api/v1/ai/chat` | QuickML RAG |
| POST | `/api/v1/ai/predict/risk` | District/station risk scores |
| GET | `/api/v1/ai/anomalies` | Recent anomaly call-outs |

Implement behind service/repository layers; no SQL in routers.

---

## Catalyst compliance reminder

For each capability, prefer the service in [`catalyst.txt`](../../catalyst.txt).
Console how-to: [`catalyst_console_setup.md`](catalyst_console_setup.md).

| Don’t | Do |
|-------|----|
| OpenAI for FIR Q&A | QuickML RAG |
| Pinecone / local-only vector DB in prod | QuickML Knowledge Base + NoSQL |
| S3 as primary blob store | Stratus |
| Auth0-only in prod | Catalyst Authentication |
| Manual Excel for demo data story | Data Store + interactive Slate UI |

---

## What the backend owner does this week

1. Catalyst console: project IDs + QuickML RAG sample docs ([`catalyst_console_setup.md`](../deployment/catalyst_console_setup.md)).
2. Alembic + seeds + Case/Accused/Victim APIs (B1).
3. Geo + hotspots + trend APIs (B2) so FE-1 can build the map.
4. Network graph API (B3) so FE-2 can build the graph.
5. QuickML chat + risk/anomaly (B4).

Judges should see: **map → hotspot alert → network → AI answer → risk score** — you supply every API behind that path.
