# Implementation Checklist — Team of 3

**Roles (updated)**

| Role | Person | Owns |
|------|--------|------|
| **Backend** (all) | **You** | FastAPI, SQLAlchemy/Alembic, FIR domain, analytics/network/AI APIs, ETL, Catalyst data/AI adapters (Data Store, NoSQL, Stratus, QuickML, Zia, Signals, Cron, Cache) |
| **Frontend 1** | Teammate 1 | React dashboards, maps, charts, case UI |
| **Frontend 2** | Teammate 2 | Network graph UI, Auth UX, Catalyst Slate / Gateway / deploy coordination |

**Contract between you and frontend**

- You publish **OpenAPI** (`/docs`) — they never guess field names.
- You ship **seeded demo data** early so UI is not blocked.
- PR tags: `[BE]`, `[FE-1]`, `[FE-2]`, `[ALL]`.

**Ground rules**

- Deploy on **Catalyst** (mandatory). Prefer Catalyst services over third-party equivalents.
- **AI paths must use Catalyst:** QuickML, NoSQL, Stratus, Zia, SmartBrowz, Signals, Circuits, Cache — see `docs/ai/README.md`.
- Follow **API → Service → Repository → DB**. No SQL in routers.
- Frontend consumes Pydantic/OpenAPI only.
- Definition of Done: code + test + short note in PR.

**Challenge blueprint:** [`../architecture/solution_blueprint.md`](../architecture/solution_blueprint.md)

---

## Phase 0 — Shared bootstrap (Day 1)

### All

- [ ] Copy `.env.example` → `.env`; run `./scripts/setup_dev.sh`
- [ ] Confirm `GET /health` and frontend shell load
- [ ] Create / join Catalyst project (Dev)
- [ ] Branch strategy + first demo date

### You (Backend)

- [x] Catalyst console: Project ID / Org ID in `.env` *(filled — keep secrets out of git)*
- [x] Decide: local Postgres for speed **+** Data Store table plan for submission → [`../database/datastore_strategy.md`](../database/datastore_strategy.md) + [`../database/catalyst_datastore_plan.md`](../database/catalyst_datastore_plan.md)
- [x] Share OpenAPI link / postman collection folder with FE → [`../api/frontend_handoff.md`](../api/frontend_handoff.md) + [`../../postman/`](../../postman/)

### Frontend 1 + 2

- [ ] `npm install` / `npm run dev`
- [ ] Agree route map: `/`, `/cases`, `/map`, `/network`, `/intelligence`

**Exit:** health OK; Catalyst project exists; FE knows which APIs are coming first.

---

## Your backend backlog (ordered)

Do these in order — each unblocks frontend.

### B1 — Domain foundation (kill silos)

- [x] Alembic: lookups (CaseCategory, GravityOffence, CaseStatusMaster, …)
- [x] Alembic: geography (State, District, Unit, UnitType)
- [x] Alembic: legal (Act, Section, CrimeHead, CrimeSubHead)
- [x] Alembic: CaseMaster (+ lat/long, dates, BriefFacts, FKs)
- [x] Alembic: Accused, Victim, ComplainantDetails, ActSectionAssociation
- [x] Seeds: multi-district Karnataka-like synthetic FIRs (no real PII) — `database/seed/seed_b1.py`
- [x] CrimeNo validator (`utils/crime_no.py`) + tests
- [x] CRUD: CaseMaster list/get/create + filters (station, status, date, crime head)
- [x] Nested or sub-resources: victims, accused, sections on a case
- [x] Lookups read APIs for FE dropdowns (`/api/v1/lookups/*`)

**FE can start:** Cases list/detail.

### B2 — Analytics & geo (visualization)

- [x] `GET /api/v1/analytics/overview` — KPIs
- [x] `GET /api/v1/analytics/geo/districts` — choropleth counts
- [x] `GET /api/v1/analytics/geo/incidents` — lat/long points + filters
- [x] `GET /api/v1/analytics/hotspots` — spatiotemporal bins
- [x] `GET /api/v1/analytics/alerts/trends` — spike vs baseline
- [x] Cache aggregates (in-memory TTL now; Catalyst Cache / Redis later)

