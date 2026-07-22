"""Graph AI service stub.

TODO: Define graph projection from FIR entities..
"""

from __future__ import annotations

from app.core.logging import get_ai_logger


class GraphService:
    """Placeholder for `graph` AI capability."""

    def __init__(self) -> None:
        self._logger = get_ai_logger()

    def run(self, *args: object, **kwargs: object) -> None:
        """TODO: Implement `graph` pipeline."""
        raise NotImplementedError("TODO: Implement graph AI service")
