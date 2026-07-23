# Postman — CIP Backend

## Import

1. Open Postman → **Import**
2. Add:
   - `CIP_Backend.postman_collection.json`
   - `CIP_AppSail.postman_environment.json` (Catalyst AppSail)
   - `CIP_Local.postman_environment.json` (local uvicorn)
3. Select environment **CIP AppSail** or **CIP Local** (top-right)

## Endpoints covered

| Folder | Status |
|--------|--------|
| Infrastructure | `/health`, `/api/v1/status`, OpenAPI |
| Lookups | statuses, categories, gravity, crime heads, districts, stations |
| Cases (B1) | list, get, create, add victim/accused/act-section |
| Analytics (B2) | overview, geo districts/incidents, hotspots, trends |
| Network / AI | stubs only (B3/B4) |

## Notes

- **Create case** / **List cases** save `caseMasterId` for follow-up requests.
- Use a unique 18-char `crime_no` when creating.
- Analytics (B2) need **Postgres**; cases on AppSail may use **Catalyst Data Store**.
- AppSail URL: `https://cip-api-50044183252.development.catalystappsail.in`
