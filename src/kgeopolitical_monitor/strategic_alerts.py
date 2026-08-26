"""M9 deterministic project-local strategic alert baseline."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from hashlib import sha256
import json
import sqlite3

from .live_end_to_end import normalize_claim_title
from .operational_monitoring import (
    MonitoringWatch,
    OperationalMonitoringRuntime,
    _normalize_time,
    utc_now,
)
from .operational_output import OperationalFinding


OPEN = "OPEN"
UPDATED = "UPDATED"
INVALIDATED = "INVALIDATED"
RESOLVED = "RESOLVED"

NORMAL = "NORMAL"
HIGH = "HIGH"
CRITICAL = "CRITICAL"

QUALIFYING_FINDING = "QUALIFYING_FINDING"

PRIORITY_RANK = {NORMAL: 0, HIGH: 1, CRITICAL: 2}
VERIFICATION_RANK = {"DETECTED": 0, "PARTLY_VERIFIED": 1, "VERIFIED": 2}


def _stable_id(prefix: str, value: str) -> str:
    digest = sha256(value.encode("utf-8")).hexdigest()[:24]
    return f"{prefix}-{digest}"


@dataclass(frozen=True)
class AlertPolicy:
    watch_id: str
    priority: str
    minimum_importance: float
    minimum_confidence: float
    minimum_verification_rank: int
    created_at: datetime
    updated_at: datetime


@dataclass(frozen=True)
class StrategicAlert:
    alert_id: str
    watch_id: str
    finding_id: str
    trigger_type: str
    dedup_key: str
    priority: str
    status: str
    first_triggered_at: datetime
    last_updated_at: datetime
    evidence_refs: tuple[str, ...]
    explanation: str
    invalidation_reason: str | None = None


@dataclass(frozen=True)
class AlertEvent:
    event_id: str
    alert_id: str
    event_type: str
    status: str
    event_at: datetime
    reason: str | None
    payload: dict[str, object]


@dataclass(frozen=True)
class PrioritizedWatch:
    watch: MonitoringWatch
    priority: str


class StrategicAlertService:
    """Persist and evaluate strategic alerts without external notification side effects."""

    def __init__(self, runtime: OperationalMonitoringRuntime):
        self.runtime = runtime
        self.database_path = runtime.database_path

    def configure_watch(
        self,
        watch_id: str,
        *,
        priority: str = NORMAL,
        minimum_importance: float = 0.5,
        minimum_confidence: float = 0.5,
        minimum_verification_rank: int = 0,
        configured_at: datetime | None = None,
    ) -> AlertPolicy:
        watch = self.runtime.repository.get_watch(watch_id)
        if watch is None:
            raise ValueError("watch does not exist")
        if priority not in PRIORITY_RANK:
            raise ValueError("unsupported alert priority")
        if not 0.0 <= minimum_importance <= 1.0:
            raise ValueError("minimum_importance must be between 0 and 1")
        if not 0.0 <= minimum_confidence <= 1.0:
            raise ValueError("minimum_confidence must be between 0 and 1")
        if minimum_verification_rank not in {0, 1, 2}:
            raise ValueError("minimum_verification_rank must be 0, 1 or 2")

        timestamp = _normalize_time(configured_at or utc_now())
        with sqlite3.connect(self.database_path) as connection:
            connection.execute("PRAGMA foreign_keys = ON")
            connection.execute(
                """
                INSERT INTO monitoring_watch_alert_policies(
                    watch_id, priority, minimum_importance, minimum_confidence,
                    minimum_verification_rank, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(watch_id) DO UPDATE SET
                    priority = excluded.priority,
                    minimum_importance = excluded.minimum_importance,
                    minimum_confidence = excluded.minimum_confidence,
                    minimum_verification_rank = excluded.minimum_verification_rank,
                    updated_at = excluded.updated_at
                """,
                (
                    watch_id,
                    priority,
                    minimum_importance,
                    minimum_confidence,
                    minimum_verification_rank,
                    timestamp.isoformat(),
                    timestamp.isoformat(),
                ),
            )
        policy = self.get_policy(watch_id)
        if policy is None:
            raise RuntimeError("failed to persist alert policy")
        return policy

    def get_policy(self, watch_id: str) -> AlertPolicy | None:
        with sqlite3.connect(self.database_path) as connection:
            row = connection.execute(
                """
                SELECT watch_id, priority, minimum_importance, minimum_confidence,
                       minimum_verification_rank, created_at, updated_at
                FROM monitoring_watch_alert_policies
                WHERE watch_id = ?
                """,
                (watch_id,),
            ).fetchone()
        if row is None:
            return None
        return AlertPolicy(
            watch_id=row[0],
            priority=row[1],
            minimum_importance=float(row[2]),
            minimum_confidence=float(row[3]),
            minimum_verification_rank=int(row[4]),
            created_at=datetime.fromisoformat(row[5]),
            updated_at=datetime.fromisoformat(row[6]),
        )

    def _finding(self, finding_id: str) -> OperationalFinding | None:
        with sqlite3.connect(self.database_path) as connection:
            row = connection.execute(
                """
                SELECT finding_id, run_id, watch_id, title, summary, importance,
                       confidence, evidence_refs, explanation, created_at
                FROM operational_findings
                WHERE finding_id = ?
                """,
                (finding_id,),
            ).fetchone()
        if row is None:
            return None
        return OperationalFinding(
            finding_id=row[0],
            run_id=row[1],
            watch_id=row[2],
            title=row[3],
            summary=row[4],
            importance=float(row[5]),
            confidence=float(row[6]),
            evidence_refs=tuple(json.loads(row[7])),
            explanation=row[8],
            created_at=datetime.fromisoformat(row[9]),
        )

    def _verification_status(self, finding: OperationalFinding) -> str | None:
        claim_refs = [
            ref.split(":", 1)[1]
            for ref in finding.evidence_refs
            if ref.startswith("claim:") and len(ref.split(":", 1)) == 2
        ]
        if len(claim_refs) != 1:
            return None
        with sqlite3.connect(self.database_path) as connection:
            row = connection.execute(
                """
                SELECT verification_status
                FROM live_analysis_claims
                WHERE claim_id = ?
                """,
                (claim_refs[0],),
            ).fetchone()
        if row is None or row[0] not in VERIFICATION_RANK:
            return None
        return row[0]

    def _row_to_alert(self, row: tuple) -> StrategicAlert:
        return StrategicAlert(
            alert_id=row[0],
            watch_id=row[1],
            finding_id=row[2],
            trigger_type=row[3],
            dedup_key=row[4],
            priority=row[5],
            status=row[6],
            first_triggered_at=datetime.fromisoformat(row[7]),
            last_updated_at=datetime.fromisoformat(row[8]),
            evidence_refs=tuple(json.loads(row[9])),
            explanation=row[10],
            invalidation_reason=row[11],
        )

    def get_alert(self, alert_id: str) -> StrategicAlert | None:
        with sqlite3.connect(self.database_path) as connection:
            row = connection.execute(
                """
                SELECT alert_id, watch_id, finding_id, trigger_type, dedup_key,
                       priority, status, first_triggered_at, last_updated_at,
                       evidence_refs, explanation, invalidation_reason
                FROM strategic_alerts
                WHERE alert_id = ?
                """,
                (alert_id,),
            ).fetchone()
        return None if row is None else self._row_to_alert(row)

    def _existing_alert(
        self,
        watch_id: str,
        trigger_type: str,
        dedup_key: str,
    ) -> StrategicAlert | None:
        with sqlite3.connect(self.database_path) as connection:
            row = connection.execute(
                """
                SELECT alert_id, watch_id, finding_id, trigger_type, dedup_key,
                       priority, status, first_triggered_at, last_updated_at,
                       evidence_refs, explanation, invalidation_reason
                FROM strategic_alerts
                WHERE watch_id = ? AND trigger_type = ? AND dedup_key = ?
                """,
                (watch_id, trigger_type, dedup_key),
            ).fetchone()
        return None if row is None else self._row_to_alert(row)

    def _record_event(
        self,
        alert_id: str,
        event_type: str,
        status: str,
        event_at: datetime,
        *,
        reason: str | None = None,
        payload: dict[str, object] | None = None,
    ) -> None:
        payload = payload or {}
        canonical_payload = json.dumps(payload, sort_keys=True)
        identity = (
            f"{alert_id}:{event_type}:{status}:{event_at.isoformat()}:"
            f"{reason or ''}:{canonical_payload}"
        )
        event_id = _stable_id("alert-event", identity)
        with sqlite3.connect(self.database_path) as connection:
            connection.execute("PRAGMA foreign_keys = ON")
            connection.execute(
                """
                INSERT INTO strategic_alert_events(
                    event_id, alert_id, event_type, status, event_at, reason, payload_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(event_id) DO NOTHING
                """,
                (
                    event_id,
                    alert_id,
                    event_type,
                    status,
                    event_at.isoformat(),
                    reason,
                    canonical_payload,
                ),
            )

    def _qualifies(
        self,
        finding: OperationalFinding,
        policy: AlertPolicy,
    ) -> tuple[bool, str | None]:
        verification_status = self._verification_status(finding)
        verification_rank = (
            VERIFICATION_RANK[verification_status]
            if verification_status in VERIFICATION_RANK
            else -1
        )
        qualifies = (
            finding.importance >= policy.minimum_importance
            and finding.confidence >= policy.minimum_confidence
            and verification_rank >= policy.minimum_verification_rank
        )
        return qualifies, verification_status

    def _explanation(
        self,
        finding: OperationalFinding,
        policy: AlertPolicy,
        verification_status: str,
    ) -> str:
        return (
            f"trigger={QUALIFYING_FINDING}; "
            f"importance={finding.importance:.3f}>={policy.minimum_importance:.3f}; "
            f"confidence={finding.confidence:.3f}>={policy.minimum_confidence:.3f}; "
            f"verification_status={verification_status}; "
            f"verification_rank={VERIFICATION_RANK[verification_status]}>="
            f"{policy.minimum_verification_rank}; "
            "priority affects alert handling only and does not modify evidence confidence."
        )

    def evaluate_finding(
        self,
        finding_id: str,
        *,
        evaluated_at: datetime | None = None,
    ) -> StrategicAlert | None:
        current = _normalize_time(evaluated_at or utc_now())
        finding = self._finding(finding_id)
        if finding is None:
            raise ValueError("operational finding does not exist")
        policy = self.get_policy(finding.watch_id)
        if policy is None:
            return None

        dedup_key = normalize_claim_title(finding.title)
        if not dedup_key:
            return None

        existing = self._existing_alert(
            finding.watch_id,
            QUALIFYING_FINDING,
            dedup_key,
        )
        qualifies, verification_status = self._qualifies(finding, policy)
        if not qualifies or verification_status is None:
            return None

        explanation = self._explanation(finding, policy, verification_status)
        evidence_refs_json = json.dumps(finding.evidence_refs)
        if existing is not None:
            if existing.status in {INVALIDATED, RESOLVED}:
                return existing
            if (
                existing.finding_id == finding.finding_id
                and existing.priority == policy.priority
                and existing.evidence_refs == finding.evidence_refs
                and existing.explanation == explanation
            ):
                return existing

            previous_finding_id = existing.finding_id
            with sqlite3.connect(self.database_path) as connection:
                connection.execute("PRAGMA foreign_keys = ON")
                connection.execute(
                    """
                    UPDATE strategic_alerts
                    SET finding_id = ?, priority = ?, status = 'UPDATED',
                        last_updated_at = ?, evidence_refs = ?, explanation = ?,
                        invalidation_reason = NULL
                    WHERE alert_id = ?
                    """,
                    (
                        finding.finding_id,
                        policy.priority,
                        current.isoformat(),
                        evidence_refs_json,
                        explanation,
                        existing.alert_id,
                    ),
                )
            self._record_event(
                existing.alert_id,
                "FINDING_UPDATED",
                UPDATED,
                current,
                payload={
                    "previous_finding_id": previous_finding_id,
                    "finding_id": finding.finding_id,
                    "verification_status": verification_status,
                    "priority": policy.priority,
                },
            )
            return self.get_alert(existing.alert_id)

        alert_id = _stable_id(
            "alert",
            f"{finding.watch_id}:{QUALIFYING_FINDING}:{dedup_key}",
        )
        with sqlite3.connect(self.database_path) as connection:
            connection.execute("PRAGMA foreign_keys = ON")
            connection.execute(
                """
                INSERT INTO strategic_alerts(
                    alert_id, watch_id, finding_id, trigger_type, dedup_key,
                    priority, status, first_triggered_at, last_updated_at,
                    evidence_refs, explanation, invalidation_reason
                ) VALUES (?, ?, ?, ?, ?, ?, 'OPEN', ?, ?, ?, ?, NULL)
                """,
                (
                    alert_id,
                    finding.watch_id,
                    finding.finding_id,
                    QUALIFYING_FINDING,
                    dedup_key,
                    policy.priority,
                    current.isoformat(),
                    current.isoformat(),
                    evidence_refs_json,
                    explanation,
                ),
            )
        self._record_event(
            alert_id,
            "TRIGGERED",
            OPEN,
            current,
            payload={
                "finding_id": finding.finding_id,
                "verification_status": verification_status,
                "priority": policy.priority,
            },
        )
        return self.get_alert(alert_id)

    def evaluate_watch(
        self,
        watch_id: str,
        *,
        evaluated_at: datetime | None = None,
    ) -> list[StrategicAlert]:
        if self.runtime.repository.get_watch(watch_id) is None:
            raise ValueError("watch does not exist")
        if self.get_policy(watch_id) is None:
            return []

        with sqlite3.connect(self.database_path) as connection:
            finding_ids = [
                row[0]
                for row in connection.execute(
                    """
                    SELECT finding_id
                    FROM operational_findings
                    WHERE watch_id = ?
                    ORDER BY created_at ASC, finding_id ASC
                    """,
                    (watch_id,),
                ).fetchall()
            ]

        alerts: dict[str, StrategicAlert] = {}
        for finding_id in finding_ids:
            alert = self.evaluate_finding(finding_id, evaluated_at=evaluated_at)
            if alert is not None:
                alerts[alert.alert_id] = alert
        return sorted(
            alerts.values(),
            key=lambda alert: (
                -PRIORITY_RANK[alert.priority],
                alert.first_triggered_at,
                alert.alert_id,
            ),
        )

    def invalidate(
        self,
        alert_id: str,
        reason: str,
        *,
        invalidated_at: datetime | None = None,
    ) -> StrategicAlert:
        if not reason.strip():
            raise ValueError("alert invalidation requires a reason")
        current = _normalize_time(invalidated_at or utc_now())
        alert = self.get_alert(alert_id)
        if alert is None:
            raise ValueError("strategic alert does not exist")
        if alert.status == RESOLVED:
            raise ValueError("resolved alert cannot be invalidated")
        if alert.status == INVALIDATED:
            return alert

        with sqlite3.connect(self.database_path) as connection:
            connection.execute(
                """
                UPDATE strategic_alerts
                SET status = 'INVALIDATED', last_updated_at = ?,
                    invalidation_reason = ?
                WHERE alert_id = ?
                """,
                (current.isoformat(), reason.strip(), alert_id),
            )
        self._record_event(
            alert_id,
            "INVALIDATED",
            INVALIDATED,
            current,
            reason=reason.strip(),
            payload={"finding_id": alert.finding_id},
        )
        updated = self.get_alert(alert_id)
        if updated is None:
            raise RuntimeError("failed to persist alert invalidation")
        return updated

    def resolve(
        self,
        alert_id: str,
        reason: str,
        *,
        resolved_at: datetime | None = None,
    ) -> StrategicAlert:
        if not reason.strip():
            raise ValueError("alert resolution requires a reason")
        current = _normalize_time(resolved_at or utc_now())
        alert = self.get_alert(alert_id)
        if alert is None:
            raise ValueError("strategic alert does not exist")
        if alert.status == RESOLVED:
            return alert

        with sqlite3.connect(self.database_path) as connection:
            connection.execute(
                """
                UPDATE strategic_alerts
                SET status = 'RESOLVED', last_updated_at = ?,
                    invalidation_reason = ?
                WHERE alert_id = ?
                """,
                (current.isoformat(), reason.strip(), alert_id),
            )
        self._record_event(
            alert_id,
            "RESOLVED",
            RESOLVED,
            current,
            reason=reason.strip(),
            payload={"finding_id": alert.finding_id},
        )
        updated = self.get_alert(alert_id)
        if updated is None:
            raise RuntimeError("failed to persist alert resolution")
        return updated

    def event_history(self, alert_id: str) -> list[AlertEvent]:
        if self.get_alert(alert_id) is None:
            raise ValueError("strategic alert does not exist")
        with sqlite3.connect(self.database_path) as connection:
            rows = connection.execute(
                """
                SELECT event_id, alert_id, event_type, status, event_at, reason, payload_json
                FROM strategic_alert_events
                WHERE alert_id = ?
                ORDER BY event_at ASC, event_id ASC
                """,
                (alert_id,),
            ).fetchall()
        return [
            AlertEvent(
                event_id=row[0],
                alert_id=row[1],
                event_type=row[2],
                status=row[3],
                event_at=datetime.fromisoformat(row[4]),
                reason=row[5],
                payload=json.loads(row[6]),
            )
            for row in rows
        ]

    def prioritized_due_watches(
        self,
        now: datetime | None = None,
    ) -> list[PrioritizedWatch]:
        due = self.runtime.due_watches(now)
        prioritized: list[PrioritizedWatch] = []
        for watch in due:
            policy = self.get_policy(watch.watch_id)
            priority = policy.priority if policy is not None else NORMAL
            prioritized.append(PrioritizedWatch(watch=watch, priority=priority))
        return sorted(
            prioritized,
            key=lambda item: (-PRIORITY_RANK[item.priority], item.watch.watch_id),
        )
