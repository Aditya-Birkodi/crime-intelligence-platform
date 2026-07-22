# FIR ER Diagram Reference

Source: [`Police_FIR_ER_Diagram.pdf`](../../Police_FIR_ER_Diagram.pdf)
(Karnataka Police Department — Police FIR System).

## Core entities

| Table | Role |
|-------|------|
| CaseMaster | FIR/case aggregate; CrimeNo / CaseNo; GPS; BriefFacts |
| ComplainantDetails | Complainants (1:N) |
| Victim | Victims (1:N) |
| Accused | Accused (1:N) |
| ArrestSurrender | Arrest/surrender events |
| ActSectionAssociation | Acts & sections applied to a case |
| ChargesheetDetails | Final report / chargesheet |
| Inv_OccuranceTime | Occurrence time/location (1:1) |
| Act / Section | Legal masters |
| CrimeHead / CrimeSubHead / CrimeHeadActSection | Crime classification |
| State / District / Court / Unit / UnitType | Geography & org |
| Employee / Rank / Designation | Personnel |
| CaseCategory / GravityOffence / CaseStatusMaster | Case lookups |
| CasteMaster / ReligionMaster / OccupationMaster | Demographic lookups |

## CrimeNo format

`1-digit Case Category` + `4-digit District ID` + `4-digit Police Station ID`
+ `4-digit Year` + `5-digit Running Serial` (18 digits total).

Examples from the PDF: FIR `104430006202600001`, UDR `304430006202600001`,
Zero FIR `804430006202600001`, PAR `404430006202600001`.

## Relationship highlights

- CaseMaster 1:N → Victim, Accused, ArrestSurrender, ComplainantDetails, ActSectionAssociation
- CaseMaster 1:1 → Inv_OccuranceTime
- Act 1:N → Section; CrimeHead 1:N → CrimeSubHead
- Unit hierarchy via `ParentUnit`

**TODO:** Formalize ER into SQLAlchemy models and Catalyst Data Store tables
(scaffold placeholders exist under `backend/app/models/*` — no columns yet).
