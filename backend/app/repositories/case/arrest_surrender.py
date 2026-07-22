"""Repository stub for `ArrestSurrender`.

TODO: Arrest/surrender events; FKs to State/District/Unit/Employee/Court/Accused.
"""

from __future__ import annotations

from app.repositories.base import BaseRepository


class ArrestSurrenderRepository(BaseRepository[object, int]):
    """Persistence for `ArrestSurrender`.

    TODO: Implement against SQLAlchemy / Catalyst Data Store.
    """

    def get_by_id(self, entity_id: int) -> object | None:
        raise NotImplementedError("TODO: Implement ArrestSurrenderRepository.get_by_id")

    def list_all(self, *, limit: int = 100, offset: int = 0) -> list[object]:
        raise NotImplementedError("TODO: Implement ArrestSurrenderRepository.list")

    def add(self, entity: object) -> object:
        raise NotImplementedError("TODO: Implement ArrestSurrenderRepository.add")

    def update(self, entity: object) -> object:
        raise NotImplementedError("TODO: Implement ArrestSurrenderRepository.update")

    def delete(self, entity_id: int) -> None:
        raise NotImplementedError("TODO: Implement ArrestSurrenderRepository.delete")
