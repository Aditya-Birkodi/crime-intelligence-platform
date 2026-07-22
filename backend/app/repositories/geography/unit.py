"""Repository stub for `Unit`.

TODO: Police unit / station; hierarchical ParentUnit.
"""

from __future__ import annotations

from app.repositories.base import BaseRepository


class UnitRepository(BaseRepository[object, int]):
    """Persistence for `Unit`.

    TODO: Implement against SQLAlchemy / Catalyst Data Store.
    """

    def get_by_id(self, entity_id: int) -> object | None:
        raise NotImplementedError("TODO: Implement UnitRepository.get_by_id")

    def list_all(self, *, limit: int = 100, offset: int = 0) -> list[object]:
        raise NotImplementedError("TODO: Implement UnitRepository.list")

    def add(self, entity: object) -> object:
        raise NotImplementedError("TODO: Implement UnitRepository.add")

    def update(self, entity: object) -> object:
        raise NotImplementedError("TODO: Implement UnitRepository.update")

    def delete(self, entity_id: int) -> None:
        raise NotImplementedError("TODO: Implement UnitRepository.delete")
