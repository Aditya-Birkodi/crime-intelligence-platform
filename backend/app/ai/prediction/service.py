"""Prediction AI service stub.

TODO: Train/serve via Catalyst Zia AutoML / QuickML..
"""

from __future__ import annotations

from app.core.logging import get_ai_logger


class PredictionService:
    """Placeholder for `prediction` AI capability."""

    def __init__(self) -> None:
        self._logger = get_ai_logger()

    def run(self, *args: object, **kwargs: object) -> None:
        """TODO: Implement `prediction` pipeline."""
        raise NotImplementedError("TODO: Implement prediction AI service")
