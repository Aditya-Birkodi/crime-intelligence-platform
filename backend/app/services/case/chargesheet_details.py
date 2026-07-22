"""Service stub for `ChargesheetDetails`.

TODO: Chargesheet / final report (types A/B/C) for a case.
"""

from __future__ import annotations

from app.repositories.case.chargesheet_details import ChargesheetDetailsRepository
from app.services.base import BaseService


class ChargesheetDetailsService(BaseService[object, int]):
    """Application service for `ChargesheetDetails`.

    TODO: Orchestrate repository calls and domain rules (no API logic here).
    """

    def __init__(self, repository: ChargesheetDetailsRepository) -> None:
        super().__init__(repository)
