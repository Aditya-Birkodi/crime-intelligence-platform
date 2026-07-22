"""Repository stub for `CrimeHeadActSection`.

TODO: Maps CrimeHead to Act+Section combinations.
"""

from __future__ import annotations

from app.repositories.base import BaseRepository


class CrimeHeadActSectionRepository(BaseRepository[object, int]):
    """Persistence for `CrimeHeadActSection`.

    TODO: Implement against SQLAlchemy / Catalyst Data Store.
    """

    def get_by_id(self, entity_id: int) -> object | None:
        raise NotImplementedError(
            "TODO: Implement CrimeHeadActSectionRepository.get_by_id"
        )

    def list_all(self, *, limit: int = 100, offset: int = 0) -> list[object]:
        raise NotImplementedError("TODO: Implement CrimeHeadActSectionRepository.list")

    def add(self, entity: object) -> object:
        raise NotImplementedError("TODO: Implement CrimeHeadActSectionRepository.add")

    def update(self, entity: object) -> object:
        raise NotImplementedError(
            "TODO: Implement CrimeHeadActSectionRepository.update"
        )

    def delete(self, entity_id: int) -> None:
        raise NotImplementedError(
            "TODO: Implement CrimeHeadActSectionRepository.delete"
        )
