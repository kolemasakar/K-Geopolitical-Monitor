"""P16.4 owner-only read model for delivery/operator experience.

The projection is deliberately read-only. It exposes persisted delivery evidence and
operator-oriented explanations without enabling delivery, feedback mutation, public
API ingress, or factual-verification changes.
"""

from __future__ import annotations

from dataclasses import dataclass
import sqlite3
from typing import Final


P16_4_GATE: Final[str] = "P16_4_OWNER_OPERATOR_EXPERIENCE_PROJECTION_VALIDATED"
OWNER_DELIVERY_PROJECTION_VERSION: Final[str] = "KGM_OWNER_DELIVERY_EXPERIENCE_V1"


@dataclass(frozen=True)
class OwnerDeliveryExperienceRow:
    delivery_intent_id: str
    canonical_object_type: str
    canonical_object_id: str
    event_type: str
    policy_key: str
    created_at: str
    current_state: str
    latest_reason_code: str | None
    attempt_count: int
    latest_transport_name: str | None
    latest_transport_state: str | None
    latest_error_code: str | None
    latest_error_detail: str | None
    receipt_type: str | None
    receipt_reference: str | None
    payload_redaction_required: bool
    payload_persisted: bool
    feedback_action_available: bool
    limitations: tuple[str, ...]


class SQLiteOwnerDeliveryExperienceProjection:
    def __init__(self, connection: sqlite3.Connection):
        self.connection = connection

    def _table_exists(self, name: str) -> bool:
        row = self.connection.execute(
            "SELECT 1 FROM sqlite_master WHERE type='table' AND name=? LIMIT 1",
            (name,),
        ).fetchone()
        return row is not None

    def list_rows(self, *, limit: int = 100) -> tuple[OwnerDeliveryExperienceRow, ...]:
        if not 1 <= limit <= 1000:
            raise ValueError("limit must be in 1..1000")
        feedback_available = self._table_exists("operator_quality_feedback")
        intents = self.connection.execute(
            """
            SELECT delivery_intent_id, canonical_object_type, canonical_object_id,
                   event_type, policy_key, created_at
            FROM delivery_intents
            ORDER BY created_at DESC, delivery_intent_id ASC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()
        output: list[OwnerDeliveryExperienceRow] = []
        for intent in intents:
            intent_id = str(intent[0])
            audit = self.connection.execute(
                """
                SELECT state, reason_code
                FROM delivery_intent_audit_events
                WHERE delivery_intent_id = ?
                ORDER BY event_sequence DESC LIMIT 1
                """,
                (intent_id,),
            ).fetchone()
            attempts = self.connection.execute(
                "SELECT COUNT(*) FROM delivery_transport_attempts WHERE delivery_intent_id = ?",
                (intent_id,),
            ).fetchone()[0]
            latest_attempt = self.connection.execute(
                """
                SELECT transport_attempt_id, transport_name, state, error_code, error_detail
                FROM delivery_transport_attempts
                WHERE delivery_intent_id = ?
                ORDER BY attempt_sequence DESC LIMIT 1
                """,
                (intent_id,),
            ).fetchone()
            receipt = None
            if latest_attempt is not None:
                receipt = self.connection.execute(
                    """
                    SELECT receipt_type, external_reference
                    FROM delivery_receipts
                    WHERE transport_attempt_id = ?
                    ORDER BY recorded_at DESC, delivery_receipt_id ASC LIMIT 1
                    """,
                    (latest_attempt[0],),
                ).fetchone()
            current_state = "UNKNOWN" if audit is None else str(audit[0])
            output.append(
                OwnerDeliveryExperienceRow(
                    delivery_intent_id=intent_id,
                    canonical_object_type=str(intent[1]),
                    canonical_object_id=str(intent[2]),
                    event_type=str(intent[3]),
                    policy_key=str(intent[4]),
                    created_at=str(intent[5]),
                    current_state=current_state,
                    latest_reason_code=None if audit is None else audit[1],
                    attempt_count=int(attempts),
                    latest_transport_name=None if latest_attempt is None else latest_attempt[1],
                    latest_transport_state=None if latest_attempt is None else latest_attempt[2],
                    latest_error_code=None if latest_attempt is None else latest_attempt[3],
                    latest_error_detail=None if latest_attempt is None else latest_attempt[4],
                    receipt_type=None if receipt is None else receipt[0],
                    receipt_reference=None if receipt is None else receipt[1],
                    payload_redaction_required=True,
                    payload_persisted=False,
                    feedback_action_available=feedback_available
                    and current_state in {"DELIVERED", "FAILED", "SUPPRESSED"},
                    limitations=(
                        "OWNER_READ_ONLY",
                        "DELIVERY_STATE_NOT_FACTUAL_VERIFICATION",
                        "NO_PUBLIC_INGRESS",
                    ),
                )
            )
        return tuple(output)
