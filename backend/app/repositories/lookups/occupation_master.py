"""Repository stub for `OccupationMaster`.

TODO: Occupation lookup for complainants.
"""

from __future__ import annotations

from app.repositories.base import BaseRepository


class OccupationMasterRepository(BaseRepository[object, int]):
    """Persistence for `OccupationMaster`.

    TODO: Implement against SQLAlchemy / Catalyst Data Store.
    """

    def get_by_id(self, entity_id: int) -> object | None:
        raise NotImplementedError(
            "TODO: Implement OccupationMasterRepository.get_by_id"
        )

    def list_all(self, *, limit: int = 100, offset: int = 0) -> list[object]:
        raise NotImplementedError("TODO: Implement OccupationMasterRepository.list")

    def add(self, entity: object) -> object:
        raise NotImplementedError("TODO: Implement OccupationMasterRepository.add")

    def update(self, entity: object) -> object:
        raise NotImplementedError("TODO: Implement OccupationMasterRepository.update")

    def delete(self, entity_id: int) -> None:
        raise NotImplementedError("TODO: Implement OccupationMasterRepository.delete")
