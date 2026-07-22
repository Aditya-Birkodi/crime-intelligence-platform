"""Repository stub for `Rank`.

TODO: Police rank hierarchy.
"""

from __future__ import annotations

from app.repositories.base import BaseRepository


class RankRepository(BaseRepository[object, int]):
    """Persistence for `Rank`.

    TODO: Implement against SQLAlchemy / Catalyst Data Store.
    """

    def get_by_id(self, entity_id: int) -> object | None:
        raise NotImplementedError("TODO: Implement RankRepository.get_by_id")

    def list_all(self, *, limit: int = 100, offset: int = 0) -> list[object]:
        raise NotImplementedError("TODO: Implement RankRepository.list")

    def add(self, entity: object) -> object:
        raise NotImplementedError("TODO: Implement RankRepository.add")

    def update(self, entity: object) -> object:
        raise NotImplementedError("TODO: Implement RankRepository.update")

    def delete(self, entity_id: int) -> None:
        raise NotImplementedError("TODO: Implement RankRepository.delete")
