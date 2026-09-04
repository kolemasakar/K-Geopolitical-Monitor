"""P16.2 deterministic delivery policy, redaction and minimized payload projection."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import re
import sqlite3
from typing import Final

from .delivery_intent_persistence import SQLiteDeliveryIntentRepository


P16_2_GATE: Final[str] = "P16_2_DELIVERY_POLICY_REDACTION_VALIDATED"
DELIVERY_POLICY_VERSION: Final[str] = "KGM_DELIVERY_POLICY_REDACTION_V1"

_PRIORITY_RANK: Final[dict[str, int]] = {"NORMAL": 0, "HIGH": 1, "CRITICAL": 2}
_ALLOWED_PAYLOAD_FIELDS: Final[frozenset[str]] = frozenset(
    {
        "delivery_intent_id",
        "canonical_object_type",
        "canonical_object_id",
        "event_type",
        "title",
        "summary",
        "priority",
        "canonical_status",
        "escalation_level",
        "limitations",
        "provenance_labels",
        "redactions_applied",
    }
)
_SECRET_ASSIGNMENT = re.compile(
    r"(?i)\b(api[_-]?key|access[_-]?token|refresh[_-]?token|token|password|secret|bearer)\b\s*[:=]\s*[^\s,;]+"
)
_PATH_PATTERN = re.compile(r"(?i)(?:[a-z]:\\[^\s,;]+|/(?:home|opt|mnt|var/lib)/[^\s,;]+)")


@dataclass(frozen=True)
class QuietHours:
    start_hour_utc: int
    end_hour_utc: int

    def __post_init__(self) -> None:
        for value in (self.start_hour_utc, self.end_hour_utc):
            if not 0 <= value <= 23:
                raise ValueError("quiet-hours values must be UTC hours in 0..23")

    def contains(self, hour: int) -> bool:
        if self.start_hour_utc == self.end_hour_utc:
            return True
        if self.start_hour_utc < self.end_hour_utc:
            return self.start_hour_utc <= hour < self.end_hour_utc
        return hour >= self.start_hour_utc or hour < self.end_hour_utc


@dataclass(frozen=True)
class DeliveryPolicyConfig:
    policy_key: str = "DEFAULT"
    minimum_alert_priority: str = "NORMAL"
    quiet_hours: QuietHours | None = None
    maximum_escalation_level: int = 2

    def __post_init__(self) -> None:
        if self.minimum_alert_priority not in _PRIORITY_RANK:
            raise ValueError("unsupported minimum_alert_priority")
        if not 0 <= self.maximum_escalation_level <= 2:
            raise ValueError("maximum_escalation_level must be in 0..2")


@dataclass(frozen=True)
class DeliveryPayload:
    delivery_intent_id: str
    canonical_object_type: str
    canonical_object_id: str
    event_type: str
    title: str
    summary: str
    priority: str
    canonical_status: str
    escalation_level: int
    limitations: tuple[str, ...]
    provenance_labels: tuple[str, ...]
    redactions_applied: bool

    def as_transport_dict(self) -> dict[str, object]:
        payload = asdict(self)
        if set(payload) != _ALLOWED_PAYLOAD_FIELDS:
            raise RuntimeError("delivery payload allowlist drift detected")
        return payload


@dataclass(frozen=True)
class DeliveryPolicyDecision:
    delivery_intent_id: str
    state: str
    reason_code: str
    payload: DeliveryPayload | None


def _utc(value: datetime | None) -> datetime:
    result = value or datetime.now(timezone.utc)
    if result.tzinfo is None:
        result = result.replace(tzinfo=timezone.utc)
    return result.astimezone(timezone.utc)


def _sanitize(value: object) -> tuple[str, bool]:
    text = str(value or "").strip()
    sanitized, count_secret = _SECRET_ASSIGNMENT.subn("[REDACTED_SECRET]", text)
    sanitized, count_path = _PATH_PATTERN.subn("[REDACTED_PATH]", sanitized)
    return sanitized[:2000], bool(count_secret or count_path)


class SQLiteDeliveryPolicyProjector:
    """Read canonical state, evaluate delivery policy, and emit minimized payloads."""

    def __init__(self, connection: sqlite3.Connection, config: DeliveryPolicyConfig | None = None):
        self.connection = connection
        self.config = config or DeliveryPolicyConfig()
        self.intents = SQLiteDeliveryIntentRepository(connection)

    def _load_canonical(self, object_type: str, object_id: str) -> dict[str, object] | None:
        if object_type == "REPORT":
            row = self.connection.execute(
                "SELECT title, summary, report_type, 'SNAPSHOT' FROM report_snapshots WHERE report_id = ?",
                (object_id,),
            ).fetchone()
            if row is None:
                return None
            return {"title": row[0], "summary": row[1], "priority": "NORMAL", "status": row[3]}
        if object_type == "FINDING":
            row = self.connection.execute(
                "SELECT title, summary, importance FROM operational_findings WHERE finding_id = ?",
                (object_id,),
            ).fetchone()
            if row is None:
                return None
            priority = "CRITICAL" if float(row[2]) >= 0.9 else "HIGH" if float(row[2]) >= 0.7 else "NORMAL"
            return {"title": row[0], "summary": row[1], "priority": priority, "status": "OBSERVED"}
        if object_type == "STRATEGIC_ALERT":
            row = self.connection.execute(
                """
                SELECT f.title, f.summary, a.priority, a.status
                FROM strategic_alerts a
                LEFT JOIN operational_findings f ON f.finding_id = a.finding_id
                WHERE a.alert_id = ?
                """,
                (object_id,),
            ).fetchone()
            if row is None or row[0] is None:
                return None
            return {"title": row[0], "summary": row[1], "priority": row[2], "status": row[3]}
        if object_type == "SEMANTIC_CLAIM":
            rows = self.connection.execute(
                """
                SELECT normalized_proposition, modality, semantic_version
                FROM semantic_claim_versions
                WHERE semantic_claim_id = ?
                ORDER BY semantic_version DESC
                LIMIT 2
                """,
                (object_id,),
            ).fetchall()
            if not rows:
                return None
            return {
                "title": "Semantic claim",
                "summary": rows[0][0],
                "priority": "NORMAL",
                "status": str(rows[0][1]),
            }
        return None

    def evaluate(
        self,
        delivery_intent_id: str,
        *,
        evaluated_at: datetime | None = None,
        reference_stale: bool = False,
        reference_ambiguous: bool = False,
    ) -> DeliveryPolicyDecision:
        intent = self.intents.get_intent(delivery_intent_id)
        if intent is None:
            raise LookupError(f"unknown delivery_intent_id: {delivery_intent_id}")
        current = self.intents.current_state(delivery_intent_id)
        if current != "PENDING":
            return DeliveryPolicyDecision(delivery_intent_id, "SUPPRESSED", "INTENT_NOT_PENDING", None)
        if reference_stale:
            return DeliveryPolicyDecision(delivery_intent_id, "SUPPRESSED", "CANONICAL_REFERENCE_STALE", None)
        if reference_ambiguous:
            return DeliveryPolicyDecision(delivery_intent_id, "SUPPRESSED", "CANONICAL_REFERENCE_AMBIGUOUS", None)

        canonical = self._load_canonical(intent.canonical_object_type, intent.canonical_object_id)
        if canonical is None:
            return DeliveryPolicyDecision(delivery_intent_id, "SUPPRESSED", "CANONICAL_REFERENCE_UNAVAILABLE", None)

        priority = str(canonical["priority"])
        if intent.canonical_object_type == "STRATEGIC_ALERT" and (
            _PRIORITY_RANK.get(priority, -1) < _PRIORITY_RANK[self.config.minimum_alert_priority]
        ):
            return DeliveryPolicyDecision(delivery_intent_id, "SUPPRESSED", "PRIORITY_BELOW_POLICY", None)

        when = _utc(evaluated_at)
        if self.config.quiet_hours is not None and self.config.quiet_hours.contains(when.hour):
            return DeliveryPolicyDecision(delivery_intent_id, "SUPPRESSED", "QUIET_HOURS", None)

        delivered = self.connection.execute(
            "SELECT 1 FROM delivery_transport_attempts WHERE delivery_intent_id = ? AND state = 'DELIVERED' LIMIT 1",
            (delivery_intent_id,),
        ).fetchone()
        if delivered is not None:
            return DeliveryPolicyDecision(delivery_intent_id, "SUPPRESSED", "ALREADY_DELIVERED", None)

        title, title_redacted = _sanitize(canonical["title"])
        summary, summary_redacted = _sanitize(canonical["summary"])
        escalation = min(_PRIORITY_RANK.get(priority, 0), self.config.maximum_escalation_level)
        payload = DeliveryPayload(
            delivery_intent_id=intent.delivery_intent_id,
            canonical_object_type=intent.canonical_object_type,
            canonical_object_id=intent.canonical_object_id,
            event_type=intent.event_type,
            title=title,
            summary=summary,
            priority=priority,
            canonical_status=str(canonical["status"]),
            escalation_level=escalation,
            limitations=("DELIVERY_VIEW_ONLY", "NOT_FACTUAL_VERIFICATION"),
            provenance_labels=(
                f"CANONICAL_REFERENCE:{intent.canonical_object_type}",
                f"POLICY:{self.config.policy_key}",
            ),
            redactions_applied=title_redacted or summary_redacted,
        )
        payload.as_transport_dict()
        return DeliveryPolicyDecision(delivery_intent_id, "READY", "POLICY_READY", payload)

    def apply(self, decision: DeliveryPolicyDecision) -> None:
        if decision.state not in {"READY", "SUPPRESSED"}:
            raise ValueError("P16.2 policy may apply only READY or SUPPRESSED")
        self.intents.append_intent_state(
            decision.delivery_intent_id,
            state=decision.state,
            reason_code=decision.reason_code,
        )
