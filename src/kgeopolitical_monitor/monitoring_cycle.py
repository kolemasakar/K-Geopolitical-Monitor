"""Controlled M5 monitoring cycle orchestration."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Protocol

from .operational_monitoring import COMPLETED, FAILED, MonitoringWatch, OperationalMonitoringRuntime
from .operational_output import FindingDraft, OperationalFinding, OperationalOutputStore


class MonitoringProcessor(Protocol):
    def process(self, watch: MonitoringWatch) -> list[FindingDraft]: ...


@dataclass(frozen=True)
class CycleExecution:
    watch_id: str
    run_id: str
    status: str
    result_count: int
    retry_count: int
    error: str | None = None


class MonitoringCycle:
    def __init__(
        self,
        runtime: OperationalMonitoringRuntime,
        processor: MonitoringProcessor,
    ):
        self.runtime = runtime
        self.processor = processor
        self.output = OperationalOutputStore(runtime.database_path)

    def execute_due(self, now: datetime) -> list[CycleExecution]:
        executions: list[CycleExecution] = []

        for watch in self.runtime.due_watches(now):
            run = self.runtime.start_run(watch.watch_id, started_at=now)
            try:
                drafts = list(self.processor.process(watch))
                findings = self.output.save_findings(
                    run.run_id,
                    watch.watch_id,
                    drafts,
                    created_at=now,
                )
                self.runtime.complete_run(
                    run.run_id,
                    result_count=len(findings),
                    completed_at=now,
                )
                executions.append(
                    CycleExecution(
                        watch_id=watch.watch_id,
                        run_id=run.run_id,
                        status=COMPLETED,
                        result_count=len(findings),
                        retry_count=run.retry_count,
                    )
                )
            except Exception as exc:
                error = str(exc).strip() or exc.__class__.__name__
                self.runtime.fail_run(run.run_id, error, completed_at=now)
                executions.append(
                    CycleExecution(
                        watch_id=watch.watch_id,
                        run_id=run.run_id,
                        status=FAILED,
                        result_count=0,
                        retry_count=run.retry_count,
                        error=error,
                    )
                )

        return executions

    def ranked_findings(
        self,
        *,
        watch_id: str | None = None,
        run_id: str | None = None,
        limit: int = 10,
    ) -> list[OperationalFinding]:
        return self.output.ranked_findings(
            watch_id=watch_id,
            run_id=run_id,
            limit=limit,
        )
