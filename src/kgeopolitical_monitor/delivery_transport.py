"""P16.3 provider-neutral delivery transport with deterministic local validation.

No external provider is configured or activated by this module. The canonical test
transport is an in-memory sink and retry timing is represented as evidence only;
there is no sleeping or network I/O here.
"""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import sqlite3
from typing import Final, Mapping, Protocol, Sequence

from .delivery_policy import DeliveryPayload


P16_3_GATE: Final[str] = "P16_3_PROVIDER_NEUTRAL_DELIVERY_TRANSPORT_VALIDATED"
TRANSPORT_MODEL_VERSION: Final[str] = "KGM_PROVIDER_NEUTRAL_DELIVERY_TRANSPORT_V1"
DEFAULT_BACKOFF_SECONDS: Final[tuple[int, ...]] = (0, 5, 15)


@dataclass(frozen=True)
class TransportSendResult:
    success: bool
    receipt_type: str = "LOCAL_TEST"
    external_reference: str | None = None
    error_code: str | None = None
    error_detail: str | None = None


class DeliveryTransport(Protocol):
    name: str

    def send(
        self,
        payload: Mapping[str, object],
        *,
        idempotency_key: str,
        attempt_sequence: int,
    ) -> TransportSendResult: ...


class InMemoryDeliverySink:
    """Deterministic engineering sink; never performs network I/O."""

    name = "IN_MEMORY_TEST"

    def __init__(self, outcomes: Sequence[TransportSendResult | bool] | None = None):
        self._outcomes = list(outcomes or (True,))
        self.sent: list[dict[str, object]] = []

    def send(
        self,
        payload: Mapping[str, object],
        *,
        idempotency_key: str,
        attempt_sequence: int,
    ) -> TransportSendResult:
        self.sent.append(
            {
                "payload": dict(payload),
                "idempotency_key": idempotency_key,
                "attempt_sequence": attempt_sequence,
            }
        )
        index = min(attempt_sequence - 1, len(self._outcomes) - 1)
        outcome = self._outcomes[index]
        if isinstance(outcome, TransportSendResult):
            return outcome
        if outcome:
            return TransportSendResult(
                success=True,
                external_reference=f"memory:{idempotency_key[:12]}:{attempt_sequence}",
            )
        return TransportSendResult(
            success=False,
            error_code="DETERMINISTIC_TEST_FAILURE",
            error_detail="in-memory sink configured failure",
        )


@dataclass(frozen=True)
class DeliveryDispatchResult:
    delivery_intent_id: str
    state: str
    attempts_made: int
    backoff_seconds: tuple[int, ...]
    receipt_id: str | None


def _digest_id(prefix: str, *parts: object) -> str:
    payload = "\0".join(str(part) for part in parts)
    return f"{prefix}-{sha256(payload.encode('utf-8')).hexdigest()[:32]}"


def _clean_optional(value: str | None, *, limit: int = 1000) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text[:limit] or None


