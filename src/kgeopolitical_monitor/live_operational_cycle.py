"""Live unattended operational cycle over the validated M7/M8 components."""

from __future__ import annotations

from datetime import datetime
from typing import Protocol

from .live_end_to_end import LiveAnalysisResult
from .live_sources import SourceCollectionReport
from .monitoring_cycle import CycleExecution
from .operational_monitoring import (
    COMPLETED,
    FAILED,
    RUNNING,
    MonitoringRun,
    OperationalMonitoringRuntime,
    _normalize_time,
)


class LiveCollector(Protocol):
    def collect(self, watch_id: str, now: datetime) -> SourceCollectionReport: ...


class LiveProcessor(Protocol):
    def process_collection(
        self,
        collection_id: str,
        *,
        processed_at: datetime,
    ) -> LiveAnalysisResult: ...


class LiveOperationalCycle:
    """Execute due live watches without bypassing their persisted cadence.

    Collection audit remains owned by M7. Verification-aware processing remains
    owned by M8. This wrapper only ensures that every due-watch attempt also
    produces monitoring-run state, including total source failure and legitimate
    zero-item successful collections.
    """

    def __init__(
        self,
        runtime: OperationalMonitoringRuntime,
        collector: LiveCollector,
        processor: LiveProcessor,
    ) -> None:
        self.runtime = runtime
        self.collector = collector
        self.processor = processor

    def _terminal_execution(self, run: MonitoringRun) -> CycleExecution:
        if run.status not in {COMPLETED, FAILED}:
            raise RuntimeError("live operational cycle requires a terminal monitoring run")
        return CycleExecution(
            watch_id=run.watch_id,
            run_id=run.run_id,
            status=run.status,
            result_count=run.result_count,
            retry_count=run.retry_count,
            error=run.error,
        )

    def _record_terminal_run(
        self,
        watch_id: str,
        current: datetime,
        *,
        status: str,
        result_count: int = 0,
        error: str | None = None,
    ) -> CycleExecution:
        run = self.runtime.start_run(watch_id, started_at=current)
        if status == COMPLETED:
            self.runtime.complete_run(
                run.run_id,
                result_count=result_count,
                completed_at=current,
            )
        elif status == FAILED:
            self.runtime.fail_run(
                run.run_id,
                error or "live operational cycle failed",
                completed_at=current,
            )
        else:
            raise ValueError("terminal monitoring status must be COMPLETED or FAILED")

        terminal = self.runtime.repository.latest_run(watch_id)
        if terminal is None or terminal.run_id != run.run_id:
            raise RuntimeError("terminal monitoring run was not persisted")
        return self._terminal_execution(terminal)

    def _collection_failure_message(self, collection: SourceCollectionReport) -> str:
        if collection.failures:
            detail = "; ".join(
                f"{failure.get('source_id', 'unknown')}: {failure.get('error', 'failed')}"
                for failure in collection.failures
            )
            return f"live source collection failed: {detail}"
        return "live source collection failed"

    def _record_processing_failure_if_needed(
        self,
        watch_id: str,
        current: datetime,
        previous_run_id: str | None,
        error: str,
    ) -> CycleExecution:
        latest = self.runtime.repository.latest_run(watch_id)
        if latest is None or latest.run_id == previous_run_id:
            return self._record_terminal_run(
                watch_id,
                current,
                status=FAILED,
                error=error,
            )

        if latest.status == RUNNING:
            self.runtime.fail_run(latest.run_id, error, completed_at=current)
            latest = self.runtime.repository.latest_run(watch_id)
            if latest is None:
                raise RuntimeError("failed monitoring run disappeared after persistence")

        if latest.status != FAILED:
            raise RuntimeError(
                "live processor raised after producing a non-failed terminal monitoring run"
            )
        return self._terminal_execution(latest)

    def execute_due(self, now: datetime) -> list[CycleExecution]:
        current = _normalize_time(now)
        executions: list[CycleExecution] = []

        for watch in self.runtime.due_watches(current):
            previous = self.runtime.repository.latest_run(watch.watch_id)
            previous_run_id = previous.run_id if previous is not None else None

            try:
                collection = self.collector.collect(watch.watch_id, current)
            except Exception as exc:
                error = str(exc).strip() or exc.__class__.__name__
                executions.append(
                    self._record_terminal_run(
                        watch.watch_id,
                        current,
                        status=FAILED,
                        error=f"live collection exception: {error}",
                    )
                )
                continue

            if collection.status == FAILED:
                executions.append(
                    self._record_terminal_run(
                        watch.watch_id,
                        current,
                        status=FAILED,
                        error=self._collection_failure_message(collection),
                    )
                )
                continue

            if collection.status not in {"COMPLETED", "PARTIAL"}:
                executions.append(
                    self._record_terminal_run(
                        watch.watch_id,
                        current,
                        status=FAILED,
                        error=f"unsupported live collection status: {collection.status}",
                    )
                )
                continue

            # A successful source request may legitimately contain no matching
            # observations. Preserve it as a completed monitoring check rather
            # than turning source availability success into a processing error.
            if collection.item_count == 0:
                executions.append(
                    self._record_terminal_run(
                        watch.watch_id,
                        current,
                        status=COMPLETED,
                        result_count=0,
                    )
                )
                continue

            try:
                result = self.processor.process_collection(
                    collection.collection_id,
                    processed_at=current,
                )
                latest = self.runtime.repository.latest_run(watch.watch_id)
                if latest is None or latest.run_id != result.monitoring_run_id:
                    raise RuntimeError(
                        "live analysis result is not backed by the latest monitoring run"
                    )
                if latest.status != COMPLETED:
                    raise RuntimeError("live analysis did not complete its monitoring run")
                executions.append(self._terminal_execution(latest))
            except Exception as exc:
                error = str(exc).strip() or exc.__class__.__name__
                executions.append(
                    self._record_processing_failure_if_needed(
                        watch.watch_id,
                        current,
                        previous_run_id,
                        f"live processing failed: {error}",
                    )
                )

        return executions
