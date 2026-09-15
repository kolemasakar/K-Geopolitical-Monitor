"""P19 recovery-window and temporal coverage semantics."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
import json
import math
import re
import sqlite3
from typing import Protocol, Sequence

from .operational_coverage import (
    CoverageRequirementResultDraft,
    CoverageRequirementSpec,
    OperationalCoverageService,
)
from .operational_monitoring import (
    MonitoringWatch,
    OperationalMonitoringRuntime,
    _normalize_time,
)

BOUNDED_HISTORY = "BOUNDED_HISTORY"
UNKNOWN_HISTORY = "UNKNOWN_HISTORY"
RECOVERY_SCOPE_PREFIX = "recovery-collection:"
SOURCE_FRESHNESS_SECONDS = {
    "consilium-press-releases": 240 * 60,
    "gdelt-doc-2": 60 * 60,
}

@dataclass(frozen=True)
class RecoveryWindow:
    start: datetime
    end: datetime

    def __post_init__(self) -> None:
        start = _normalize_time(self.start)
        end = _normalize_time(self.end)
        if end <= start:
            raise ValueError("recovery window end must be after start")

    @property
    def seconds(self) -> int:
        return max(1, math.ceil((self.end - self.start).total_seconds()))


@dataclass(frozen=True)
class SourceRecoveryCapability:
    mode: str
    max_history_seconds: int | None = None

    def __post_init__(self) -> None:
        if self.mode not in {BOUNDED_HISTORY, UNKNOWN_HISTORY}:
            raise ValueError("unsupported source recovery capability mode")
        if self.mode == BOUNDED_HISTORY and not self.max_history_seconds:
            raise ValueError("bounded history requires a positive history window")


class RecoverySource(Protocol):
    source_id: str
    source_name: str
    source_class: str

    def recovery_capability(self) -> SourceRecoveryCapability: ...


class RecoveryAttempt(Protocol):
    source_id: str
    status: str
    item_count: int
    error: str | None


def parse_history_window_seconds(value: str) -> int:
    match = re.fullmatch(r"\s*(\d+)\s*([mhd])\s*", str(value), re.IGNORECASE)
    if match is None:
        raise ValueError("unsupported historical retrieval window")
    quantity = int(match.group(1))
    multiplier = {"m": 60, "h": 3600, "d": 86400}[match.group(2).lower()]
    seconds = quantity * multiplier
    if seconds <= 0:
        raise ValueError("historical retrieval window must be positive")
    return seconds


def _parse_content_timestamp(metadata):
    for field in ("published_at", "published_at_raw", "seendate"):
        raw = str(metadata.get(field) or "").strip()
        if not raw:
            continue
        try:
            value = datetime.fromisoformat(raw.replace("Z", "+00:00"))
            return _normalize_time(value), field
        except ValueError:
            pass
        try:
            return _normalize_time(parsedate_to_datetime(raw)), field
        except (TypeError, ValueError, OverflowError):
            pass
        for fmt in ("%Y%m%dT%H%M%SZ", "%Y%m%d%H%M%S"):
            try:
                return datetime.strptime(raw, fmt).replace(tzinfo=timezone.utc), field
            except ValueError:
                pass
    return None, None

def recovery_window_for(
    runtime: OperationalMonitoringRuntime,
    watch: MonitoringWatch,
    now: datetime,
) -> RecoveryWindow | None:
    current = _normalize_time(now)
    latest = runtime.repository.latest_run(watch.watch_id)
    if latest is None or latest.status == "RUNNING":
        return None
    expected_at = _normalize_time(latest.started_at) + timedelta(
        minutes=watch.cadence_minutes
    )
    if current <= expected_at:
        return None
    return RecoveryWindow(expected_at, current)


def recovery_snapshot_ids(database_path, collection_id: str) -> tuple[str, ...]:
    scope_key = f"{RECOVERY_SCOPE_PREFIX}{collection_id}"
    with sqlite3.connect(database_path) as connection:
        rows = connection.execute(
            """
            SELECT snapshot.coverage_snapshot_id
            FROM operational_coverage_snapshots AS snapshot
            JOIN operational_coverage_contracts AS contract
              ON contract.coverage_contract_id = snapshot.coverage_contract_id
            WHERE contract.scope_key = ?
            ORDER BY snapshot.assessed_at, snapshot.coverage_snapshot_id
            """,
            (scope_key,),
        ).fetchall()
    return tuple(row[0] for row in rows)


class RecoveryCoverageRecorder:
    def __init__(self, runtime: OperationalMonitoringRuntime):
        self.runtime = runtime
        self.coverage = OperationalCoverageService(runtime)
        self.freshness_seconds = dict(SOURCE_FRESHNESS_SECONDS)

    @staticmethod
    def _capability(adapter: RecoverySource) -> SourceRecoveryCapability:
        provider = getattr(adapter, "recovery_capability", None)
        if provider is None:
            return SourceRecoveryCapability(UNKNOWN_HISTORY)
        capability = provider()
        if not isinstance(capability, SourceRecoveryCapability):
            raise TypeError("recovery_capability must return SourceRecoveryCapability")
        return capability

    @staticmethod
    def _result_payload(
        window: RecoveryWindow,
        capability: SourceRecoveryCapability,
        attempt: RecoveryAttempt,
    ) -> tuple[str, dict[str, object]]:
        base: dict[str, object] = {
            "requested_start": _normalize_time(window.start).isoformat(),
            "requested_end": _normalize_time(window.end).isoformat(),
            "capability_mode": capability.mode,
            "max_history_seconds": capability.max_history_seconds,
            "attempt_status": attempt.status,
            "item_count": int(attempt.item_count),
        }
        if attempt.status != "SUCCESS":
            base.update(
                {
                    "temporal_state": "MISSING",
                    "covered_intervals": [],
                    "uncovered_intervals": [[base["requested_start"], base["requested_end"]]],
                    "error": attempt.error,
                }
            )
            return "UNAVAILABLE", base

        if capability.mode == UNKNOWN_HISTORY:
            base.update(
                {
                    "temporal_state": "MISSING_OR_UNPROVEN",
                    "covered_intervals": [],
                    "uncovered_intervals": [[base["requested_start"], base["requested_end"]]],
                    "error": None,
                }
            )
            return "UNKNOWN", base

        assert capability.max_history_seconds is not None
        earliest = _normalize_time(window.end) - timedelta(
            seconds=capability.max_history_seconds
        )
        covered_start = max(_normalize_time(window.start), earliest)
        covered = [[covered_start.isoformat(), base["requested_end"]]]
        uncovered = []
        if covered_start > _normalize_time(window.start):
            uncovered.append([base["requested_start"], covered_start.isoformat()])
        base.update(
            {
                "temporal_state": "RECOVERED" if not uncovered else "PARTIAL_RECOVERY",
                "covered_intervals": covered,
                "uncovered_intervals": uncovered,
                "error": None,
            }
        )
        return ("SATISFIED" if not uncovered else "GAP"), base

    def _freshness_result(self, collection_id, source_id, attempt, assessed_at):
        expected = self.freshness_seconds.get(source_id)
        payload = {"collection_id": collection_id, "source_id": source_id,
                   "expected_freshness_seconds": expected}
        if attempt.status != "SUCCESS":
            payload.update({"freshness_state": "UNAVAILABLE", "error": attempt.error})
            return "UNAVAILABLE", payload
        with sqlite3.connect(self.runtime.database_path) as connection:
            rows = connection.execute(
                """SELECT p.metadata_json FROM live_source_provenance p
                JOIN raw_items r ON r.id = p.raw_item_id
                WHERE p.collection_id = ? AND r.source_id = ?""",
                (collection_id, source_id),
            ).fetchall()
        observed = []
        for (metadata_json,) in rows:
            try:
                metadata = json.loads(metadata_json or "{}")
            except json.JSONDecodeError:
                metadata = {}
            timestamp, basis = _parse_content_timestamp(metadata)
            if timestamp is not None and timestamp <= assessed_at:
                observed.append((timestamp, basis))
        if not observed:
            payload.update({"freshness_state": "UNKNOWN", "reason": "NO_PUBLISHER_TIMESTAMP"})
            return "UNKNOWN", payload
        latest, basis = max(observed, key=lambda item: item[0])
        age_seconds = max(0.0, (assessed_at - latest).total_seconds())
        payload.update({"latest_content_at": latest.isoformat(), "timestamp_basis": basis,
                        "content_age_seconds": age_seconds})
        if expected is None:
            payload["freshness_state"] = "UNKNOWN"
            return "UNKNOWN", payload
        fresh = age_seconds <= expected
        payload["freshness_state"] = "FRESH" if fresh else "STALE"
        return ("SATISFIED" if fresh else "STALE"), payload

    def record(
        self,
        *,
        collection_id: str,
        watch: MonitoringWatch,
        window: RecoveryWindow,
        adapters: Sequence[RecoverySource],
        attempts: Sequence[RecoveryAttempt],
        assessed_at: datetime,
    ) -> str:
        attempt_by_source = {item.source_id: item for item in attempts}
        if {item.source_id for item in adapters} != set(attempt_by_source):
            raise ValueError("recovery coverage requires one attempt per configured source")

        requirements = []
        capabilities: dict[str, SourceRecoveryCapability] = {}
        for adapter in adapters:
            capability = self._capability(adapter)
            capabilities[adapter.source_id] = capability
            requirements.append(
                CoverageRequirementSpec(
                    dimension="SOURCE_ID", requirement_key=adapter.source_id,
                    parameters={"collection_id": collection_id,
                        "recovery_start": _normalize_time(window.start).isoformat(),
                        "recovery_end": _normalize_time(window.end).isoformat(),
                        "capability_mode": capability.mode,
                        "max_history_seconds": capability.max_history_seconds},
                )
            )
            requirements.append(
                CoverageRequirementSpec(
                    dimension="FRESHNESS", requirement_key=adapter.source_id,
                    parameters={"collection_id": collection_id,
                        "expected_freshness_seconds": self.freshness_seconds.get(adapter.source_id)},
                )
            )

        contract = self.coverage.create_contract(
            scope_key=f"{RECOVERY_SCOPE_PREFIX}{collection_id}",
            name=f"Recovery coverage for {collection_id}",
            watch_id=watch.watch_id,
            assessment_window_seconds=window.seconds,
            freshness_requirement_seconds=max(1, watch.cadence_minutes * 60),
            requirements=requirements,
            created_at=assessed_at,
        )
        requirement_by_key = {
            (item.dimension, item.requirement_key): item
            for item in self.coverage.requirements(contract.coverage_contract_id)
        }
        results = []
        for adapter in adapters:
            attempt = attempt_by_source[adapter.source_id]
            requirement = requirement_by_key[("SOURCE_ID", adapter.source_id)]
            status, payload = self._result_payload(
                window, capabilities[adapter.source_id], attempt
            )
            results.append(
                CoverageRequirementResultDraft(
                    requirement_id=requirement.requirement_id,
                    status=status,
                    evidence_refs=(
                        f"collection:{collection_id}",
                        f"source_attempt:{collection_id}:{adapter.source_id}",
                    ),
                    explanation=json.dumps(payload, sort_keys=True, separators=(",", ":")),
                    measured_at=assessed_at,
                )
            )
            freshness_requirement = requirement_by_key[("FRESHNESS", adapter.source_id)]
            freshness_status, freshness_payload = self._freshness_result(
                collection_id, adapter.source_id, attempt, assessed_at
            )
            results.append(
                CoverageRequirementResultDraft(
                    requirement_id=freshness_requirement.requirement_id,
                    status=freshness_status,
                    evidence_refs=(f"collection:{collection_id}",
                        f"source_attempt:{collection_id}:{adapter.source_id}"),
                    explanation=json.dumps(freshness_payload, sort_keys=True, separators=(",", ":")),
                    measured_at=assessed_at,
                )
            )

        snapshot = self.coverage.create_snapshot(
            contract.coverage_contract_id,
            results,
            assessed_at=assessed_at,
        )
        return snapshot.coverage_snapshot_id