**FE can start:** Map, heatmap, trend badges, dashboard KPIs.

### B3 — Network APIs (link analysis)

- [x] `GET /api/v1/network/graph?case_id=` / `?accused_id=` → `{ nodes, edges }`
- [x] `GET /api/v1/network/offenders/{id}` — repeat offender + cases + MO fields
- [x] Optional association score field on edges

**FE can start:** Network page + offender profile.

### B4 — AI / ML APIs (Catalyst-only)

- [ ] Document builder → NoSQL shape (done stub) + publish path
- [ ] Catalyst QuickML RAG wired in `integrations/catalyst/quickml.py`
- [ ] `POST /api/v1/ai/chat` — citations with CrimeNo / case id
- [ ] Feature engineering (`etl/feature_engineering`)
- [ ] `POST /api/v1/ai/predict/risk` — Zia AutoML / QuickML
- [ ] `GET /api/v1/ai/anomalies`
- [ ] Signals/Cron: reindex + feature refresh (with FE-2 for deploy hooks)

**FE can start:** Ask AI panel, risk/anomaly widgets.

### B5 — Catalyst production path

- [x] Case APIs → Catalyst Data Store via `CaseStore` (`PERSISTENCE_BACKEND=catalyst`)
- [x] Data Store strategy + mock path documented (`docs/database/datastore_strategy.md`)
- [ ] Create Data Store tables in Catalyst console (cip_case_master, …)
- [ ] NoSQL + Stratus + Cache clients real (not NotImplemented)
- [x] Functions or AppSail entry for FastAPI
- [ ] API Gateway route list for FE-2
- [ ] Circuits ETL orchestration (stretch)

---

## Frontend 1 backlog

- [x] Vue 3 app shell + routing (Home, Cases, Case detail, Map, Network)
- [x] Cases list / detail consuming Case APIs
- [ ] Dashboard KPIs + charts
- [ ] District drill-down **map** + pins + time filters
- [ ] Hotspot heatmap + trend alert UI
- [ ] Risk / anomaly cards (when B4 ready)

## Frontend 2 backlog

- [ ] Catalyst Authentication login/logout
- [ ] Network / link-analysis graph UI
- [ ] Repeat-offender profile page
- [ ] Ask AI panel on case / cluster
- [ ] Slate / Web Client Hosting + Gateway URL in `VITE_*`
- [ ] Demo accounts + deploy checklist

---

## Phase exit criteria (demo path)

```text
Login (FE-2)
  → Map + hotspot/alert (FE-1 + your B2)
  → Network graph (FE-2 + your B3)
  → Ask AI (FE-2 + your B4)
  → Risk/anomaly (FE-1 + your B4)
```

---

## Dependency map

```text
You B1 Case APIs + seeds
        ├──► FE-1 Cases UI
        ├──► You B2 analytics/geo
        │         └──► FE-1 Map / dashboard
        ├──► You B3 network
        │         └──► FE-2 Graph UI
        └──► You B4 AI
                  ├──► FE-2 Ask AI
                  └──► FE-1 Risk widgets

FE-2 Auth + Gateway + Slate ──► staging URL for everyone
```

---

## First week (you — backend only)

| Day | Focus |
|-----|--------|
| 1 | Catalyst project IDs; Alembic lookups + geography; seed script skeleton |
| 2 | CaseMaster + Accused/Victim models; list/get APIs; CrimeNo tests |
| 3 | Richer seeds (3+ districts); analytics overview + geo incidents |
| 4 | Hotspots + trend alerts APIs |
| 5 | Network graph API; OpenAPI review with FE |
| Weekend | QuickML console RAG + start `POST /ai/chat` |

Ship **OpenAPI + seed DB** to FE by end of day 3 even if AI is incomplete.

---

## Daily standup

1. Which **B#** checkbox moved?
2. Is FE blocked on a missing field/endpoint?
3. Today’s single backend deliverable?

Update checkboxes in this file as you go.
