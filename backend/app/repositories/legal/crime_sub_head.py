"""Repository stub for `CrimeSubHead`.

TODO: Crime sub-head under CrimeHead.
"""

from __future__ import annotations

from app.repositories.base import BaseRepository


class CrimeSubHeadRepository(BaseRepository[object, int]):
    """Persistence for `CrimeSubHead`.

    TODO: Implement against SQLAlchemy / Catalyst Data Store.
    """

    def get_by_id(self, entity_id: int) -> object | None:
        raise NotImplementedError("TODO: Implement CrimeSubHeadRepository.get_by_id")

    def list_all(self, *, limit: int = 100, offset: int = 0) -> list[object]:
        raise NotImplementedError("TODO: Implement CrimeSubHeadRepository.list")

    def add(self, entity: object) -> object:
        raise NotImplementedError("TODO: Implement CrimeSubHeadRepository.add")

    def update(self, entity: object) -> object:
        raise NotImplementedError("TODO: Implement CrimeSubHeadRepository.update")

    def delete(self, entity_id: int) -> None:
        raise NotImplementedError("TODO: Implement CrimeSubHeadRepository.delete")
