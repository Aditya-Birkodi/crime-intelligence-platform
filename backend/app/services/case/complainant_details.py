"""Service stub for `ComplainantDetails`.

TODO: Complainant linked to CaseMaster; FKs to Occupation/Religion/Caste masters.
"""

from __future__ import annotations

from app.repositories.case.complainant_details import ComplainantDetailsRepository
from app.services.base import BaseService


class ComplainantDetailsService(BaseService[object, int]):
    """Application service for `ComplainantDetails`.

    TODO: Orchestrate repository calls and domain rules (no API logic here).
    """

    def __init__(self, repository: ComplainantDetailsRepository) -> None:
        super().__init__(repository)
