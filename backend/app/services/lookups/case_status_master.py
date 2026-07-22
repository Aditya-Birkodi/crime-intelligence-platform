"""Service stub for `CaseStatusMaster`.

TODO: Case status (Under Investigation, Charge Sheeted, Closed, …).
"""

from __future__ import annotations

from app.repositories.lookups.case_status_master import CaseStatusMasterRepository
from app.services.base import BaseService


class CaseStatusMasterService(BaseService[object, int]):
    """Application service for `CaseStatusMaster`.

    TODO: Orchestrate repository calls and domain rules (no API logic here).
    """

    def __init__(self, repository: CaseStatusMasterRepository) -> None:
        super().__init__(repository)
