"""Service stub for `CasteMaster`.

TODO: Caste lookup for complainants.
"""

from __future__ import annotations

from app.repositories.lookups.caste_master import CasteMasterRepository
from app.services.base import BaseService


class CasteMasterService(BaseService[object, int]):
    """Application service for `CasteMaster`.

    TODO: Orchestrate repository calls and domain rules (no API logic here).
    """

    def __init__(self, repository: CasteMasterRepository) -> None:
        super().__init__(repository)
