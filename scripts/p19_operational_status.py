#!/usr/bin/env python3
"""Operator-facing Phase 19 owner-local stability status summary."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path

from kgeopolitical_monitor.operational_stability import (
    CRITICAL,
    DEGRADED,
    OperationalStabilityEvaluator,
    evaluate_soak_window,
)
from kgeopolitical_monitor.runtime_storage import RuntimeStoragePolicy


def _parse_time(value: str | None) -> datetime:
    if value is None:
        return datetime.now(timezone.utc)
    parsed = datetime.fromisoformat(value)
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ValueError("--at must be timezone-aware ISO-8601")
    return parsed.astimezone(timezone.utc)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Evaluate owner-local KGM beta operational stability."
    )
    parser.add_argument("--project-root", default=".")
    parser.add_argument(
        "--database",
        default=None,
        help="Optional database path; must remain inside project-root/data.",
    )
    parser.add_argument(
        "--expected-source",
        action="append",
        default=[],
        dest="expected_sources",
        help="Source ID expected to have fresh collection attempts; repeatable.",
    )
    parser.add_argument(
        "--at",
        default=None,
        help="Timezone-aware ISO-8601 evaluation timestamp; defaults to current UTC.",
    )
    parser.add_argument(
        "--window-hours",
        type=float,
        default=None,
        help="Also evaluate persisted run history over the preceding real elapsed window.",
    )
    args = parser.parse_args()

    policy = RuntimeStoragePolicy(Path(args.project_root))
    database_path = policy.resolve_database(args.database)
    if not database_path.is_file():
        raise SystemExit(f"runtime database does not exist: {database_path}")

    evaluated_at = _parse_time(args.at)
    report = OperationalStabilityEvaluator(
        database_path,
        expected_source_ids=args.expected_sources,
    ).evaluate(evaluated_at)
    payload = {"snapshot": report.as_dict()}

    window_clean = True
    if args.window_hours is not None:
        if args.window_hours <= 0:
            raise ValueError("--window-hours must be positive")
        from datetime import timedelta

        window = evaluate_soak_window(
            database_path,
            started_at=evaluated_at - timedelta(hours=args.window_hours),
            ended_at=evaluated_at,
        )
        payload["soak_window"] = window.as_dict()
        window_clean = window.clean

    print(json.dumps(payload, indent=2, sort_keys=True))

    if report.status == CRITICAL or not window_clean:
        return 3
    if report.status == DEGRADED:
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
