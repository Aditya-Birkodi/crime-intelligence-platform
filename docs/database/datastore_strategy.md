# Data strategy: Local Postgres + Catalyst Data Store

**Decision:** Cases (`/api/v1/cases`) select persistence via `PERSISTENCE_BACKEND`.

| Environment | Relational store | Cache | Why |
|-------------|------------------|-------|-----|
| Local / CI | Docker Postgres (`PERSISTENCE_BACKEND=postgres`) | Docker Redis | Fast Alembic, pytest |
| Local Catalyst dry-run | JSON mock (`PERSISTENCE_BACKEND=catalyst` + `CATALYST_DATASTORE_MOCK=true`) | — | FE/API without OAuth |
| Catalyst staging/prod | **Catalyst Data Store** (`PERSISTENCE_BACKEND=catalyst`) | **Catalyst Cache** | Mandatory per `catalyst.txt` |

## Switch cases to Catalyst Data Store

Install SDK ([official setup](https://docs.catalyst.zoho.com/en/sdk/python/v1/setup/)):

```bash
pip install zcatalyst-sdk
```

- **Inside Catalyst Functions / AppSail:** `zcatalyst_sdk.initialize(scope='admin')`
  via `CATALYST_INIT_MODE=function` (default scope `CATALYST_SDK_SCOPE=admin`).
- **Outside Catalyst (local FastAPI):** Self-Client OAuth + `initialize_app`
  ([third-party apps](https://docs.catalyst.zoho.com/en/sdk/python/v1/integrate-sdk-in-third-party-apps/)).

```bash
# Real Data Store (Self Client OAuth — local / non-Catalyst host)
PERSISTENCE_BACKEND=catalyst
CATALYST_INIT_MODE=third_party
CATALYST_PROJECT_ID=...
CATALYST_ZAID=...
CATALYST_REFRESH_TOKEN=...
CATALYST_CLIENT_ID=...
CATALYST_CLIENT_SECRET=...
CATALYST_DATASTORE_MOCK=false

# Or local mock (no Catalyst console needed)
PERSISTENCE_BACKEND=catalyst
CATALYST_DATASTORE_MOCK=true
CATALYST_DATASTORE_MOCK_PATH=.data/catalyst_datastore.json
```

Seed mock FIRs:

```bash
PYTHONPATH=backend uv run python database/seed/seed_catalyst_cases.py
```

Create console tables named `cip_case_master`, `cip_victim`, `cip_accused`,
`cip_act_section_association` (prefix from `CATALYST_DATASTORE_TABLE_PREFIX`)
per [`catalyst_datastore_plan.md`](catalyst_datastore_plan.md).

## Rules

1. SQLAlchemy models are the **schema source of truth** (columns from FIR ER PDF).
2. Alembic migrations apply to **local Postgres**.
3. For Catalyst Data Store, create tables in the console with the **same logical
   columns** listed in [`catalyst_datastore_plan.md`](catalyst_datastore_plan.md).
4. Case APIs use `CaseStore` (`PostgresCaseStore` | `CatalystCaseStore`) so routers
   stay backend-agnostic.
5. Analytics (B2) and lookups still use Postgres until switched separately.
6. Do **not** treat local Postgres as the submission database of record.

## Backend owner checklist

- [x] Decision recorded (this file)
- [x] CaseStore port + Postgres / Catalyst adapters for `/api/v1/cases`
- [ ] Create Data Store tables in Catalyst console per plan
- [ ] Document table IDs / names in `.env` notes when available
- [ ] Optional: migrate seed → live Data Store for demo
