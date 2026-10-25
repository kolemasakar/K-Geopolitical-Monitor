"""One-shot, fixture-only research dispatcher. Not a live/public execution route.

The existing collection pipeline requires a persisted enabled watch. This
dispatcher creates one ONLY inside its owned TemporaryDirectory, invokes one
cycle, and removes the entire temporary project before returning aggregates.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
import re
import sqlite3
from tempfile import TemporaryDirectory
from typing import Protocol, Sequence

from .live_end_to_end import LiveEndToEndProcessor
from .live_operational_cycle import LiveOperationalCycle
from .live_sources import LiveSourceCollector
from .operational_monitoring import OperationalMonitoringRuntime, _normalize_time


class OfflineFixtureAdapter(Protocol):
    source_id: str
    source_name: str
    source_class: str
    offline_fixture_only: bool

    def fetch(self, watch, collected_at): ...


@dataclass(frozen=True)
class OnDemandRequest:
    topic: str
    requested_at: datetime
    request_id: str = "owner-request"

    def __post_init__(self):
        if not isinstance(self.topic, str) or not 1 <= len(self.topic.strip()) <= 256:
            raise ValueError("topic must contain 1..256 characters")
        if any(ord(c) < 32 for c in self.topic):
            raise ValueError("topic contains control characters")
        if not re.fullmatch(r"[A-Za-z0-9_-]{1,64}", self.request_id):
            raise ValueError("request_id must use safe short identifier")
        _normalize_time(self.requested_at)


@dataclass(frozen=True)
class OnDemandResult:
    request_id: str
    executed_at: datetime
    status: str
    collection_status: str
    source_success_count: int
    source_failure_count: int
    finding_count: int
    distinct_source_id_count: int
    evidence_count: int
    ephemeral_workspace_removed: bool


def dispatch_offline_once(
    request: OnDemandRequest,
    *,
    adapters: Sequence[OfflineFixtureAdapter],
) -> OnDemandResult:
    """Execute exactly one user-invoked OFFLINE request; no network/default sources.

    All adapters must explicitly declare offline_fixture_only = True. The
    result exposes only aggregate counts. Source content, URLs, and SQLite are
    never returned or stored beyond the temporary workspace.
    """
    if not adapters or len(adapters) > 5:
        raise ValueError("expected 1..5 approved offline fixture adapters")
    if any(getattr(a, "offline_fixture_only", False) is not True for a in adapters):
        raise ValueError("live/network adapters are forbidden in offline dispatcher")
    ids = [getattr(a, "source_id", "") for a in adapters]
    if len(ids) != len(set(ids)):
        raise ValueError("duplicate source identities")
    when = _normalize_time(request.requested_at)
    with TemporaryDirectory(prefix="kgm-o1-offline-") as workspace:
        runtime = OperationalMonitoringRuntime(workspace)
        watch = runtime.create_watch(
            name="Ephemeral user request",
            query=request.topic,
            cadence_minutes=1440,
            enabled=True,
            created_at=when,
        )
        collector = LiveSourceCollector(runtime, list(adapters))
        cycle = LiveOperationalCycle(runtime, collector, LiveEndToEndProcessor(runtime))
        executions = cycle.execute_due(when)
        if len(executions) != 1:
            raise RuntimeError("one-shot request did not yield exactly one execution")
        execution = executions[0]
        # One collection per explicit one-shot invocation, never a permanent watch.
        with sqlite3.connect(runtime.database_path) as conn:
            row = conn.execute(
                "SELECT status,source_success_count,source_failure_count,item_count "
                "FROM source_collection_runs WHERE watch_id=?", (watch.watch_id,)
            ).fetchone()
            if row is None:
                raise RuntimeError("collection audit missing")
            origins = conn.execute(
                "SELECT COUNT(DISTINCT source_id) FROM raw_items WHERE id IN (SELECT raw_item_id FROM live_source_provenance "
                "WHERE collection_id IN (SELECT collection_id FROM source_collection_runs "
                "WHERE watch_id=?))", (watch.watch_id,)
            ).fetchone()[0]
        result = OnDemandResult(
            request_id=request.request_id,
            executed_at=when,
            status=execution.status,
            collection_status=str(row[0]),
            source_success_count=int(row[1]),
            source_failure_count=int(row[2]),
            finding_count=int(execution.result_count),
            distinct_source_id_count=int(origins),
            evidence_count=int(row[3]),
            ephemeral_workspace_removed=True,
        )
    return result
