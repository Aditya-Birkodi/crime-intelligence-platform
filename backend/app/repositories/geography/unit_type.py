"""Repository stub for `UnitType`.

TODO: Unit type (Police Station, Circle Office, …).
"""

from __future__ import annotations

from app.repositories.base import BaseRepository


class UnitTypeRepository(BaseRepository[object, int]):
    """Persistence for `UnitType`.

    TODO: Implement against SQLAlchemy / Catalyst Data Store.
    """

    def get_by_id(self, entity_id: int) -> object | None:
        raise NotImplementedError("TODO: Implement UnitTypeRepository.get_by_id")

    def list_all(self, *, limit: int = 100, offset: int = 0) -> list[object]:
        raise NotImplementedError("TODO: Implement UnitTypeRepository.list")

    def add(self, entity: object) -> object:
        raise NotImplementedError("TODO: Implement UnitTypeRepository.add")

    def update(self, entity: object) -> object:
        raise NotImplementedError("TODO: Implement UnitTypeRepository.update")

    def delete(self, entity_id: int) -> None:
        raise NotImplementedError("TODO: Implement UnitTypeRepository.delete")
