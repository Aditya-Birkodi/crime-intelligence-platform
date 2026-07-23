# Catalyst Slate (frontend) — cip-web

Real Vue app lives in **`/frontend`** (not a separate `cip-web/` boilerplate).

| File | Purpose |
|------|---------|
| `/catalyst.json` | `"slate": [{ "name": "cip-web", "source": "./frontend" }]` |
| `/frontend/.catalyst/slate-config.toml` | install / build / `dist` |
| `/frontend/cli-config.json` | `npm run dev -- --port $ZC_SLATE_PORT` |

## Deploy

```bash
cd frontend && npm install && npm run build   # optional local check
cd .. && catalyst deploy --only slate
```

## Env

Set `VITE_API_BASE_URL` to the AppSail (or API Gateway) URL before build/deploy.
