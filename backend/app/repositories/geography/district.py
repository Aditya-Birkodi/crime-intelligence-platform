"""Repository stub for `District`.

TODO: District under State.
"""

from __future__ import annotations

from app.repositories.base import BaseRepository


class DistrictRepository(BaseRepository[object, int]):
    """Persistence for `District`.

    TODO: Implement against SQLAlchemy / Catalyst Data Store.
    """

    def get_by_id(self, entity_id: int) -> object | None:
        raise NotImplementedError("TODO: Implement DistrictRepository.get_by_id")

    def list_all(self, *, limit: int = 100, offset: int = 0) -> list[object]:
        raise NotImplementedError("TODO: Implement DistrictRepository.list")

    def add(self, entity: object) -> object:
        raise NotImplementedError("TODO: Implement DistrictRepository.add")

    def update(self, entity: object) -> object:
        raise NotImplementedError("TODO: Implement DistrictRepository.update")

    def delete(self, entity_id: int) -> None:
        raise NotImplementedError("TODO: Implement DistrictRepository.delete")
