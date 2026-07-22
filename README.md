# Crime Intelligence Platform

Enterprise-grade AI Crime Intelligence & Analytics Platform for the
**Karnataka State Police Hackathon**.

This repository is a production-oriented scaffold: clean architecture,
domain-driven boundaries aligned to the Police FIR ER diagram, and
mandatory Zoho Catalyst deployment targets. Business logic, domain APIs,
and AI implementations are intentionally **not** included yet.

## Reference Documents

| Document | Role |
|----------|------|
| [`Police_FIR_ER_Diagram.pdf`](Police_FIR_ER_Diagram.pdf) | FIR domain entity / relationship source of truth |
| [`catalyst.txt`](catalyst.txt) | Mandatory Catalyst capability → service mapping |

**Deployment via Catalyst is mandatory.** Local Docker (PostgreSQL + Redis)
is for development only.

## Stack

| Layer | Technology |
|-------|------------|
| Backend | Python 3.12, FastAPI, Pydantic v2, SQLAlchemy 2, Alembic, uv |
| Frontend | Vue 3, TypeScript, Vite, TailwindCSS, Vue Router |
| Local Dev | Docker Compose (Postgres 16, Redis 7) |
| Production | Zoho Catalyst (Functions, Data Store, Cache, NoSQL, Stratus, Auth, API Gateway, QuickML, Zia, SmartBrowz, Signals, Circuits, …) |

## Repository Structure

```
crime-intelligence-platform/
├── backend/          # FastAPI application (DDD layers)
├── frontend/         # Vue 3 + Vite SPA (Catalyst Slate / Web Client)
├── database/         # Schema docs, seeds, Alembic migrations
├── etl/              # Ingestion → feature-engineering pipeline stubs
├── catalyst/         # Catalyst deployment stubs
├── docs/             # Architecture, API, DB, AI, deployment guides
├── scripts/          # Dev setup helpers
├── tests/            # Cross-cutting unit / integration tests
└── catalyst/         # Catalyst Functions / AppSail / Gateway stubs
```

### Backend bounded contexts (FIR ER)

| Context | Example entities |
|---------|------------------|
| Case | CaseMaster, Victim, Accused, ArrestSurrender, ChargesheetDetails |
| Legal | Act, Section, CrimeHead, CrimeSubHead |
| Geography | State, District, Court, Unit, UnitType |
| Personnel | Employee, Rank, Designation |
| Lookups | CaseCategory, GravityOffence, CaseStatusMaster, … |

## Development Setup

### Prerequisites

- Python 3.12+
- [uv](https://github.com/astral-sh/uv)
- Node.js 20+
- Docker & Docker Compose

### 1. Clone & environment

```bash
cp .env.example .env
# Edit .env for local DATABASE_URL / REDIS_URL as needed
```

### 2. Backend

```bash
uv sync --extra dev
uv run pre-commit install
docker compose up -d
# Option A — simple:
uv run python app.py
# Option B — uvicorn CLI:
uv run uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000 --app-dir .
# Health: http://127.0.0.1:8000/health
```

Or use the helper:

```bash
./scripts/setup_dev.sh
```

### 3. Frontend (Vue 3)

```bash
cd frontend
cp .env.example .env
# Set VITE_API_BASE_URL to http://127.0.0.1:8000 or your ngrok HTTPS URL
npm install
npm run dev
```

### 4. Tests

```bash
uv run pytest
```

## Coding Standards

| Tool | Purpose |
|------|---------|
| Black | Formatting (line length 88) |
| isort | Import sorting (Black profile) |
| Ruff | Lint |
| MyPy | Static types (strict on `backend/app`, `etl`) |
| pre-commit | Runs the above on commit |

Configure via [`pyproject.toml`](pyproject.toml).

## Architecture Principles

- FastAPI + Dependency Injection
- Repository pattern + Service layer
- Central Pydantic Settings (`backend/app/core/config.py`)
- Structured logging (application / API / error / AI)
- Exception hierarchy + response models
- No business logic in this scaffold — placeholders with `# TODO` only

## Documentation

- [Architecture overview](docs/architecture/overview.md)
- [Solution blueprint (hackathon challenge)](docs/architecture/solution_blueprint.md)
- [Bounded contexts](docs/architecture/bounded_contexts.md)
- [FIR ER reference](docs/database/fir_er_reference.md)
- [Data strategy (Postgres + Data Store)](docs/database/datastore_strategy.md)
- [Frontend API handoff](docs/api/frontend_handoff.md)
- [Catalyst deployment](docs/deployment/catalyst.md)
- [Catalyst console setup (beginner)](docs/deployment/catalyst_console_setup.md)
- [Team checklist](docs/development/team_checklist.md)
- [AI — Catalyst-first](docs/ai/README.md)
- [AI engineer day-1](docs/ai/getting_started_ai.md)
- [Dev setup](docs/development/setup.md)

## License

MIT — see [`LICENSE`](LICENSE).
