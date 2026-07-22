"""Repository stub for `Court`.

TODO: Court master; District/State FKs.
"""

from __future__ import annotations

from app.repositories.base import BaseRepository


class CourtRepository(BaseRepository[object, int]):
    """Persistence for `Court`.

    TODO: Implement against SQLAlchemy / Catalyst Data Store.
    """

    def get_by_id(self, entity_id: int) -> object | None:
        raise NotImplementedError("TODO: Implement CourtRepository.get_by_id")

    def list_all(self, *, limit: int = 100, offset: int = 0) -> list[object]:
        raise NotImplementedError("TODO: Implement CourtRepository.list")

    def add(self, entity: object) -> object:
        raise NotImplementedError("TODO: Implement CourtRepository.add")

    def update(self, entity: object) -> object:
        raise NotImplementedError("TODO: Implement CourtRepository.update")

    def delete(self, entity_id: int) -> None:
        raise NotImplementedError("TODO: Implement CourtRepository.delete")
