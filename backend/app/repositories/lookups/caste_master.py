"""Repository stub for `CasteMaster`.

TODO: Caste lookup for complainants.
"""

from __future__ import annotations

from app.repositories.base import BaseRepository


class CasteMasterRepository(BaseRepository[object, int]):
    """Persistence for `CasteMaster`.

    TODO: Implement against SQLAlchemy / Catalyst Data Store.
    """

    def get_by_id(self, entity_id: int) -> object | None:
        raise NotImplementedError("TODO: Implement CasteMasterRepository.get_by_id")

    def list_all(self, *, limit: int = 100, offset: int = 0) -> list[object]:
        raise NotImplementedError("TODO: Implement CasteMasterRepository.list")

    def add(self, entity: object) -> object:
        raise NotImplementedError("TODO: Implement CasteMasterRepository.add")

    def update(self, entity: object) -> object:
        raise NotImplementedError("TODO: Implement CasteMasterRepository.update")

    def delete(self, entity_id: int) -> None:
        raise NotImplementedError("TODO: Implement CasteMasterRepository.delete")
