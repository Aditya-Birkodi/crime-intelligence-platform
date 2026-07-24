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

## AppSail

After regenerating `appsail_datastore.json`:

```bash
catalyst deploy --only appsail:cip-api
```
