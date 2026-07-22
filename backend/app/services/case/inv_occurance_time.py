"""Service stub for `Inv_OccuranceTime`.

TODO: Occurrence time/location record (1:1 with CaseMaster per ER matrix).
"""

from __future__ import annotations

from app.repositories.case.inv_occurance_time import InvOccuranceTimeRepository
from app.services.base import BaseService


class InvOccuranceTimeService(BaseService[object, int]):
    """Application service for `Inv_OccuranceTime`.

    TODO: Orchestrate repository calls and domain rules (no API logic here).
    """

    def __init__(self, repository: InvOccuranceTimeRepository) -> None:
        super().__init__(repository)
