"""Repository stub for `CaseCategory`.

TODO: Case category (FIR, UDR, PAR, …).
"""

from __future__ import annotations

from app.repositories.base import BaseRepository


class CaseCategoryRepository(BaseRepository[object, int]):
    """Persistence for `CaseCategory`.

    TODO: Implement against SQLAlchemy / Catalyst Data Store.
    """

    def get_by_id(self, entity_id: int) -> object | None:
        raise NotImplementedError("TODO: Implement CaseCategoryRepository.get_by_id")

    def list_all(self, *, limit: int = 100, offset: int = 0) -> list[object]:
        raise NotImplementedError("TODO: Implement CaseCategoryRepository.list")

    def add(self, entity: object) -> object:
        raise NotImplementedError("TODO: Implement CaseCategoryRepository.add")

    def update(self, entity: object) -> object:
        raise NotImplementedError("TODO: Implement CaseCategoryRepository.update")

    def delete(self, entity_id: int) -> None:
        raise NotImplementedError("TODO: Implement CaseCategoryRepository.delete")
