"""Repository stub for `CrimeHead`.

TODO: Major crime head / crime group.
"""

from __future__ import annotations

from app.repositories.base import BaseRepository


class CrimeHeadRepository(BaseRepository[object, int]):
    """Persistence for `CrimeHead`.

    TODO: Implement against SQLAlchemy / Catalyst Data Store.
    """

    def get_by_id(self, entity_id: int) -> object | None:
        raise NotImplementedError("TODO: Implement CrimeHeadRepository.get_by_id")

    def list_all(self, *, limit: int = 100, offset: int = 0) -> list[object]:
        raise NotImplementedError("TODO: Implement CrimeHeadRepository.list")

    def add(self, entity: object) -> object:
        raise NotImplementedError("TODO: Implement CrimeHeadRepository.add")

    def update(self, entity: object) -> object:
        raise NotImplementedError("TODO: Implement CrimeHeadRepository.update")

    def delete(self, entity_id: int) -> None:
        raise NotImplementedError("TODO: Implement CrimeHeadRepository.delete")
