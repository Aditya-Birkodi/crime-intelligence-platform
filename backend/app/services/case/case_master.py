"""CaseMaster application service."""

from __future__ import annotations

from datetime import date

from app.exceptions.base import NotFoundError, ValidationError
from app.repositories.case.case_store import CaseStore
from app.schemas.case.case_master import (
    AccusedCreate,
    ActSectionCreate,
    CaseMasterCreate,
    CaseMasterDetail,
    CaseMasterListResponse,
    VictimCreate,
)
from app.utils.crime_no import parse_crime_no


class CaseMasterService:
    def __init__(self, store: CaseStore) -> None:
        self._store = store

    def list_cases(
        self,
        *,
        police_station_id: int | None = None,
        case_status_id: int | None = None,
        crime_major_head_id: int | None = None,
        registered_from: date | None = None,
        registered_to: date | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> CaseMasterListResponse:
        items, total = self._store.list_filtered(
            police_station_id=police_station_id,
            case_status_id=case_status_id,
            crime_major_head_id=crime_major_head_id,
            registered_from=registered_from,
            registered_to=registered_to,
            limit=limit,
            offset=offset,
        )
        return CaseMasterListResponse(
            items=items,
            total=total,
            limit=limit,
            offset=offset,
        )

    def get_case(self, case_master_id: int) -> CaseMasterDetail:
        detail = self._store.get_detail(case_master_id)
        if detail is None:
            raise NotFoundError(f"Case {case_master_id} not found")
        return detail

    def create_case(self, payload: CaseMasterCreate) -> CaseMasterDetail:
        try:
            parsed = parse_crime_no(payload.crime_no)
        except ValueError as exc:
            raise ValidationError(str(exc)) from exc

        if self._store.get_by_crime_no(payload.crime_no) is not None:
            raise ValidationError(f"CrimeNo already exists: {payload.crime_no}")

        case_no = payload.case_no or parsed.case_no_suffix
        if case_no != parsed.case_no_suffix:
            case_no = payload.case_no

        return self._store.create(payload, case_no=case_no)

    def add_victim(
        self, case_master_id: int, payload: VictimCreate
    ) -> CaseMasterDetail:
        try:
            return self._store.add_victim(case_master_id, payload)
        except KeyError as exc:
            raise NotFoundError(f"Case {case_master_id} not found") from exc

    def add_accused(
        self, case_master_id: int, payload: AccusedCreate
    ) -> CaseMasterDetail:
        try:
            return self._store.add_accused(case_master_id, payload)
        except KeyError as exc:
            raise NotFoundError(f"Case {case_master_id} not found") from exc

    def add_act_section(
        self, case_master_id: int, payload: ActSectionCreate
    ) -> CaseMasterDetail:
        try:
            return self._store.add_act_section(case_master_id, payload)
        except KeyError as exc:
            raise NotFoundError(f"Case {case_master_id} not found") from exc
