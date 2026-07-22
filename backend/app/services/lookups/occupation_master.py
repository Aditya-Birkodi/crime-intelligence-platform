"""Service stub for `OccupationMaster`.

TODO: Occupation lookup for complainants.
"""

from __future__ import annotations

from app.repositories.lookups.occupation_master import OccupationMasterRepository
from app.services.base import BaseService


class OccupationMasterService(BaseService[object, int]):
    """Application service for `OccupationMaster`.

    TODO: Orchestrate repository calls and domain rules (no API logic here).
    """

    def __init__(self, repository: OccupationMasterRepository) -> None:
        super().__init__(repository)
