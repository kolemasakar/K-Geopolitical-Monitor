"""P16.1 canonical delivery-intent and append-only audit persistence.

This module records delivery intent only. It performs no network/provider action and
cannot alter canonical factual, alert, forecast, report, or finding state.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from hashlib import sha256
import sqlite3
from typing import Final


P16_1_GATE: Final[str] = "P16_1_CANONICAL_DELIVERY_INTENT_AUDIT_PERSISTENCE_VALIDATED"
DELIVERY_INTENT_MODEL_VERSION: Final[str] = "KGM_DELIVERY_INTENT_AUDIT_V1"

CANONICAL_OBJECT_TYPES: Final[tuple[str, ...]] = (
    "STRATEGIC_ALERT",
    "REPORT",
    "FINDING",
    "SEMANTIC_CLAIM",
)
EVENT_TYPES: Final[tuple[str, ...]] = ("INITIAL", "UPDATE", "RESOLUTION")
INTENT_STATES: Final[tuple[str, ...]] = ("PENDING", "SUPPRESSED", "READY")

_CANONICAL_LOOKUPS: Final[dict[str, tuple[str, str]]] = {
    "STRATEGIC_ALERT": ("strategic_alerts", "alert_id"),
    "REPORT": ("report_snapshots", "report_id"),
    "FINDING": ("operational_findings", "finding_id"),
    "SEMANTIC_CLAIM": ("semantic_claim_versions", "semantic_claim_id"),
}

_ALLOWED_TRANSITIONS: Final[dict[str, frozenset[str]]] = {
    "PENDING": frozenset(("SUPPRESSED", "READY")),
    "SUPPRESSED": frozenset(),
    "READY": frozenset(),
}


@dataclass(frozen=True)
class DeliveryIntent:
    delivery_intent_id: str
    canonical_object_type: str
    canonical_object_id: str
    event_type: str
    policy_key: str
    idempotency_key: str
    created_at: str


@dataclass(frozen=True)
class DeliveryIntentAuditEvent:
    delivery_audit_event_id: str
    delivery_intent_id: str
    event_sequence: int
    state: str
    reason_code: str | None
    detail: str | None
    recorded_at: str


def _utc_iso(value: datetime | None = None) -> str:
    current = value or datetime.now(timezone.utc)
    if current.tzinfo is None:
        current = current.replace(tzinfo=timezone.utc)
    return current.astimezone(timezone.utc).isoformat()


def _require_text(value: str, field: str) -> str:
    normalized = str(value).strip()
    if not normalized:
        raise ValueError(f"{field} must be non-empty")
    return normalized


def build_delivery_idempotency_key(
    canonical_object_type: str,
    canonical_object_id: str,
    event_type: str,
    *,
    policy_key: str = "DEFAULT",
) -> str:
    object_type = _require_text(canonical_object_type, "canonical_object_type").upper()
    object_id = _require_text(canonical_object_id, "canonical_object_id")
    event = _require_text(event_type, "event_type").upper()
    policy = _require_text(policy_key, "policy_key")
    if object_type not in CANONICAL_OBJECT_TYPES:
        raise ValueError(f"unsupported canonical_object_type: {object_type}")
    if event not in EVENT_TYPES:
        raise ValueError(f"unsupported event_type: {event}")
    payload = f"{DELIVERY_INTENT_MODEL_VERSION}\0{object_type}\0{object_id}\0{event}\0{policy}"
    return sha256(payload.encode("utf-8")).hexdigest()


def build_delivery_intent_id(idempotency_key: str) -> str:
    key = _require_text(idempotency_key, "idempotency_key")
    return f"DI-{key[:32]}"


def _row_to_intent(row: sqlite3.Row | tuple) -> DeliveryIntent:
    return DeliveryIntent(*tuple(row))


def _row_to_audit(row: sqlite3.Row | tuple) -> DeliveryIntentAuditEvent:
    return DeliveryIntentAuditEvent(*tuple(row))


class SQLiteDeliveryIntentRepository:
    """Append-only P16.1 repository with canonical-reference validation."""

    def __init__(self, connection: sqlite3.Connection):
        self.connection = connection

    def _canonical_exists(self, object_type: str, object_id: str) -> bool:
        table, column = _CANONICAL_LOOKUPS[object_type]
        row = self.connection.execute(
            f"SELECT 1 FROM {table} WHERE {column} = ? LIMIT 1",
            (object_id,),
        ).fetchone()
        return row is not None

    def get_intent(self, delivery_intent_id: str) -> DeliveryIntent | None:
        row = self.connection.execute(
            """
            SELECT delivery_intent_id, canonical_object_type, canonical_object_id,
                   event_type, policy_key, idempotency_key, created_at
            FROM delivery_intents
            WHERE delivery_intent_id = ?
            """,
            (delivery_intent_id,),
        ).fetchone()
        return None if row is None else _row_to_intent(row)

    def get_by_idempotency_key(self, idempotency_key: str) -> DeliveryIntent | None:
        row = self.connection.execute(
            """
            SELECT delivery_intent_id, canonical_object_type, canonical_object_id,
                   event_type, policy_key, idempotency_key, created_at
            FROM delivery_intents
            WHERE idempotency_key = ?
            """,
            (idempotency_key,),
        ).fetchone()
        return None if row is None else _row_to_intent(row)

    def list_audit_events(self, delivery_intent_id: str) -> tuple[DeliveryIntentAuditEvent, ...]:
        rows = self.connection.execute(
            """
            SELECT delivery_audit_event_id, delivery_intent_id, event_sequence,
                   state, reason_code, detail, recorded_at
            FROM delivery_intent_audit_events
            WHERE delivery_intent_id = ?
            ORDER BY event_sequence ASC
            """,
            (delivery_intent_id,),
        ).fetchall()
        return tuple(_row_to_audit(row) for row in rows)

    def current_state(self, delivery_intent_id: str) -> str | None:
        row = self.connection.execute(
            """
            SELECT state
            FROM delivery_intent_audit_events
            WHERE delivery_intent_id = ?
            ORDER BY event_sequence DESC
            LIMIT 1
            """,
            (delivery_intent_id,),
        ).fetchone()
        return None if row is None else str(row[0])

    def create_intent(
        self,
        *,
        canonical_object_type: str,
        canonical_object_id: str,
        event_type: str,
        policy_key: str = "DEFAULT",
        created_at: datetime | None = None,
    ) -> DeliveryIntent:
        object_type = _require_text(canonical_object_type, "canonical_object_type").upper()
        object_id = _require_text(canonical_object_id, "canonical_object_id")
        event = _require_text(event_type, "event_type").upper()
        policy = _require_text(policy_key, "policy_key")
        key = build_delivery_idempotency_key(object_type, object_id, event, policy_key=policy)
        existing = self.get_by_idempotency_key(key)
        if existing is not None:
            return existing
        if not self._canonical_exists(object_type, object_id):
            raise LookupError(
                f"canonical delivery reference does not exist: {object_type}:{object_id}"
            )

        intent = DeliveryIntent(
            delivery_intent_id=build_delivery_intent_id(key),
            canonical_object_type=object_type,
            canonical_object_id=object_id,
            event_type=event,
            policy_key=policy,
            idempotency_key=key,
            created_at=_utc_iso(created_at),
        )
        self.connection.execute(
            """
            INSERT INTO delivery_intents(
                delivery_intent_id, canonical_object_type, canonical_object_id,
                event_type, policy_key, idempotency_key, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                intent.delivery_intent_id,
                intent.canonical_object_type,
                intent.canonical_object_id,
                intent.event_type,
                intent.policy_key,
                intent.idempotency_key,
                intent.created_at,
            ),
        )
        self._append_event(
            intent.delivery_intent_id,
            state="PENDING",
            reason_code="INTENT_CREATED",
            detail=None,
            recorded_at=created_at,
        )
        return intent

    def append_intent_state(
        self,
        delivery_intent_id: str,
        *,
        state: str,
        reason_code: str | None = None,
        detail: str | None = None,
        recorded_at: datetime | None = None,
    ) -> DeliveryIntentAuditEvent:
        target = _require_text(state, "state").upper()
        if target not in INTENT_STATES:
            raise ValueError(f"P16.1 may record only intent states: {INTENT_STATES}")
        current = self.current_state(delivery_intent_id)
        if current is None:
            raise LookupError(f"unknown delivery_intent_id: {delivery_intent_id}")
        if target not in _ALLOWED_TRANSITIONS.get(current, frozenset()):
            raise ValueError(f"invalid delivery intent transition: {current} -> {target}")
        return self._append_event(
            delivery_intent_id,
            state=target,
            reason_code=reason_code,
            detail=detail,
            recorded_at=recorded_at,
        )

    def _append_event(
        self,
        delivery_intent_id: str,
        *,
        state: str,
        reason_code: str | None,
        detail: str | None,
        recorded_at: datetime | None,
    ) -> DeliveryIntentAuditEvent:
        next_sequence = int(
            self.connection.execute(
                "SELECT COALESCE(MAX(event_sequence), 0) + 1 FROM delivery_intent_audit_events WHERE delivery_intent_id = ?",
                (delivery_intent_id,),
            ).fetchone()[0]
        )
        event_payload = f"{delivery_intent_id}\0{next_sequence}\0{state}"
        audit_id = f"DIA-{sha256(event_payload.encode('utf-8')).hexdigest()[:32]}"
        event = DeliveryIntentAuditEvent(
            delivery_audit_event_id=audit_id,
            delivery_intent_id=delivery_intent_id,
            event_sequence=next_sequence,
            state=state,
            reason_code=None if reason_code is None else str(reason_code).strip() or None,
            detail=None if detail is None else str(detail).strip() or None,
            recorded_at=_utc_iso(recorded_at),
        )
        self.connection.execute(
            """
            INSERT INTO delivery_intent_audit_events(
                delivery_audit_event_id, delivery_intent_id, event_sequence,
                state, reason_code, detail, recorded_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                event.delivery_audit_event_id,
                event.delivery_intent_id,
                event.event_sequence,
                event.state,
                event.reason_code,
                event.detail,
                event.recorded_at,
            ),
        )
        return event
