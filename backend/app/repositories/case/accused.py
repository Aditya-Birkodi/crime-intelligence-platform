"""Repository stub for `Accused`.

TODO: Accused persons for a CaseMaster (1:N); PersonID sorting A1/A2/….
"""

from __future__ import annotations

from app.repositories.base import BaseRepository


class AccusedRepository(BaseRepository[object, int]):
    """Persistence for `Accused`.

    TODO: Implement against SQLAlchemy / Catalyst Data Store.
    """

    def get_by_id(self, entity_id: int) -> object | None:
        raise NotImplementedError("TODO: Implement AccusedRepository.get_by_id")

    def list_all(self, *, limit: int = 100, offset: int = 0) -> list[object]:
        raise NotImplementedError("TODO: Implement AccusedRepository.list")

    def add(self, entity: object) -> object:
        raise NotImplementedError("TODO: Implement AccusedRepository.add")

    def update(self, entity: object) -> object:
        raise NotImplementedError("TODO: Implement AccusedRepository.update")

    def delete(self, entity_id: int) -> None:
        raise NotImplementedError("TODO: Implement AccusedRepository.delete")
