# Architecture Overview

Crime Intelligence Platform follows layered + domain-driven design.

## Layers

1. **API** (`backend/app/api`) — versioned FastAPI routers
2. **Services** — application / domain orchestration
3. **Repositories** — persistence boundary (SQLAlchemy local; Catalyst Data Store prod)
4. **Models / Schemas** — ORM + Pydantic DTOs by bounded context
5. **AI** — QuickML / Zia / RAG stubs
6. **Workers / ETL** — Cron, Signals, Circuits orchestration

## Production topology

See Catalyst mandatory mapping in [`../deployment/catalyst.md`](../deployment/catalyst.md).

**TODO:** Add sequence diagrams for FIR registration analytics and RAG query flows.
