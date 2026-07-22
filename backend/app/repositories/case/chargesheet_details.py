"""Repository stub for `ChargesheetDetails`.

TODO: Chargesheet / final report (types A/B/C) for a case.
"""

from __future__ import annotations

from app.repositories.base import BaseRepository


class ChargesheetDetailsRepository(BaseRepository[object, int]):
    """Persistence for `ChargesheetDetails`.

    TODO: Implement against SQLAlchemy / Catalyst Data Store.
    """

    def get_by_id(self, entity_id: int) -> object | None:
        raise NotImplementedError(
            "TODO: Implement ChargesheetDetailsRepository.get_by_id"
        )

    def list_all(self, *, limit: int = 100, offset: int = 0) -> list[object]:
        raise NotImplementedError("TODO: Implement ChargesheetDetailsRepository.list")

    def add(self, entity: object) -> object:
        raise NotImplementedError("TODO: Implement ChargesheetDetailsRepository.add")

    def update(self, entity: object) -> object:
        raise NotImplementedError("TODO: Implement ChargesheetDetailsRepository.update")

    def delete(self, entity_id: int) -> None:
        raise NotImplementedError("TODO: Implement ChargesheetDetailsRepository.delete")
