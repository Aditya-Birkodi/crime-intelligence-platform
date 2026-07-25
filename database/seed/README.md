# Seed data

Canonical dataset: [`fir_demo_dataset.yaml`](fir_demo_dataset.yaml)
Aligned to [`Police_FIR_ER_Diagram.pdf`](../../Police_FIR_ER_Diagram.pdf)

~18 synthetic FIRs across Bengaluru City, Mysuru, Belagavi — no real PII.

## What is seeded (analytics + intelligence)

| Layer | Entities |
|-------|----------|
| Masters | CaseCategory, CaseStatus, Gravity, Occupation, Religion, Caste |
| Geography | State, District, UnitType, Unit (+ ParentUnit circles), Court |
| Legal | Act, Section, CrimeHead, CrimeSubHead, CrimeHeadActSection |
| Personnel | Rank, Designation, Employee (registering officer / IO) |
| Case | CaseMaster, Victim, Accused, Complainant, ActSectionAssociation |
| Investigation | Inv_OccuranceTime, ArrestSurrender + junction, ChargesheetDetails |
| AI prep | [`fir_rag_documents.json`](fir_rag_documents.json) text blobs for QuickML/NoSQL |

## Seed both targets (recommended)

```bash
PYTHONPATH=backend python database/seed/seed_fir_dataset.py --force

# Mock + RAG docs only
PYTHONPATH=backend python database/seed/seed_fir_dataset.py --target catalyst-mock

# Postgres only (drops/recreates schema when --force)
PYTHONPATH=backend python database/seed/seed_fir_dataset.py --target postgres --force
```

## Legacy wrappers

```bash
PYTHONPATH=backend python database/seed/seed_b1.py --force
PYTHONPATH=backend python database/seed/seed_catalyst_cases.py
```

## AppSail (JSON mock bundle)

After regenerating `appsail_datastore.json`:

```bash
catalyst deploy --only appsail:cip-api
```

## Live Catalyst Data Store

Console create steps + column list: [`catalyst_tables_checklist.md`](catalyst_tables_checklist.md)
(also [`../docs/database/catalyst_datastore_plan.md`](../../docs/database/catalyst_datastore_plan.md)).

### 1. Create tables in console

Cloud Scale → Data Store → create `cip_case_master`, `cip_victim`, `cip_accused`,
`cip_act_section_association`. Optional: paste Table IDs into `.env`:

```bash
CATALYST_TABLE_CASE_MASTER=
CATALYST_TABLE_VICTIM=
CATALYST_TABLE_ACCUSED=
CATALYST_TABLE_ACT_SECTION=
```

### 2. Seed (local Self Client OAuth)

```bash
# India DC + third-party SDK
export CATALYST_PROJECT_DOMAIN=https://api.catalyst.zoho.in
export CATALYST_INIT_MODE=third_party
export PERSISTENCE_BACKEND=catalyst
export DATASTORE_MOCK=false

# Required: PROJECT_ID, ZAID, CLIENT_ID, CLIENT_SECRET, REFRESH_TOKEN in .env

PYTHONPATH=backend python database/seed/seed_catalyst_datastore_live.py --dry-run
PYTHONPATH=backend python database/seed/seed_catalyst_datastore_live.py --limit 5
PYTHONPATH=backend python database/seed/seed_catalyst_datastore_live.py --force   # full ~221 FIRs
```

Probe a table ID:

```bash
PYTHONPATH=backend python scripts/probe_catalyst_table.py <TABLE_ID>
PYTHONPATH=backend python scripts/list_catalyst_tables.py
```

### 3. Seed from AppSail (function-scope)

After tables exist and AppSail has `DATASTORE_MOCK=false`, set `CIP_SEED_TOKEN`
in AppSail env, then:

```bash
curl -sS -X POST \
  'https://cip-api-50044183252.development.catalystappsail.in/api/v1/admin/seed-datastore?limit=5' \
  -H 'X-CIP-SEED-TOKEN: <your-token>'

# full re-seed
curl -sS -X POST \
  'https://cip-api-50044183252.development.catalystappsail.in/api/v1/admin/seed-datastore?force=true' \
  -H 'X-CIP-SEED-TOKEN: <your-token>'
```

Or run the script locally with Self Client OAuth (`CATALYST_INIT_MODE=third_party`).
