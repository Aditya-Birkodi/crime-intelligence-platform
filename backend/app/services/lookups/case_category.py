"""Service stub for `CaseCategory`.

TODO: Case category (FIR, UDR, PAR, …).
"""

from __future__ import annotations

from app.repositories.lookups.case_category import CaseCategoryRepository
from app.services.base import BaseService


class CaseCategoryService(BaseService[object, int]):
    """Application service for `CaseCategory`.

    TODO: Orchestrate repository calls and domain rules (no API logic here).
    """

    def __init__(self, repository: CaseCategoryRepository) -> None:
        super().__init__(repository)
