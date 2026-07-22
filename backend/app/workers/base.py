"""Base worker interface.

TODO: Integrate Catalyst Cron triggers and Circuits orchestration steps.
"""

from __future__ import annotations

from abc import ABC, abstractmethod


class BaseWorker(ABC):
    """Async/background job placeholder."""

    @abstractmethod
    def run(self) -> None:
        """TODO: Execute worker job."""
