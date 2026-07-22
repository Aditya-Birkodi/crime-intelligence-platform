"""Repository stub for `Act`.

TODO: Legal act master (e.g. IPC, NDPS); PK ActCode.
"""

from __future__ import annotations

from app.repositories.base import BaseRepository


class ActRepository(BaseRepository[object, int]):
    """Persistence for `Act`.

    TODO: Implement against SQLAlchemy / Catalyst Data Store.
    """

    def get_by_id(self, entity_id: int) -> object | None:
        raise NotImplementedError("TODO: Implement ActRepository.get_by_id")

    def list_all(self, *, limit: int = 100, offset: int = 0) -> list[object]:
        raise NotImplementedError("TODO: Implement ActRepository.list")

    def add(self, entity: object) -> object:
        raise NotImplementedError("TODO: Implement ActRepository.add")

    def update(self, entity: object) -> object:
        raise NotImplementedError("TODO: Implement ActRepository.update")

    def delete(self, entity_id: int) -> None:
        raise NotImplementedError("TODO: Implement ActRepository.delete")
