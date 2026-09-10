from __future__ import annotations

import argparse
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Iterable

MILESTONE_HOURS = (24, 72, 168)


def parse_utc(value: str) -> datetime:
    text = value.strip()
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    parsed = datetime.fromisoformat(text)
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def iso_z(value: datetime) -> str:
    return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def _normalize_observations(
    values: Iterable[str | datetime], *, baseline: datetime, now: datetime
) -> tuple[datetime, ...]:
    normalized: set[datetime] = set()
    for value in values:
        observed = parse_utc(value) if isinstance(value, str) else value.astimezone(timezone.utc)
        if baseline <= observed <= now:
            normalized.add(observed)
    return tuple(sorted(normalized))


def _max_gap(points: Iterable[datetime]) -> timedelta:
    ordered = tuple(sorted(points))
    if len(ordered) < 2:
        return timedelta(0)
    return max((right - left for left, right in zip(ordered, ordered[1:])), default=timedelta(0))


def evaluate_soak(
    *,
    baseline: datetime,
    now: datetime,
    observations: Iterable[str | datetime],
    max_gap: timedelta = timedelta(hours=7),
) -> dict[str, object]:
    baseline = baseline.astimezone(timezone.utc)
    now = now.astimezone(timezone.utc)
    if now < baseline:
        raise ValueError("now must be at or after baseline")
    if max_gap <= timedelta(0):
        raise ValueError("max_gap must be positive")

    observed = _normalize_observations(observations, baseline=baseline, now=now)
    post_baseline = tuple(item for item in observed if item > baseline)

    current_points = (baseline, *post_baseline, now)
    current_max_gap = _max_gap(current_points)
    continuity_ok = current_max_gap <= max_gap

    milestones: dict[str, dict[str, object]] = {}
    milestone_failure = False

    for hours in MILESTONE_HOURS:
        boundary = baseline + timedelta(hours=hours)
        key = "7d" if hours == 168 else f"{hours}h"
        terminal = next((item for item in post_baseline if item >= boundary), None)

        if now < boundary:
            status = "IN_PROGRESS"
        elif terminal is None:
            status = "FAIL_CONTINUITY" if not continuity_ok else "WAITING_TERMINAL_OBSERVATION"
        else:
            points_to_terminal = (baseline, *(item for item in post_baseline if item <= terminal))
            status = "PASS" if _max_gap(points_to_terminal) <= max_gap else "FAIL_CONTINUITY"

        if status == "FAIL_CONTINUITY":
            milestone_failure = True

        milestones[key] = {
            "hours": hours,
            "boundary_utc": iso_z(boundary),
            "status": status,
            "terminal_observation_utc": iso_z(terminal) if terminal else None,
        }

    return {
        "schema_version": "kgm.p19_soak_gate.v1",
        "baseline_utc": iso_z(baseline),
        "evaluated_at_utc": iso_z(now),
        "max_allowed_gap_hours": max_gap.total_seconds() / 3600,
        "qualifying_observation_count_after_baseline": len(post_baseline),
        "latest_observation_utc": iso_z(post_baseline[-1]) if post_baseline else iso_z(baseline),
        "current_max_gap_hours": current_max_gap.total_seconds() / 3600,
        "continuity_status": "PASS" if continuity_ok else "FAIL_CONTINUITY",
        "milestones": milestones,
        "audit_status": "FAIL_CONTINUITY" if (not continuity_ok or milestone_failure) else "PASS",
    }


def _read_observations(path: Path) -> list[str]:
    if not path.exists():
        return []
    return [line.strip() for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def main() -> int:
    parser = argparse.ArgumentParser(description="Evaluate P19 owner-local real-soak elapsed evidence.")
    parser.add_argument("--baseline", required=True)
    parser.add_argument("--now", required=True)
    parser.add_argument("--observations-file", required=True, type=Path)
    parser.add_argument("--max-gap-hours", type=float, default=7.0)
    parser.add_argument("--output-json", type=Path)
    args = parser.parse_args()

    result = evaluate_soak(
        baseline=parse_utc(args.baseline),
        now=parse_utc(args.now),
        observations=_read_observations(args.observations_file),
        max_gap=timedelta(hours=args.max_gap_hours),
    )

    rendered = json.dumps(result, indent=2, sort_keys=True)
    print(rendered)
    if args.output_json:
        args.output_json.write_text(rendered + "\n", encoding="utf-8")

    milestones = result["milestones"]
    print(f"P19_SOAK_AUDIT={result['audit_status']}")
    print(f"P19_CONTINUITY_STATUS={result['continuity_status']}")
    print(f"P19_REAL_24H_SOAK={milestones['24h']['status']}")
    print(f"P19_REAL_72H_SOAK={milestones['72h']['status']}")
    print(f"P19_REAL_7D_SOAK={milestones['7d']['status']}")

    return 0 if result["audit_status"] == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
