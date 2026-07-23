# Catalyst layout (this repo)

After `catalyst init` (AppSail + Slate):

```
.
├── catalyst.json          # AppSail cip-api + Slate cip-web
├── app-config.json        # AppSail Python 3.12 start command
├── .catalystrc            # linked Catalyst project (local)
├── app.py                 # AppSail / local API entry
├── requirements.txt       # AppSail runtime deps
├── backend/               # FastAPI code
├── frontend/              # Slate source (cip-web)
│   ├── .catalyst/slate-config.toml
│   └── cli-config.json
└── catalyst/              # human docs / stubs (not CLI source trees)
```

**Do not use** the CLI-generated `cip-web/` boilerplate — removed; Slate points at `frontend/`.

Deploy: `catalyst deploy`
Serve local: `catalyst serve` (if configured) or `python app.py` + `cd frontend && npm run dev`
