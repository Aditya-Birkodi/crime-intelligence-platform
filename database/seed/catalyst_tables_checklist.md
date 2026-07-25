# Catalyst Data Store — console create checklist (Wave 2)

**Console:** https://console.catalyst.zoho.in → project `50116000000022364` → **Development**
**Path:** Cloud Scale → Storage → Data Store → Create Table

Do **not** add a custom primary key. Catalyst adds `ROWID`, `CREATORID`, `CREATEDTIME`, `MODIFIEDTIME`.

## Critical: use Big Int for every ROWID / FK

Catalyst `ROWID` values are **17-digit** numbers (e.g. `50116000000030053`).

| Wrong type | What happens |
|------------|----------------|
| **Int** (max 10 digits) | Values truncate → `5011600000` — joins break |
| Double | Precision loss on large IDs |

**You cannot change a column’s data type after create.** Recreate the table if any FK was created as Int.

All of these columns **must** be **Big Int**:

- `case_master_id` (every child table)
- `accused_master_id` (`cip_arrest_surrender`)
- Optional lookup ids that may grow large (`police_person_id`, `court_id`, …) — prefer Big Int

## Status (2026-07-25)

| Table | Rows | Notes |
|-------|------|--------|
| `cip_case_master` | **221** | OK — API `/api/v1/cases` returns them |
| `cip_victim` | 2 | `case_master_id` truncated (column is Int) |
| `cip_accused` | 3 | same truncation |
| `cip_act_section_association` | 2 | same truncation |
| complainants / occurrence / arrests / chargesheets | 0 | not seeded yet |

### Fix child tables (required before re-seed)

For each broken child table:

1. Data Store → open table → **Delete table** (or create a new table with a `_v2` name and update AppSail / seed names).
2. Recreate with columns below — **`case_master_id` = Big Int**, mandatory.
3. Then run:

```bash
python3 database/seed/seed_catalyst_via_cli.py --skip-masters --children-only
```

## 1. `cip_case_master`

| Column | Type | Mandatory |
|--------|------|-----------|
| crime_no | Var Char (18) | Yes |
| case_no | Var Char (20) | Yes |
| crime_registered_date | Date | No |
| police_person_id | Big Int | No |
| police_station_id | Big Int | Yes |
| case_category_id | Big Int | Yes |
| gravity_offence_id | Big Int | No |
| crime_major_head_id | Big Int | No |
| crime_minor_head_id | Big Int | No |
| case_status_id | Big Int | Yes |
| court_id | Big Int | No |
| incident_from_date | Date Time | No |
| incident_to_date | Date Time | No |
| info_received_ps_date | Date Time | No |
| latitude | Var Char (20) | No |
| longitude | Var Char (20) | No |
| brief_facts | Text | No |

## 2. `cip_victim`

| Column | Type | Mandatory |
|--------|------|-----------|
| case_master_id | **Big Int** | Yes |
| victim_name | Var Char (150) | Yes |
| age_year | Big Int | No |
| gender_id | Var Char (1) | No |
| victim_police | Var Char (1) | No |

## 3. `cip_accused`

| Column | Type | Mandatory |
|--------|------|-----------|
| case_master_id | **Big Int** | Yes |
| accused_name | Var Char (150) | Yes |
| age_year | Big Int | No |
| gender_id | Var Char (1) | No |
| person_id | Var Char (10) | No |

## 4. `cip_act_section_association`

| Column | Type | Mandatory |
|--------|------|-----------|
| case_master_id | **Big Int** | Yes |
| act_id | Var Char (20) | Yes |
| section_id | Var Char (20) | Yes |
| act_order_id | Big Int | Yes |
| section_order_id | Big Int | Yes |

## 5. `cip_complainant_details`

| Column | Type | Mandatory |
|--------|------|-----------|
| case_master_id | **Big Int** | Yes |
| complainant_name | Var Char (150) | Yes |
| age_year | Big Int | No |
| gender_id | Var Char (1) | No |
| occupation_id | Big Int | No |
| religion_id | Big Int | No |
| caste_id | Big Int | No |

## 6. `cip_inv_occurance_time`

| Column | Type | Mandatory |
|--------|------|-----------|
| case_master_id | **Big Int** | Yes |
| occurrence_from | Date Time | No |
| occurrence_to | Date Time | No |
| place_of_occurrence | Var Char (255) | No |
| beat_number | Var Char (20) | No |
| distance_from_ps_km | Var Char (20) | No |
| direction_from_ps | Var Char (50) | No |
| village_or_city | Var Char (100) | No |

## 7. `cip_arrest_surrender`

| Column | Type | Mandatory |
|--------|------|-----------|
| case_master_id | **Big Int** | Yes |
| arrest_surrender_type_id | Big Int | No |
| arrest_surrender_date | Date Time | No |
| arrest_surrender_state_id | Big Int | No |
| arrest_surrender_district_id | Big Int | No |
| police_station_id | Big Int | No |
| io_id | Big Int | No |
| court_id | Big Int | No |
| accused_master_id | **Big Int** | No |
| is_accused | Boolean | No |
| is_complainant_accused | Boolean | No |

## 8. `cip_chargesheet_details`

| Column | Type | Mandatory |
|--------|------|-----------|
| case_master_id | **Big Int** | Yes |
| cs_date | Date | No |
| cs_type | Var Char (50) | No |
| police_person_id | Big Int | No |

## Verify after recreate

In Schema View, confirm `case_master_id` shows **bigint**, not **int**.

Then:

```bash
python3 database/seed/seed_catalyst_via_cli.py --skip-masters --children-only
curl -sS 'https://cip-api-50044183252.development.catalystappsail.in/api/v1/cases/50116000000030053' | python3 -m json.tool | head -40
```

Victims / accused / act_sections should be non-empty.
