"""Repository stub for `Section`.

TODO: Section under an Act; FK ActCode.
"""

from __future__ import annotations

from app.repositories.base import BaseRepository


class SectionRepository(BaseRepository[object, int]):
    """Persistence for `Section`.

    TODO: Implement against SQLAlchemy / Catalyst Data Store.
    """

    def get_by_id(self, entity_id: int) -> object | None:
        raise NotImplementedError("TODO: Implement SectionRepository.get_by_id")

    def list_all(self, *, limit: int = 100, offset: int = 0) -> list[object]:
        raise NotImplementedError("TODO: Implement SectionRepository.list")

    def add(self, entity: object) -> object:
        raise NotImplementedError("TODO: Implement SectionRepository.add")

    def update(self, entity: object) -> object:
        raise NotImplementedError("TODO: Implement SectionRepository.update")

    def delete(self, entity_id: int) -> None:
        raise NotImplementedError("TODO: Implement SectionRepository.delete")
