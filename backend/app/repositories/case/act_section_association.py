"""Repository stub for `ActSectionAssociation`.

TODO: Junction of CaseMaster ↔ Act ↔ Section with display order.
"""

from __future__ import annotations

from app.repositories.base import BaseRepository


class ActSectionAssociationRepository(BaseRepository[object, int]):
    """Persistence for `ActSectionAssociation`.

    TODO: Implement against SQLAlchemy / Catalyst Data Store.
    """

    def get_by_id(self, entity_id: int) -> object | None:
        raise NotImplementedError(
            "TODO: Implement ActSectionAssociationRepository.get_by_id"
        )

    def list_all(self, *, limit: int = 100, offset: int = 0) -> list[object]:
        raise NotImplementedError(
            "TODO: Implement ActSectionAssociationRepository.list"
        )

    def add(self, entity: object) -> object:
        raise NotImplementedError("TODO: Implement ActSectionAssociationRepository.add")

    def update(self, entity: object) -> object:
        raise NotImplementedError(
            "TODO: Implement ActSectionAssociationRepository.update"
        )

    def delete(self, entity_id: int) -> None:
        raise NotImplementedError(
            "TODO: Implement ActSectionAssociationRepository.delete"
        )
