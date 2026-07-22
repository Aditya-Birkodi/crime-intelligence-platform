"""Repository stub for `ComplainantDetails`.

TODO: Complainant linked to CaseMaster; FKs to Occupation/Religion/Caste masters.
"""

from __future__ import annotations

from app.repositories.base import BaseRepository


class ComplainantDetailsRepository(BaseRepository[object, int]):
    """Persistence for `ComplainantDetails`.

    TODO: Implement against SQLAlchemy / Catalyst Data Store.
    """

    def get_by_id(self, entity_id: int) -> object | None:
        raise NotImplementedError(
            "TODO: Implement ComplainantDetailsRepository.get_by_id"
        )

    def list_all(self, *, limit: int = 100, offset: int = 0) -> list[object]:
        raise NotImplementedError("TODO: Implement ComplainantDetailsRepository.list")

    def add(self, entity: object) -> object:
        raise NotImplementedError("TODO: Implement ComplainantDetailsRepository.add")

    def update(self, entity: object) -> object:
        raise NotImplementedError("TODO: Implement ComplainantDetailsRepository.update")

    def delete(self, entity_id: int) -> None:
        raise NotImplementedError("TODO: Implement ComplainantDetailsRepository.delete")
