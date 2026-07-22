"""Repository stub for `Inv_OccuranceTime`.

TODO: Occurrence time/location record (1:1 with CaseMaster per ER matrix).
"""

from __future__ import annotations

from app.repositories.base import BaseRepository


class InvOccuranceTimeRepository(BaseRepository[object, int]):
    """Persistence for `Inv_OccuranceTime`.

    TODO: Implement against SQLAlchemy / Catalyst Data Store.
    """

    def get_by_id(self, entity_id: int) -> object | None:
        raise NotImplementedError(
            "TODO: Implement InvOccuranceTimeRepository.get_by_id"
        )

    def list_all(self, *, limit: int = 100, offset: int = 0) -> list[object]:
        raise NotImplementedError("TODO: Implement InvOccuranceTimeRepository.list")

    def add(self, entity: object) -> object:
        raise NotImplementedError("TODO: Implement InvOccuranceTimeRepository.add")

    def update(self, entity: object) -> object:
        raise NotImplementedError("TODO: Implement InvOccuranceTimeRepository.update")

    def delete(self, entity_id: int) -> None:
        raise NotImplementedError("TODO: Implement InvOccuranceTimeRepository.delete")
