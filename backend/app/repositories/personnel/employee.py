"""Repository stub for `Employee`.

TODO: Police employee; KGID, Rank, Designation, Unit, District.
"""

from __future__ import annotations

from app.repositories.base import BaseRepository


class EmployeeRepository(BaseRepository[object, int]):
    """Persistence for `Employee`.

    TODO: Implement against SQLAlchemy / Catalyst Data Store.
    """

    def get_by_id(self, entity_id: int) -> object | None:
        raise NotImplementedError("TODO: Implement EmployeeRepository.get_by_id")

    def list_all(self, *, limit: int = 100, offset: int = 0) -> list[object]:
        raise NotImplementedError("TODO: Implement EmployeeRepository.list")

    def add(self, entity: object) -> object:
        raise NotImplementedError("TODO: Implement EmployeeRepository.add")

    def update(self, entity: object) -> object:
        raise NotImplementedError("TODO: Implement EmployeeRepository.update")

    def delete(self, entity_id: int) -> None:
        raise NotImplementedError("TODO: Implement EmployeeRepository.delete")
