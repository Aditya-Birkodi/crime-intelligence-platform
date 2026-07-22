"""Repository stub for `CaseStatusMaster`.

TODO: Case status (Under Investigation, Charge Sheeted, Closed, …).
"""

from __future__ import annotations

from app.repositories.base import BaseRepository


class CaseStatusMasterRepository(BaseRepository[object, int]):
    """Persistence for `CaseStatusMaster`.

    TODO: Implement against SQLAlchemy / Catalyst Data Store.
    """

    def get_by_id(self, entity_id: int) -> object | None:
        raise NotImplementedError(
            "TODO: Implement CaseStatusMasterRepository.get_by_id"
        )

    def list_all(self, *, limit: int = 100, offset: int = 0) -> list[object]:
        raise NotImplementedError("TODO: Implement CaseStatusMasterRepository.list")

    def add(self, entity: object) -> object:
        raise NotImplementedError("TODO: Implement CaseStatusMasterRepository.add")

    def update(self, entity: object) -> object:
        raise NotImplementedError("TODO: Implement CaseStatusMasterRepository.update")

    def delete(self, entity_id: int) -> None:
        raise NotImplementedError("TODO: Implement CaseStatusMasterRepository.delete")
