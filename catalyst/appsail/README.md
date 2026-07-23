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
catalyst deploy --only appsail:cip-api
# or full:
catalyst deploy
```

`scripts.predeploy` installs packages into `.appsail_vendor/` (gitignored) and the
CLI packages them with the upload. **Do not** `pip install` in the start command —
AppSail kills instances that do not bind the listen port within ~10 seconds.

## Start command

`python3 -u app.py` — binds `0.0.0.0:$X_ZOHO_CATALYST_LISTEN_PORT`.

## Env vars

Do **not** put reserved Catalyst keys in `app-config.json` `env_variables`
(e.g. `CATALYST_ENV`, `CATALYST_*`, `X_ZOHO_*`). Set those in the AppSail console instead.

Safe examples in `app-config.json`: `APP_RELOAD`, `PERSISTENCE_BACKEND`,
`DATASTORE_MOCK`, `DATASTORE_MOCK_PATH`, `CORS_ORIGINS`, `DEBUG`, `LOG_DIR`.

For hackathon demo, AppSail uses the seeded mock JSON at
`database/seed/appsail_datastore.json` until real Data Store tables + OAuth are wired.
