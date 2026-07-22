# Catalyst Data Store — table plan

Create these in **Cloud Scale → Data Store** (Development first).
Names use `cip_` prefix to match `CATALYST_DATASTORE_TABLE_PREFIX`.

Align columns with [`Police_FIR_ER_Diagram.pdf`](../../Police_FIR_ER_Diagram.pdf)
and SQLAlchemy models under `backend/app/models/`.

## Wave 1 — masters (create first)

| Data Store table | ER entity | Priority |
|------------------|-----------|----------|
| `cip_case_status_master` | CaseStatusMaster | P0 |
| `cip_case_category` | CaseCategory | P0 |
| `cip_gravity_offence` | GravityOffence | P0 |
| `cip_state` | State | P0 |
| `cip_district` | District | P0 |
| `cip_unit_type` | UnitType | P0 |
| `cip_unit` | Unit | P0 |
| `cip_act` | Act | P0 |
| `cip_section` | Section | P0 |
| `cip_crime_head` | CrimeHead | P0 |
| `cip_crime_sub_head` | CrimeSubHead | P0 |

## Wave 2 — core FIR (required for `/api/v1/cases` on Catalyst)

Create these **four** tables first. Catalyst auto-adds `ROWID`, `CREATORID`,
`CREATEDTIME`, `MODIFIEDTIME` — do **not** add a separate PK column. Our API
maps `ROWID` → `case_master_id` / party IDs.

### Console path

1. [Catalyst Console](https://console.catalyst.zoho.com/) → your project → **Development**
2. **Cloud Scale** → **Storage** → **Data Store** → **Create Table**
3. Table name must match exactly (case-sensitive): `cip_...`
4. Add columns below → Save → set **Scopes** to allow App/Admin insert+read for your Self Client

### `cip_case_master`

| Column | Type | Mandatory | Notes |
|--------|------|-----------|-------|
| `crime_no` | Var Char (18) | Yes | Unique if console allows |
| `case_no` | Var Char (20) | Yes | |
| `crime_registered_date` | Date | No | ISO date string from API |
| `police_station_id` | Big Int | Yes | Unit ID (no FK enforce) |
| `case_category_id` | Big Int | Yes | |
| `gravity_offence_id` | Big Int | No | |
| `crime_major_head_id` | Big Int | No | |
| `crime_minor_head_id` | Big Int | No | |
| `case_status_id` | Big Int | Yes | |
| `court_id` | Big Int | No | |
| `incident_from_date` | Date Time | No | |
| `incident_to_date` | Date Time | No | |
| `info_received_ps_date` | Date Time | No | |
| `latitude` | Double / Var Char (20) | No | Adapter sends string decimal |
| `longitude` | Double / Var Char (20) | No | |
| `brief_facts` | Text | No | |

### `cip_victim`

| Column | Type | Mandatory |
|--------|------|-----------|
| `case_master_id` | Big Int | Yes (parent `ROWID`) |
| `victim_name` | Var Char (150) | Yes |
| `age_year` | Big Int | No |
| `gender_id` | Var Char (1) | No |
| `victim_police` | Var Char (1) | No |

### `cip_accused`

| Column | Type | Mandatory |
|--------|------|-----------|
| `case_master_id` | Big Int | Yes |
| `accused_name` | Var Char (150) | Yes |
| `age_year` | Big Int | No |
| `gender_id` | Var Char (1) | No |
| `person_id` | Var Char (10) | No |

### `cip_act_section_association`

| Column | Type | Mandatory |
|--------|------|-----------|
| `case_master_id` | Big Int | Yes |
| `act_id` | Var Char (20) | Yes |
| `section_id` | Var Char (20) | Yes |
| `act_order_id` | Big Int | Yes (default 1) |
| `section_order_id` | Big Int | Yes (default 1) |

| Data Store table | ER entity | Priority |
|------------------|-----------|----------|
| `cip_case_master` | CaseMaster | P0 |
| `cip_accused` | Accused | P0 |
| `cip_victim` | Victim | P0 |
| `cip_complainant_details` | ComplainantDetails | P1 |
| `cip_act_section_association` | ActSectionAssociation | P1 |

## Wave 3 — extended

| Data Store table | ER entity | Priority |
|------------------|-----------|----------|
| `cip_arrest_surrender` | ArrestSurrender | P1 |
| `cip_chargesheet_details` | ChargesheetDetails | P2 |
| `cip_employee` | Employee | P2 |
| `cip_court` | Court | P2 |
| `cip_rank` / `cip_designation` | Rank / Designation | P2 |
| Lookup masters (caste/religion/occupation) | *Master | P2 |

## Companion Catalyst stores (not Data Store)

| Store | Purpose | Suggested name |
|-------|---------|----------------|
| **NoSQL** | RAG documents | `cip_rag_documents` (`doc_id` PK) |
| **Stratus** | FIR PDFs / scans | bucket `cip-fir-docs-...` |
| **Cache** | Hot analytics | segment `cip_ai` / `cip_analytics` |

## Console steps (per table)

1. Catalyst → Cloud Scale → **Data Store** → Create Table.
2. Name = `cip_...` from above.
3. Add columns matching the model (start with PK + essential FKs + display fields).
4. Note table creation in standup when FE depends on live Catalyst data.

Local Postgres remains the active target until Wave 1–2 exist in Data Store **or**
AppSail runs against a provisioned DB explicitly documented for judges.

## Strategy overview

See [`datastore_strategy.md`](datastore_strategy.md).
