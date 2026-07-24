"""CaseMaster repository — SQLAlchemy persistence."""

from __future__ import annotations

from datetime import date

from sqlalchemy import Select, func, select
from sqlalchemy.orm import Session, selectinload
from sqlalchemy.sql.elements import ColumnElement

from app.models.case.case_master import CaseMaster
from app.repositories.base import BaseRepository


class CaseMasterRepository(BaseRepository[CaseMaster, int]):
    def __init__(self, session: Session) -> None:
        self._session = session

    def get_by_id(self, entity_id: int) -> CaseMaster | None:
        stmt = (
            select(CaseMaster)
            .where(CaseMaster.case_master_id == entity_id)
            .options(
                selectinload(CaseMaster.victims),
                selectinload(CaseMaster.accused),
                selectinload(CaseMaster.complainants),
                selectinload(CaseMaster.act_sections),
                selectinload(CaseMaster.occurrence),
                selectinload(CaseMaster.arrests),
                selectinload(CaseMaster.chargesheets),
            )
        )
        return self._session.scalar(stmt)

    def list_all(self, *, limit: int = 100, offset: int = 0) -> list[CaseMaster]:
        stmt = (
            select(CaseMaster)
            .order_by(CaseMaster.case_master_id.desc())
            .limit(limit)
            .offset(offset)
        )
        return list(self._session.scalars(stmt).all())

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
    ) -> tuple[list[CaseMaster], int]:
        filters: list[ColumnElement[bool]] = []
        if police_station_id is not None:
            filters.append(CaseMaster.police_station_id == police_station_id)
        if case_status_id is not None:
            filters.append(CaseMaster.case_status_id == case_status_id)
        if crime_major_head_id is not None:
            filters.append(CaseMaster.crime_major_head_id == crime_major_head_id)
        if crime_no is not None:
            filters.append(CaseMaster.crime_no == crime_no)
        if registered_from is not None:
            filters.append(CaseMaster.crime_registered_date >= registered_from)
        if registered_to is not None:
            filters.append(CaseMaster.crime_registered_date <= registered_to)

        base: Select[tuple[CaseMaster]] = select(CaseMaster)
        count_stmt = select(func.count()).select_from(CaseMaster)
        if filters:
            base = base.where(*filters)
            count_stmt = count_stmt.where(*filters)

        total = int(self._session.scalar(count_stmt) or 0)
        stmt = (
            base.order_by(CaseMaster.case_master_id.desc()).limit(limit).offset(offset)
        )
        rows = list(self._session.scalars(stmt).all())
        return rows, total

    def add(self, entity: CaseMaster) -> CaseMaster:
        self._session.add(entity)
        self._session.flush()
        self._session.refresh(entity)
        return entity

    def update(self, entity: CaseMaster) -> CaseMaster:
        self._session.add(entity)
        self._session.flush()
        self._session.refresh(entity)
        return entity

    def delete(self, entity_id: int) -> None:
        entity = self.get_by_id(entity_id)
        if entity is not None:
            self._session.delete(entity)
            self._session.flush()

    def get_by_crime_no(self, crime_no: str) -> CaseMaster | None:
        stmt = select(CaseMaster).where(CaseMaster.crime_no == crime_no)
        return self._session.scalar(stmt)
