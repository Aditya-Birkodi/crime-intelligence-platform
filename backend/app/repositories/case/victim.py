"""Repository stub for `Victim`.

TODO: Victim records for a CaseMaster (1:N).
"""

from __future__ import annotations

from app.repositories.base import BaseRepository


class VictimRepository(BaseRepository[object, int]):
    """Persistence for `Victim`.

    TODO: Implement against SQLAlchemy / Catalyst Data Store.
    """

    def get_by_id(self, entity_id: int) -> object | None:
        raise NotImplementedError("TODO: Implement VictimRepository.get_by_id")

    def list_all(self, *, limit: int = 100, offset: int = 0) -> list[object]:
        raise NotImplementedError("TODO: Implement VictimRepository.list")

    def add(self, entity: object) -> object:
        raise NotImplementedError("TODO: Implement VictimRepository.add")

    def update(self, entity: object) -> object:
        raise NotImplementedError("TODO: Implement VictimRepository.update")

    def delete(self, entity_id: int) -> None:
        raise NotImplementedError("TODO: Implement VictimRepository.delete")
