"""Repository stub for `GravityOffence`.

TODO: Offence gravity (Heinous / Non-Heinous).
"""

from __future__ import annotations

from app.repositories.base import BaseRepository


class GravityOffenceRepository(BaseRepository[object, int]):
    """Persistence for `GravityOffence`.

    TODO: Implement against SQLAlchemy / Catalyst Data Store.
    """

    def get_by_id(self, entity_id: int) -> object | None:
        raise NotImplementedError("TODO: Implement GravityOffenceRepository.get_by_id")

    def list_all(self, *, limit: int = 100, offset: int = 0) -> list[object]:
        raise NotImplementedError("TODO: Implement GravityOffenceRepository.list")

    def add(self, entity: object) -> object:
        raise NotImplementedError("TODO: Implement GravityOffenceRepository.add")

    def update(self, entity: object) -> object:
        raise NotImplementedError("TODO: Implement GravityOffenceRepository.update")

    def delete(self, entity_id: int) -> None:
        raise NotImplementedError("TODO: Implement GravityOffenceRepository.delete")
