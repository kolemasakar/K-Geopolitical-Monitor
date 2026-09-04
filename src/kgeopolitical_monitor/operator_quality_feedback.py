"""P16.5 append-only operator quality feedback persistence."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from hashlib import sha256
import re
import sqlite3
from typing import Final


P16_5_GATE: Final[str] = "P16_5_OPERATOR_QUALITY_FEEDBACK_PERSISTENCE_VALIDATED"
FEEDBACK_MODEL_VERSION: Final[str] = "KGM_OPERATOR_QUALITY_FEEDBACK_V1"
FEEDBACK_TYPES: Final[tuple[str, ...]] = (
    "USEFUL",
    "NOT_USEFUL",
    "TIMELY",
    "LATE",
    "DUPLICATE_NOISY",
    "MISSING_CONTEXT",
    "INCORRECT_PRIORITIZATION",
    "FACTUAL_CORRECTION_REQUESTED",
    "DELIVERY_FORMAT_ISSUE",
    "NOTE",
)

_SECRET_ASSIGNMENT = re.compile(
    r"(?i)\b(api[_-]?key|access[_-]?token|refresh[_-]?token|token|password|secret|bearer)\b\s*[:=]\s*[^\s,;]+"
)
_PATH_PATTERN = re.compile(r"(?i)(?:[a-z]:\\[^\s,;]+|/(?:home|opt|mnt|var/lib)/[^\s,;]+)")


@dataclass(frozen=True)
class OperatorQualityFeedback:
    feedback_id: str
    delivery_intent_id: str
    reviewed_transport_attempt_id: str | None
    canonical_object_type: str
    canonical_object_id: str
    feedback_type: str
    note: str | None
    created_at: str


def _utc_iso(value: datetime | None) -> str:
    current = value or datetime.now(timezone.utc)
    if current.tzinfo is None:
        current = current.replace(tzinfo=timezone.utc)
    return current.astimezone(timezone.utc).isoformat()


def sanitize_feedback_note(value: str | None) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    if not text:
        return None
    text = _SECRET_ASSIGNMENT.sub("[REDACTED_SECRET]", text)
    text = _PATH_PATTERN.sub("[REDACTED_PATH]", text)
    return text[:1000]


class SQLiteOperatorQualityFeedbackRepository:
    def __init__(self, connection: sqlite3.Connection):
        self.connection = connection

    def record_feedback(
        self,
        *,
        delivery_intent_id: str,
        feedback_type: str,
        note: str | None = None,
        reviewed_transport_attempt_id: str | None = None,
        created_at: datetime | None = None,
    ) -> OperatorQualityFeedback:
        normalized_type = str(feedback_type).strip().upper()
        if normalized_type not in FEEDBACK_TYPES:
            raise ValueError(f"unsupported feedback_type: {normalized_type}")
        intent = self.connection.execute(
            """
            SELECT canonical_object_type, canonical_object_id
            FROM delivery_intents WHERE delivery_intent_id = ?
            """,
            (delivery_intent_id,),
        ).fetchone()
        if intent is None:
            raise LookupError(f"unknown delivery_intent_id: {delivery_intent_id}")
        attempt_id = None
        if reviewed_transport_attempt_id is not None:
            attempt_id = str(reviewed_transport_attempt_id).strip() or None
        if attempt_id is not None:
            attempt = self.connection.execute(
                """
                SELECT 1 FROM delivery_transport_attempts
                WHERE transport_attempt_id = ? AND delivery_intent_id = ?
                """,
                (attempt_id, delivery_intent_id),
            ).fetchone()
            if attempt is None:
                raise LookupError("reviewed transport attempt does not belong to delivery intent")
        cleaned_note = sanitize_feedback_note(note)
        if normalized_type == "NOTE" and cleaned_note is None:
            raise ValueError("NOTE feedback requires a non-empty note")
        timestamp = _utc_iso(created_at)
        identity = "\0".join(
            (
                FEEDBACK_MODEL_VERSION,
                delivery_intent_id,
                attempt_id or "",
                normalized_type,
                timestamp,
                cleaned_note or "",
            )
        )
        feedback_id = f"OQF-{sha256(identity.encode('utf-8')).hexdigest()[:32]}"
        record = OperatorQualityFeedback(
            feedback_id=feedback_id,
            delivery_intent_id=delivery_intent_id,
            reviewed_transport_attempt_id=attempt_id,
            canonical_object_type=str(intent[0]),
            canonical_object_id=str(intent[1]),
            feedback_type=normalized_type,
            note=cleaned_note,
            created_at=timestamp,
        )
        self.connection.execute(
            """
            INSERT INTO operator_quality_feedback(
                feedback_id, delivery_intent_id, reviewed_transport_attempt_id,
                canonical_object_type, canonical_object_id, feedback_type, note, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                record.feedback_id,
                record.delivery_intent_id,
                record.reviewed_transport_attempt_id,
                record.canonical_object_type,
                record.canonical_object_id,
                record.feedback_type,
                record.note,
                record.created_at,
            ),
        )
        return record

    def list_feedback(self, delivery_intent_id: str) -> tuple[OperatorQualityFeedback, ...]:
        rows = self.connection.execute(
            """
            SELECT feedback_id, delivery_intent_id, reviewed_transport_attempt_id,
                   canonical_object_type, canonical_object_id, feedback_type, note, created_at
            FROM operator_quality_feedback
            WHERE delivery_intent_id = ?
            ORDER BY created_at ASC, feedback_id ASC
            """,
            (delivery_intent_id,),
        ).fetchall()
        return tuple(OperatorQualityFeedback(*tuple(row)) for row in rows)
