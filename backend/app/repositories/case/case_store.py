"""Case persistence port — Postgres or Catalyst Data Store."""

from __future__ import annotations

from datetime import date
from typing import Protocol

from app.schemas.case.case_master import (
    AccusedCreate,
    AccusedRead,
    ActSectionCreate,
    CaseMasterCreate,
    CaseMasterDetail,
    CaseMasterRead,
    VictimCreate,
)


class CaseStore(Protocol):
    """Persistence boundary for FIR / CaseMaster operations."""

    def list_filtered(
        self,
        *,
        police_station_id: int | None = None,
        case_status_id: int | None = None,
        crime_major_head_id: int | None = None,
        registered_from: date | None = None,
        registered_to: date | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> tuple[list[CaseMasterRead], int]: ...

    def get_detail(self, case_master_id: int) -> CaseMasterDetail | None: ...

    def get_by_crime_no(self, crime_no: str) -> CaseMasterRead | None: ...

    def list_accused(self, *, limit: int = 2000) -> list[AccusedRead]: ...

    def create(
        self, payload: CaseMasterCreate, *, case_no: str
    ) -> CaseMasterDetail: ...

    def add_victim(
        self, case_master_id: int, payload: VictimCreate
    ) -> CaseMasterDetail: ...

    def add_accused(
        self, case_master_id: int, payload: AccusedCreate
    ) -> CaseMasterDetail: ...

    def add_act_section(
        self, case_master_id: int, payload: ActSectionCreate
    ) -> CaseMasterDetail: ...
