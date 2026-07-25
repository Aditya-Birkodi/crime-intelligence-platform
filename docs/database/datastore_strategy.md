# Data strategy: Local Postgres + Catalyst Data Store

**Decision:** Cases (`/api/v1/cases`) select persistence via `PERSISTENCE_BACKEND`.

| Environment | Cases / analytics | Lookups | Notes |
|-------------|-------------------|---------|-------|
| Local / CI | Docker Postgres (`PERSISTENCE_BACKEND=postgres`) | Postgres | Fast Alembic, pytest |
| Local Catalyst dry-run | JSON mock (`catalyst` + `DATASTORE_MOCK=true`) | `appsail_lookups.json` | FE/API without OAuth |
| **Catalyst AppSail (Dev + Prod)** | **Live Data Store** (`catalyst` + `DATASTORE_MOCK=false`) | DS masters + JSON fallback | Mandatory for hosted CIP |

AppSail `app-config.json` ships with live Data Store enabled. On AppSail boot,
`app.py` also defaults `PERSISTENCE_BACKEND=catalyst` and `DATASTORE_MOCK=false`
when `X_ZOHO_CATALYST_LISTEN_PORT` is set.

Slate production builds call AppSail via `frontend/.env.production`
(`VITE_API_BASE_URL`).

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

Seed mock FIRs (ER-aligned demo dataset):

```bash
PYTHONPATH=backend python database/seed/seed_fir_dataset.py --target catalyst-mock
# or both Postgres + mock:
PYTHONPATH=backend python database/seed/seed_fir_dataset.py --force
```

Canonical YAML: [`../../database/seed/fir_demo_dataset.yaml`](../../database/seed/fir_demo_dataset.yaml).

Create console tables named `cip_case_master`, `cip_victim`, `cip_accused`,
`cip_act_section_association` (prefix from `CATALYST_DATASTORE_TABLE_PREFIX`)
per [`catalyst_datastore_plan.md`](catalyst_datastore_plan.md) and
[`../../database/seed/catalyst_tables_checklist.md`](../../database/seed/catalyst_tables_checklist.md).

### Live seed from `appsail_datastore.json`

```bash
export CATALYST_PROJECT_DOMAIN=https://api.catalyst.zoho.in   # India DC
export CATALYST_INIT_MODE=third_party   # local; use function on AppSail
export DATASTORE_MOCK=false
PYTHONPATH=backend python database/seed/seed_catalyst_datastore_live.py --limit 5
PYTHONPATH=backend python database/seed/seed_catalyst_datastore_live.py --force
```

AppSail production: set `DATASTORE_MOCK=false` in [`../../app-config.json`](../../app-config.json)
(table names resolve without IDs; optional `CATALYST_TABLE_*` in console AppSail env).
Lookups/RAG remain on JSON paths in the same config.

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
- [x] Data Store Wave-2 table checklist (`database/seed/catalyst_tables_checklist.md`)
- [x] Live seed script (`database/seed/seed_catalyst_datastore_live.py`)
- [ ] Create Data Store tables in Catalyst console (manual)
- [ ] Paste Table IDs into `.env` / AppSail env when available
- [ ] Run live seed + set `DATASTORE_MOCK=false` on AppSail
