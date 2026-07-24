"""CaseStore backed by Catalyst Data Store (or local mock)."""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import Any

from app.integrations.catalyst.datastore import CatalystDataStoreClient
from app.schemas.case.arrest_surrender import ArrestSurrenderRead
from app.schemas.case.case_master import (
    AccusedCreate,
    AccusedRead,
    ActSectionCreate,
    ActSectionRead,
    CaseMasterCreate,
    CaseMasterDetail,
    CaseMasterRead,
    VictimCreate,
    VictimRead,
)
from app.schemas.case.chargesheet_details import ChargesheetDetailsRead
from app.schemas.case.complainant_details import (
    ComplainantDetailsCreate,
    ComplainantDetailsRead,
)
from app.schemas.case.inv_occurance_time import InvOccuranceTimeRead

_CASE = "case_master"
_VICTIM = "victim"
_ACCUSED = "accused"
_ACT_SECTION = "act_section_association"
_COMPLAINANT = "complainant_details"
_OCCURRENCE = "inv_occurance_time"
_ARREST = "arrest_surrender"
_CHARGESHEET = "chargesheet_details"


def _ser(value: Any) -> Any:
    if value is None:
        return None
    if isinstance(value, datetime | date):
        return value.isoformat()
    if isinstance(value, Decimal):
        return str(value)
    return value


def _row_to_case_read(row: dict[str, Any]) -> CaseMasterRead:
    row_id = int(row.get("ROWID") or row.get("case_master_id") or 0)
    return CaseMasterRead(
        case_master_id=row_id,
        crime_no=str(row.get("crime_no", "")),
        case_no=str(row.get("case_no", "")),
        crime_registered_date=_parse_date(row.get("crime_registered_date")),
        police_person_id=_opt_int(row.get("police_person_id")),
        police_station_id=int(row.get("police_station_id") or 0),
        case_category_id=int(row.get("case_category_id") or 0),
        gravity_offence_id=_opt_int(row.get("gravity_offence_id")),
        crime_major_head_id=_opt_int(row.get("crime_major_head_id")),
        crime_minor_head_id=_opt_int(row.get("crime_minor_head_id")),
        case_status_id=int(row.get("case_status_id") or 0),
        court_id=_opt_int(row.get("court_id")),
        incident_from_date=_parse_dt(row.get("incident_from_date")),
        incident_to_date=_parse_dt(row.get("incident_to_date")),
        info_received_ps_date=_parse_dt(row.get("info_received_ps_date")),
        latitude=_opt_decimal(row.get("latitude")),
        longitude=_opt_decimal(row.get("longitude")),
        brief_facts=row.get("brief_facts"),
    )


def _opt_int(value: Any) -> int | None:
    if value is None or value == "":
        return None
    return int(value)


def _opt_decimal(value: Any) -> Decimal | None:
    if value is None or value == "":
        return None
    return Decimal(str(value))


def _parse_date(value: Any) -> date | None:
    if value is None or value == "":
        return None
    if isinstance(value, date) and not isinstance(value, datetime):
        return value
    return date.fromisoformat(str(value)[:10])


def _parse_dt(value: Any) -> datetime | None:
    if value is None or value == "":
        return None
    if isinstance(value, datetime):
        return value
    text = str(value).replace("Z", "+00:00")
    return datetime.fromisoformat(text)


def _opt_bool(value: Any, default: bool = False) -> bool:
    if value is None or value == "":
        return default
    if isinstance(value, bool):
        return value
    return str(value).lower() in {"1", "true", "yes"}


