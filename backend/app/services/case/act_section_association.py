"""Service stub for `ActSectionAssociation`.

TODO: Junction of CaseMaster ↔ Act ↔ Section with display order.
"""

from __future__ import annotations

from app.repositories.case.act_section_association import (
    ActSectionAssociationRepository,
)
from app.services.base import BaseService


class ActSectionAssociationService(BaseService[object, int]):
    """Application service for `ActSectionAssociation`.

    TODO: Orchestrate repository calls and domain rules (no API logic here).
    """

    def __init__(self, repository: ActSectionAssociationRepository) -> None:
        super().__init__(repository)
