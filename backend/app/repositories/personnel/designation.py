"""Repository stub for `Designation`.

TODO: Designation (IO, SHO, …).
"""

from __future__ import annotations

from app.repositories.base import BaseRepository


class DesignationRepository(BaseRepository[object, int]):
    """Persistence for `Designation`.

    TODO: Implement against SQLAlchemy / Catalyst Data Store.
    """

    def get_by_id(self, entity_id: int) -> object | None:
        raise NotImplementedError("TODO: Implement DesignationRepository.get_by_id")

    def list_all(self, *, limit: int = 100, offset: int = 0) -> list[object]:
        raise NotImplementedError("TODO: Implement DesignationRepository.list")

    def add(self, entity: object) -> object:
        raise NotImplementedError("TODO: Implement DesignationRepository.add")

    def update(self, entity: object) -> object:
        raise NotImplementedError("TODO: Implement DesignationRepository.update")

    def delete(self, entity_id: int) -> None:
        raise NotImplementedError("TODO: Implement DesignationRepository.delete")