class SQLiteDeliveryDispatcher:
    """Persist transport evidence while isolating provider failure from analysis state."""

    def __init__(
        self,
        connection: sqlite3.Connection,
        transport: DeliveryTransport,
        *,
        max_attempts: int = 3,
        backoff_seconds: Sequence[int] = DEFAULT_BACKOFF_SECONDS,
    ):
        if not 1 <= max_attempts <= 10:
            raise ValueError("max_attempts must be in 1..10")
        normalized = tuple(int(value) for value in backoff_seconds)
        if len(normalized) < max_attempts or any(value < 0 for value in normalized):
            raise ValueError("backoff_seconds must provide non-negative values for each attempt")
        self.connection = connection
        self.transport = transport
        self.max_attempts = max_attempts
        self.backoff_seconds = normalized[:max_attempts]

    def _intent_row(self, delivery_intent_id: str):
        return self.connection.execute(
            """
            SELECT delivery_intent_id, idempotency_key
            FROM delivery_intents
            WHERE delivery_intent_id = ?
            """,
            (delivery_intent_id,),
        ).fetchone()

    def _current_state(self, delivery_intent_id: str) -> str | None:
        row = self.connection.execute(
            """
            SELECT state FROM delivery_intent_audit_events
            WHERE delivery_intent_id = ?
            ORDER BY event_sequence DESC LIMIT 1
            """,
            (delivery_intent_id,),
        ).fetchone()
        return None if row is None else str(row[0])

    def _already_delivered(self, delivery_intent_id: str) -> tuple[bool, str | None]:
        row = self.connection.execute(
            """
            SELECT r.delivery_receipt_id
            FROM delivery_transport_attempts a
            LEFT JOIN delivery_receipts r ON r.transport_attempt_id = a.transport_attempt_id
            WHERE a.delivery_intent_id = ? AND a.state = 'DELIVERED'
            ORDER BY a.attempt_sequence ASC LIMIT 1
            """,
            (delivery_intent_id,),
        ).fetchone()
        return (row is not None, None if row is None else row[0])

    def _append_audit(self, delivery_intent_id: str, state: str, reason_code: str) -> None:
        sequence = int(
            self.connection.execute(
                "SELECT COALESCE(MAX(event_sequence), 0) + 1 FROM delivery_intent_audit_events WHERE delivery_intent_id = ?",
                (delivery_intent_id,),
            ).fetchone()[0]
        )
        audit_id = _digest_id("DIA", delivery_intent_id, sequence, state, reason_code)
        self.connection.execute(
            """
            INSERT INTO delivery_intent_audit_events(
                delivery_audit_event_id, delivery_intent_id, event_sequence,
                state, reason_code, detail, recorded_at
            ) VALUES (?, ?, ?, ?, ?, NULL, strftime('%Y-%m-%dT%H:%M:%fZ','now'))
            """,
            (audit_id, delivery_intent_id, sequence, state, reason_code),
        )

    def dispatch(self, payload: DeliveryPayload) -> DeliveryDispatchResult:
        intent = self._intent_row(payload.delivery_intent_id)
        if intent is None:
            raise LookupError(f"unknown delivery_intent_id: {payload.delivery_intent_id}")
        if payload.as_transport_dict()["delivery_intent_id"] != intent[0]:
            raise ValueError("payload delivery intent identity mismatch")

        already_delivered, receipt_id = self._already_delivered(payload.delivery_intent_id)
        if already_delivered:
            return DeliveryDispatchResult(
                payload.delivery_intent_id,
                "DELIVERED",
                0,
                (),
                receipt_id,
            )

        if self._current_state(payload.delivery_intent_id) != "READY":
            raise ValueError("delivery intent must be READY before dispatch")

        attempts_made = 0
        for attempt_sequence in range(1, self.max_attempts + 1):
            attempts_made += 1
            self._append_audit(payload.delivery_intent_id, "ATTEMPTED", "TRANSPORT_ATTEMPTED")
            result = self.transport.send(
                payload.as_transport_dict(),
                idempotency_key=str(intent[1]),
                attempt_sequence=attempt_sequence,
            )
            state = "DELIVERED" if result.success else "FAILED"
            attempt_id = _digest_id(
                "DTA", payload.delivery_intent_id, attempt_sequence, self.transport.name
            )
            self.connection.execute(
                """
                INSERT INTO delivery_transport_attempts(
                    transport_attempt_id, delivery_intent_id, attempt_sequence,
                    transport_name, state, error_code, error_detail, attempted_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, strftime('%Y-%m-%dT%H:%M:%fZ','now'))
                """,
                (
                    attempt_id,
                    payload.delivery_intent_id,
                    attempt_sequence,
                    self.transport.name,
                    state,
                    _clean_optional(result.error_code, limit=120),
                    _clean_optional(result.error_detail),
                ),
            )
            self._append_audit(
                payload.delivery_intent_id,
                state,
                "TRANSPORT_DELIVERED" if result.success else "TRANSPORT_FAILED",
            )
            if result.success:
                receipt_id = _digest_id("DR", attempt_id, result.receipt_type)
                self.connection.execute(
                    """
                    INSERT INTO delivery_receipts(
                        delivery_receipt_id, transport_attempt_id, receipt_type,
                        external_reference, recorded_at
                    ) VALUES (?, ?, ?, ?, strftime('%Y-%m-%dT%H:%M:%fZ','now'))
                    """,
                    (
                        receipt_id,
                        attempt_id,
                        _clean_optional(result.receipt_type, limit=120) or "LOCAL_TEST",
                        _clean_optional(result.external_reference, limit=500),
                    ),
                )
                return DeliveryDispatchResult(
                    payload.delivery_intent_id,
                    "DELIVERED",
                    attempts_made,
                    self.backoff_seconds[:attempts_made],
                    receipt_id,
                )

        return DeliveryDispatchResult(
            payload.delivery_intent_id,
            "FAILED",
            attempts_made,
            self.backoff_seconds,
            None,
        )
