"""Service stub for `Employee`.

TODO: Police employee; KGID, Rank, Designation, Unit, District.
"""

from __future__ import annotations

from app.repositories.personnel.employee import EmployeeRepository
from app.services.base import BaseService


class EmployeeService(BaseService[object, int]):
    """Application service for `Employee`.

    TODO: Orchestrate repository calls and domain rules (no API logic here).
    """

    def __init__(self, repository: EmployeeRepository) -> None:
        super().__init__(repository)
