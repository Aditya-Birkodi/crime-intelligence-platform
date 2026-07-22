"""ETL trigger worker stub.

TODO: Schedule FIR ingestion via Catalyst Cron; emit Catalyst Signals on completion.
"""

from __future__ import annotations

from app.workers.base import BaseWorker


class EtlTriggerWorker(BaseWorker):
    """Placeholder worker to kick off ETL pipelines."""

    def run(self) -> None:
        raise NotImplementedError("TODO: Trigger etl.ingestion pipeline")