class CatalystCaseStore:
    """FIR persistence via Catalyst Cloud Scale Data Store."""

    def __init__(self, client: CatalystDataStoreClient | None = None) -> None:
        self._ds = client or CatalystDataStoreClient()

    def list_filtered(
        self,
        *,
        police_station_id: int | None = None,
        case_status_id: int | None = None,
        crime_major_head_id: int | None = None,
        crime_no: str | None = None,
        registered_from: date | None = None,
        registered_to: date | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> tuple[list[CaseMasterRead], int]:
        rows = self._ds.get_paged_rows(_CASE, max_rows=2000)
        items = [_row_to_case_read(r) for r in rows]
        if police_station_id is not None:
            items = [c for c in items if c.police_station_id == police_station_id]
        if case_status_id is not None:
            items = [c for c in items if c.case_status_id == case_status_id]
        if crime_major_head_id is not None:
            items = [c for c in items if c.crime_major_head_id == crime_major_head_id]
        if crime_no is not None:
            items = [c for c in items if c.crime_no == crime_no]
        if registered_from is not None:
            items = [
                c
                for c in items
                if c.crime_registered_date
                and c.crime_registered_date >= registered_from
            ]
        if registered_to is not None:
            items = [
                c
                for c in items
                if c.crime_registered_date and c.crime_registered_date <= registered_to
            ]
        items.sort(key=lambda c: c.case_master_id, reverse=True)
        total = len(items)
        return items[offset : offset + limit], total

    def get_detail(self, case_master_id: int) -> CaseMasterDetail | None:
        row = self._ds.get_row(_CASE, case_master_id)
        if row is None:
            return None
        base = _row_to_case_read(row)
        victims = [
            VictimRead(
                victim_master_id=int(v.get("ROWID") or 0),
                case_master_id=case_master_id,
                victim_name=str(v.get("victim_name", "")),
                age_year=_opt_int(v.get("age_year")),
                gender_id=v.get("gender_id"),
                victim_police=v.get("victim_police"),
            )
            for v in self._ds.get_paged_rows(_VICTIM, max_rows=2000)
            if int(v.get("case_master_id") or 0) == case_master_id
        ]
        accused = [
            AccusedRead(
                accused_master_id=int(a.get("ROWID") or 0),
                case_master_id=case_master_id,
                accused_name=str(a.get("accused_name", "")),
                age_year=_opt_int(a.get("age_year")),
                gender_id=a.get("gender_id"),
                person_id=a.get("person_id"),
            )
            for a in self._ds.get_paged_rows(_ACCUSED, max_rows=2000)
            if int(a.get("case_master_id") or 0) == case_master_id
        ]
        complainants = [
            ComplainantDetailsRead(
                complainant_id=int(c.get("ROWID") or c.get("complainant_id") or 0),
                case_master_id=case_master_id,
                complainant_name=str(c.get("complainant_name", "")),
                age_year=_opt_int(c.get("age_year")),
                gender_id=c.get("gender_id"),
                occupation_id=_opt_int(c.get("occupation_id")),
                religion_id=_opt_int(c.get("religion_id")),
                caste_id=_opt_int(c.get("caste_id")),
            )
            for c in self._ds.get_paged_rows(_COMPLAINANT, max_rows=2000)
            if int(c.get("case_master_id") or 0) == case_master_id
        ]
        sections = [
            ActSectionRead(
                id=int(s.get("ROWID") or 0),
                case_master_id=case_master_id,
                act_id=str(s.get("act_id", "")),
                section_id=str(s.get("section_id", "")),
                act_order_id=int(s.get("act_order_id") or 1),
                section_order_id=int(s.get("section_order_id") or 1),
            )
            for s in self._ds.get_paged_rows(_ACT_SECTION, max_rows=2000)
            if int(s.get("case_master_id") or 0) == case_master_id
        ]
        occurrence: InvOccuranceTimeRead | None = None
        for occ in self._ds.get_paged_rows(_OCCURRENCE, max_rows=2000):
            if (
                int(occ.get("case_master_id") or occ.get("ROWID") or 0)
                != case_master_id
            ):
                continue
            occurrence = InvOccuranceTimeRead(
                case_master_id=case_master_id,
                occurrence_from=_parse_dt(occ.get("occurrence_from")),
                occurrence_to=_parse_dt(occ.get("occurrence_to")),
                place_of_occurrence=occ.get("place_of_occurrence"),
                beat_number=occ.get("beat_number"),
                distance_from_ps_km=_opt_decimal(occ.get("distance_from_ps_km")),
                direction_from_ps=occ.get("direction_from_ps"),
                village_or_city=occ.get("village_or_city"),
            )
            break
        arrests = [
            ArrestSurrenderRead(
                arrest_surrender_id=int(
                    a.get("ROWID") or a.get("arrest_surrender_id") or 0
                ),
                case_master_id=case_master_id,
                arrest_surrender_type_id=int(a.get("arrest_surrender_type_id") or 1),
                arrest_surrender_date=_parse_date(a.get("arrest_surrender_date")),
                arrest_surrender_state_id=_opt_int(a.get("arrest_surrender_state_id")),
                arrest_surrender_district_id=_opt_int(
                    a.get("arrest_surrender_district_id")
                ),
                police_station_id=_opt_int(a.get("police_station_id")),
                io_id=_opt_int(a.get("io_id")),
                court_id=_opt_int(a.get("court_id")),
                accused_master_id=_opt_int(a.get("accused_master_id")),
                is_accused=_opt_bool(a.get("is_accused"), True),
                is_complainant_accused=_opt_bool(
                    a.get("is_complainant_accused"), False
                ),
            )
            for a in self._ds.get_paged_rows(_ARREST, max_rows=2000)
            if int(a.get("case_master_id") or 0) == case_master_id
        ]
        chargesheets = [
            ChargesheetDetailsRead(
                cs_id=int(cs.get("ROWID") or cs.get("cs_id") or 0),
                case_master_id=case_master_id,
                cs_date=_parse_dt(cs.get("cs_date")),
                cs_type=str(cs.get("cs_type") or "A"),
                police_person_id=_opt_int(cs.get("police_person_id")),
            )
            for cs in self._ds.get_paged_rows(_CHARGESHEET, max_rows=2000)
            if int(cs.get("case_master_id") or 0) == case_master_id
        ]
        return CaseMasterDetail(
            **base.model_dump(),
            victims=victims,
            accused=accused,
            complainants=complainants,
            act_sections=sections,
            occurrence=occurrence,
            arrests=arrests,
            chargesheets=chargesheets,
        )

    def get_by_crime_no(self, crime_no: str) -> CaseMasterRead | None:
        for row in self._ds.get_paged_rows(_CASE, max_rows=2000):
            if str(row.get("crime_no")) == crime_no:
                return _row_to_case_read(row)
        return None

    def list_accused(self, *, limit: int = 2000) -> list[AccusedRead]:
        rows = self._ds.get_paged_rows(_ACCUSED, max_rows=limit)
        return [
            AccusedRead(
                accused_master_id=int(
                    a.get("ROWID") or a.get("accused_master_id") or 0
                ),
                case_master_id=int(a.get("case_master_id") or 0),
                accused_name=str(a.get("accused_name", "")),
                age_year=_opt_int(a.get("age_year")),
                gender_id=a.get("gender_id"),
                person_id=a.get("person_id"),
            )
            for a in rows
        ]

    def create(self, payload: CaseMasterCreate, *, case_no: str) -> CaseMasterDetail:
        case_row = {
            "crime_no": payload.crime_no,
            "case_no": case_no,
            "crime_registered_date": _ser(payload.crime_registered_date),
            "police_person_id": payload.police_person_id,
            "police_station_id": payload.police_station_id,
            "case_category_id": payload.case_category_id,
            "gravity_offence_id": payload.gravity_offence_id,
            "crime_major_head_id": payload.crime_major_head_id,
            "crime_minor_head_id": payload.crime_minor_head_id,
            "case_status_id": payload.case_status_id,
            "court_id": payload.court_id,
            "incident_from_date": _ser(payload.incident_from_date),
            "incident_to_date": _ser(payload.incident_to_date),
            "info_received_ps_date": _ser(payload.info_received_ps_date),
            "latitude": _ser(payload.latitude),
            "longitude": _ser(payload.longitude),
            "brief_facts": payload.brief_facts,
        }
        inserted = self._ds.insert_row(_CASE, case_row)
        case_id = int(inserted.get("ROWID") or inserted.get("case_master_id") or 0)

        for v in payload.victims:
            self._ds.insert_row(
                _VICTIM,
                {
                    "case_master_id": case_id,
                    "victim_name": v.victim_name,
                    "age_year": v.age_year,
                    "gender_id": v.gender_id,
                    "victim_police": v.victim_police,
                },
            )
        for a in payload.accused:
            self._ds.insert_row(
                _ACCUSED,
                {
                    "case_master_id": case_id,
                    "accused_name": a.accused_name,
                    "age_year": a.age_year,
                    "gender_id": a.gender_id,
                    "person_id": a.person_id,
                },
            )
        for c in payload.complainants:
            self._ds.insert_row(
                _COMPLAINANT,
                {
                    "case_master_id": case_id,
                    "complainant_name": c.complainant_name,
                    "age_year": c.age_year,
                    "gender_id": c.gender_id,
                    "occupation_id": c.occupation_id,
                    "religion_id": c.religion_id,
                    "caste_id": c.caste_id,
                },
            )
        for s in payload.act_sections:
            self._ds.insert_row(
                _ACT_SECTION,
                {
                    "case_master_id": case_id,
                    "act_id": s.act_id,
                    "section_id": s.section_id,
                    "act_order_id": s.act_order_id,
                    "section_order_id": s.section_order_id,
                },
            )

        detail = self.get_detail(case_id)
        assert detail is not None
        return detail

    def add_victim(
        self, case_master_id: int, payload: VictimCreate
    ) -> CaseMasterDetail:
        if self.get_detail(case_master_id) is None:
            raise KeyError(case_master_id)
        self._ds.insert_row(
            _VICTIM,
            {
                "case_master_id": case_master_id,
                "victim_name": payload.victim_name,
                "age_year": payload.age_year,
                "gender_id": payload.gender_id,
                "victim_police": payload.victim_police,
            },
        )
        detail = self.get_detail(case_master_id)
        assert detail is not None
        return detail

    def add_accused(
        self, case_master_id: int, payload: AccusedCreate
    ) -> CaseMasterDetail:
        if self.get_detail(case_master_id) is None:
            raise KeyError(case_master_id)
        self._ds.insert_row(
            _ACCUSED,
            {
                "case_master_id": case_master_id,
                "accused_name": payload.accused_name,
                "age_year": payload.age_year,
                "gender_id": payload.gender_id,
                "person_id": payload.person_id,
            },
        )
        detail = self.get_detail(case_master_id)
        assert detail is not None
        return detail

    def add_act_section(
        self, case_master_id: int, payload: ActSectionCreate
    ) -> CaseMasterDetail:
        if self.get_detail(case_master_id) is None:
            raise KeyError(case_master_id)
        self._ds.insert_row(
            _ACT_SECTION,
            {
                "case_master_id": case_master_id,
                "act_id": payload.act_id,
                "section_id": payload.section_id,
                "act_order_id": payload.act_order_id,
                "section_order_id": payload.section_order_id,
            },
        )
        detail = self.get_detail(case_master_id)
        assert detail is not None
        return detail

    def add_complainant(
        self, case_master_id: int, payload: ComplainantDetailsCreate
    ) -> CaseMasterDetail:
        if self.get_detail(case_master_id) is None:
            raise KeyError(case_master_id)
        self._ds.insert_row(
            _COMPLAINANT,
            {
                "case_master_id": case_master_id,
                "complainant_name": payload.complainant_name,
                "age_year": payload.age_year,
                "gender_id": payload.gender_id,
                "occupation_id": payload.occupation_id,
                "religion_id": payload.religion_id,
                "caste_id": payload.caste_id,
            },
        )
        detail = self.get_detail(case_master_id)
        assert detail is not None
        return detail
