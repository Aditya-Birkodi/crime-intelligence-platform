"""Repository stub for `inv_arrestsurrenderaccused`.

TODO: Junction linking ArrestSurrender to multiple Accused.
"""

from __future__ import annotations

from app.repositories.base import BaseRepository


class InvArrestSurrenderAccusedRepository(BaseRepository[object, int]):
    """Persistence for `inv_arrestsurrenderaccused`.

    TODO: Implement against SQLAlchemy / Catalyst Data Store.
    """

    def get_by_id(self, entity_id: int) -> object | None:
        raise NotImplementedError(
            "TODO: Implement InvArrestSurrenderAccusedRepository.get_by_id"
        )

    def list_all(self, *, limit: int = 100, offset: int = 0) -> list[object]:
        raise NotImplementedError(
            "TODO: Implement InvArrestSurrenderAccusedRepository.list"
        )

    def add(self, entity: object) -> object:
        raise NotImplementedError(
            "TODO: Implement InvArrestSurrenderAccusedRepository.add"
        )

    def update(self, entity: object) -> object:
        raise NotImplementedError(
            "TODO: Implement InvArrestSurrenderAccusedRepository.update"
        )

    def delete(self, entity_id: int) -> None:
        raise NotImplementedError(
            "TODO: Implement InvArrestSurrenderAccusedRepository.delete"
        )
