"""Post-Phase-11 unattended pilot service supervisor."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
import time
from typing import Callable, Protocol

from .monitoring_cycle import CycleExecution
from .operational_monitoring import OperationalMonitoringRuntime, _normalize_time, utc_now


class DueCycleExecutor(Protocol):
    def execute_due(self, now: datetime) -> list[CycleExecution]: ...


class RuntimeHealthRecorder(Protocol):
    def record_tick(
        self,
        *,
        checked_at: datetime,
        recovered_runs: int,
        executions: tuple[CycleExecution, ...],
    ) -> object: ...


@dataclass(frozen=True)
class UnattendedTick:
    checked_at: datetime
    recovered_runs: int
    executions: tuple[CycleExecution, ...]


class UnattendedMonitoringService:
    """Thin restart-safe supervisor over the existing monitoring runtime.

    Per-watch failures remain the responsibility of the injected cycle executor.
    Unexpected supervisor failures are intentionally not swallowed so an external
    service manager such as systemd can restart the process and make the failure
    visible.
    """

    def __init__(
        self,
        runtime: OperationalMonitoringRuntime,
        cycle: DueCycleExecutor,
        *,
        poll_seconds: float = 60.0,
        health_recorder: RuntimeHealthRecorder | None = None,
    ) -> None:
        if poll_seconds <= 0:
            raise ValueError("poll_seconds must be positive")
        self.runtime = runtime
        self.cycle = cycle
        self.poll_seconds = float(poll_seconds)
        self.health_recorder = health_recorder
        self._startup_recovery_complete = False

    def run_once(self, now: datetime | None = None) -> UnattendedTick:
        current = _normalize_time(now or utc_now())
        recovered_runs = 0
        if not self._startup_recovery_complete:
            recovered_runs = self.runtime.recover_interrupted_runs(current)
            self._startup_recovery_complete = True

        executions = tuple(self.cycle.execute_due(current))
        tick = UnattendedTick(
            checked_at=current,
            recovered_runs=recovered_runs,
            executions=executions,
        )
        if self.health_recorder is not None:
            self.health_recorder.record_tick(
                checked_at=current,
                recovered_runs=recovered_runs,
                executions=executions,
            )
        return tick

    def serve_forever(
        self,
        *,
        clock: Callable[[], datetime] = utc_now,
        sleeper: Callable[[float], None] = time.sleep,
        stop_requested: Callable[[], bool] = lambda: False,
        max_iterations: int | None = None,
    ) -> int:
        if max_iterations is not None and max_iterations <= 0:
            raise ValueError("max_iterations must be positive when provided")

        iterations = 0
        while not stop_requested():
            self.run_once(clock())
            iterations += 1
            if max_iterations is not None and iterations >= max_iterations:
                break
            sleeper(self.poll_seconds)
        return iterations
