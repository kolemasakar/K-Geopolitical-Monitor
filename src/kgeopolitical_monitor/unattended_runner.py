"""Executable unattended monitoring runner for the E4 owner-only deployment pilot."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import signal
import threading
from typing import Sequence

from .live_end_to_end import LiveEndToEndProcessor
from .live_operational_cycle import LiveOperationalCycle
from .live_sources import (
    ConsiliumRssAdapter,
    GdeltDoc2Adapter,
    HttpTransport,
    LiveSourceCollector,
    UrllibHttpTransport,
)
from .operational_monitoring import OperationalMonitoringRuntime
from .unattended_service import UnattendedMonitoringService, UnattendedTick


def build_unattended_service(
    project_root: str | Path,
    *,
    poll_seconds: float = 60.0,
    transport: HttpTransport | None = None,
) -> UnattendedMonitoringService:
    """Build the validated live unattended stack without opening inbound services."""

    runtime = OperationalMonitoringRuntime(Path(project_root))
    http_transport = transport if transport is not None else UrllibHttpTransport()
    collector = LiveSourceCollector(
        runtime,
        [
            ConsiliumRssAdapter(http_transport),
            GdeltDoc2Adapter(http_transport),
        ],
    )
    processor = LiveEndToEndProcessor(runtime)
    cycle = LiveOperationalCycle(runtime, collector, processor)
    return UnattendedMonitoringService(
        runtime,
        cycle,
        poll_seconds=poll_seconds,
    )


def _tick_payload(tick: UnattendedTick) -> dict[str, object]:
    return {
        "checked_at": tick.checked_at.isoformat(),
        "recovered_runs": tick.recovered_runs,
        "execution_count": len(tick.executions),
        "executions": [
            {
                "watch_id": execution.watch_id,
                "run_id": execution.run_id,
                "status": execution.status,
                "result_count": execution.result_count,
                "retry_count": execution.retry_count,
                "error": execution.error,
            }
            for execution in tick.executions
        ],
    }


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run the K-Geopolitical Monitor unattended monitoring supervisor."
    )
    parser.add_argument(
        "--project-root",
        type=Path,
        default=Path.cwd(),
        help="Project root containing the project-local data directory.",
    )
    parser.add_argument(
        "--poll-seconds",
        type=float,
        default=60.0,
        help="Supervisor poll interval; watch cadence remains independently persisted.",
    )
    parser.add_argument(
        "--once",
        action="store_true",
        help="Run one supervisor tick and exit; intended for validation/smoke checks.",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    service = build_unattended_service(
        args.project_root,
        poll_seconds=args.poll_seconds,
    )

    if args.once:
        tick = service.run_once()
        print(json.dumps(_tick_payload(tick), sort_keys=True))
        return 0

    stop_event = threading.Event()

    def request_stop(_signum, _frame) -> None:
        stop_event.set()

    signal.signal(signal.SIGTERM, request_stop)
    signal.signal(signal.SIGINT, request_stop)
    service.serve_forever(stop_requested=stop_event.is_set)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
