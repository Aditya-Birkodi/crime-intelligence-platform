# Catalyst AppSail (backend) — cip-api

Paired with **Slate** frontend `cip-web` → `./frontend`.

| File | Purpose |
|------|---------|
| `/app-config.json` | AppSail stack, start command, env |
| `/app.py` | Uvicorn entry (listens on `X_ZOHO_CATALYST_LISTEN_PORT`) |
| `/requirements.txt` | Runtime deps (vendored at deploy via `scripts.predeploy`) |
| `/catalyst.json` | Links AppSail source `.` as `cip-api` |

## Deploy

```bash
# Development environment (default)
catalyst deploy --only appsail:cip-api
catalyst deploy --only slate:cip-web

# Full project
catalyst deploy
```

`scripts.predeploy` installs packages into `.appsail_vendor/` (gitignored) and the
CLI packages them with the upload. **Do not** `pip install` in the start command —
AppSail kills instances that do not bind the listen port within ~10 seconds.

## Start command

`python3 -u app.py` — binds `0.0.0.0:$X_ZOHO_CATALYST_LISTEN_PORT`.

## Env vars (live Data Store)

`app-config.json` is configured for **live Catalyst Data Store**:

| Key | Value | Meaning |
|-----|-------|---------|
| `PERSISTENCE_BACKEND` | `catalyst` | Cases / analytics / network via Data Store |
| `DATASTORE_MOCK` | `false` | No JSON mock — real tables |
| `LOOKUPS_PATH` | `database/seed/appsail_lookups.json` | Fallback for crime heads etc.; districts/units/statuses prefer DS |
| `RAG_DOCS_PATH` / `AI_FEATURES_PATH` | seed JSON | Ask-AI citations until NoSQL KB is wired |
| `QUICKML_MOCK` | `true` | Set `false` + OAuth when enabling live GLM |

Do **not** put reserved Catalyst keys in `app-config.json` `env_variables`
(e.g. `CATALYST_ENV`, `CATALYST_*`, `X_ZOHO_*`). Set those in the AppSail console instead.

### Seed

Tables: see `database/seed/catalyst_tables_checklist.md` (**Big Int** for all ROWID FKs).

```bash
# Cases already live (221). Children:
python3 database/seed/seed_catalyst_via_cli.py --skip-masters --children-only

# Master lookups (district / unit / status):
python3 database/seed/seed_catalyst_via_cli.py --masters-only
```

### Verify

```bash
curl -sS https://cip-api-50044183252.development.catalystappsail.in/api/v1/status
# expect: persistence=catalyst, datastore_mock=false, cases_source=catalyst_datastore
```

Slate (`cip-web`) is built with `VITE_API_BASE_URL` pointing at this AppSail URL
(`frontend/.env.production`).
