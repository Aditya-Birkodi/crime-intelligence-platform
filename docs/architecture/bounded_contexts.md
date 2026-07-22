# Bounded Contexts

Aligned to [`Police_FIR_ER_Diagram.pdf`](../../Police_FIR_ER_Diagram.pdf).

| Context | Path | Entities |
|---------|------|----------|
| Case | `backend/app/models/case` | CaseMaster, ComplainantDetails, Victim, Accused, ArrestSurrender, ActSectionAssociation, ChargesheetDetails, Inv_OccuranceTime, inv_arrestsurrenderaccused |
| Legal | `backend/app/models/legal` | Act, Section, CrimeHead, CrimeSubHead, CrimeHeadActSection |
| Geography | `backend/app/models/geography` | State, District, Court, Unit, UnitType |
| Personnel | `backend/app/models/personnel` | Employee, Rank, Designation |
| Lookups | `backend/app/models/lookups` | CaseCategory, GravityOffence, CaseStatusMaster, CasteMaster, ReligionMaster, OccupationMaster |

Aggregate root (future): **CaseMaster**.

**TODO:** Document invariants (CrimeNo uniqueness per station/category/year, etc.).
