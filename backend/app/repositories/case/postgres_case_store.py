"""Postgres-backed CaseStore (local / CI)."""

from __future__ import annotations

from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.case.accused import Accused
from app.models.case.act_section_association import ActSectionAssociation
from app.models.case.case_master import CaseMaster
from app.models.case.victim import Victim
from app.repositories.case.case_master import CaseMasterRepository
from app.schemas.case.case_master import (
    AccusedCreate,
    AccusedRead,
    ActSectionCreate,
    CaseMasterCreate,
    CaseMasterDetail,
    CaseMasterRead,
    VictimCreate,
)


class PostgresCaseStore:
    def __init__(self, session: Session) -> None:
        self._session = session
        self._repo = CaseMasterRepository(session)

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
    ) -> tuple[list[CaseMasterRead], int]:
        items, total = self._repo.list_filtered(
            police_station_id=police_station_id,
            case_status_id=case_status_id,
            crime_major_head_id=crime_major_head_id,
            registered_from=registered_from,
            registered_to=registered_to,
            limit=limit,
            offset=offset,
        )
        return [CaseMasterRead.model_validate(c) for c in items], total

    def get_detail(self, case_master_id: int) -> CaseMasterDetail | None:
        entity = self._repo.get_by_id(case_master_id)
        if entity is None:
            return None
        return CaseMasterDetail.model_validate(entity)

    def get_by_crime_no(self, crime_no: str) -> CaseMasterRead | None:
        entity = self._repo.get_by_crime_no(crime_no)
        if entity is None:
            return None
        return CaseMasterRead.model_validate(entity)

    def list_accused(self, *, limit: int = 2000) -> list[AccusedRead]:
        rows = self._session.scalars(select(Accused).limit(limit)).all()
        return [AccusedRead.model_validate(r) for r in rows]

    def create(self, payload: CaseMasterCreate, *, case_no: str) -> CaseMasterDetail:
        entity = CaseMaster(
            crime_no=payload.crime_no,
            case_no=case_no,
            crime_registered_date=payload.crime_registered_date,
            police_station_id=payload.police_station_id,
            case_category_id=payload.case_category_id,
            gravity_offence_id=payload.gravity_offence_id,
            crime_major_head_id=payload.crime_major_head_id,
            crime_minor_head_id=payload.crime_minor_head_id,
            case_status_id=payload.case_status_id,
            court_id=payload.court_id,
            incident_from_date=payload.incident_from_date,
            incident_to_date=payload.incident_to_date,
            info_received_ps_date=payload.info_received_ps_date,
            latitude=payload.latitude,
            longitude=payload.longitude,
            brief_facts=payload.brief_facts,
            victims=[
                Victim(
                    victim_name=v.victim_name,
                    age_year=v.age_year,
                    gender_id=v.gender_id,
                    victim_police=v.victim_police,
                )
                for v in payload.victims
            ],
            accused=[
                Accused(
                    accused_name=a.accused_name,
                    age_year=a.age_year,
                    gender_id=a.gender_id,
                    person_id=a.person_id,
                )
                for a in payload.accused
            ],
            act_sections=[
                ActSectionAssociation(
                    act_id=s.act_id,
                    section_id=s.section_id,
                    act_order_id=s.act_order_id,
                    section_order_id=s.section_order_id,
                )
                for s in payload.act_sections
            ],
        )
        created = self._repo.add(entity)
        self._session.commit()
        detail = self.get_detail(created.case_master_id)
        assert detail is not None
        return detail

    def add_victim(
        self, case_master_id: int, payload: VictimCreate
    ) -> CaseMasterDetail:
        case = self._repo.get_by_id(case_master_id)
        if case is None:
            raise KeyError(case_master_id)
        case.victims.append(
            Victim(
                victim_name=payload.victim_name,
                age_year=payload.age_year,
                gender_id=payload.gender_id,
                victim_police=payload.victim_police,
            )
        )
        self._session.commit()
        detail = self.get_detail(case_master_id)
        assert detail is not None
        return detail

    def add_accused(
        self, case_master_id: int, payload: AccusedCreate
    ) -> CaseMasterDetail:
        case = self._repo.get_by_id(case_master_id)
        if case is None:
            raise KeyError(case_master_id)
        case.accused.append(
            Accused(
                accused_name=payload.accused_name,
                age_year=payload.age_year,
                gender_id=payload.gender_id,
                person_id=payload.person_id,
            )
        )
        self._session.commit()
        detail = self.get_detail(case_master_id)
        assert detail is not None
        return detail

    def add_act_section(
        self, case_master_id: int, payload: ActSectionCreate
    ) -> CaseMasterDetail:
        case = self._repo.get_by_id(case_master_id)
        if case is None:
            raise KeyError(case_master_id)
        case.act_sections.append(
            ActSectionAssociation(
                act_id=payload.act_id,
                section_id=payload.section_id,
                act_order_id=payload.act_order_id,
                section_order_id=payload.section_order_id,
            )
        )
        self._session.commit()
        detail = self.get_detail(case_master_id)
        assert detail is not None
        return detail
