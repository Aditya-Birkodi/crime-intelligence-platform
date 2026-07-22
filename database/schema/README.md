# Database schema ownership

Canonical FIR domain schema is defined by
[`Police_FIR_ER_Diagram.pdf`](../../Police_FIR_ER_Diagram.pdf).

Subfolders mirror backend bounded contexts:

- `case/` — CaseMaster and related case entities
- `legal/` — Act, Section, CrimeHead, …
- `geography/` — State, District, Unit, Court, …
- `personnel/` — Employee, Rank, Designation
- `lookups/` — CaseCategory, GravityOffence, masters

**TODO:** Place DDL drafts or Catalyst Data Store table definitions here once
columns are implemented. Prefer Alembic migrations under `../migrations/` for
local PostgreSQL; map tables to Catalyst Data Store for production.
