"""Repository stub for `State`.

TODO: State master; referenced by District, Unit, Court, ArrestSurrender.
"""

from __future__ import annotations

from app.repositories.base import BaseRepository


class StateRepository(BaseRepository[object, int]):
    """Persistence for `State`.

    TODO: Implement against SQLAlchemy / Catalyst Data Store.
    """

    def get_by_id(self, entity_id: int) -> object | None:
        raise NotImplementedError("TODO: Implement StateRepository.get_by_id")

    def list_all(self, *, limit: int = 100, offset: int = 0) -> list[object]:
        raise NotImplementedError("TODO: Implement StateRepository.list")

    def add(self, entity: object) -> object:
        raise NotImplementedError("TODO: Implement StateRepository.add")

    def update(self, entity: object) -> object:
        raise NotImplementedError("TODO: Implement StateRepository.update")

    def delete(self, entity_id: int) -> None:
        raise NotImplementedError("TODO: Implement StateRepository.delete")
