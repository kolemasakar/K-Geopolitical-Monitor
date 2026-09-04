from __future__ import annotations

import sqlite3

import pytest

from kgeopolitical_monitor.database import initialize_database
from kgeopolitical_monitor.delivery_intent_persistence import SQLiteDeliveryIntentRepository
from kgeopolitical_monitor.delivery_policy import SQLiteDeliveryPolicyProjector
from kgeopolitical_monitor.delivery_transport import (
    P16_3_GATE,
    InMemoryDeliverySink,
    SQLiteDeliveryDispatcher,
    TransportSendResult,
)


def _connection(tmp_path):
    path = tmp_path / "kgm.db"
    initialize_database(str(path))
    return sqlite3.connect(path)


def _ready_report(connection, report_id="REPORT-P16-3"):
    connection.execute(
        """
        INSERT INTO report_snapshots(
            report_id, report_type, scope_key, subject_ref_type, subject_ref_id,
            title, summary, as_of, created_at, generator_version
        ) VALUES (?, 'GLOBAL_GEOPOLITICAL_BRIEF', 'GLOBAL', NULL, NULL,
                  'Transport test', 'Canonical report remains immutable by transport',
                  '2026-09-04T00:00:00+00:00', '2026-09-04T00:00:00+00:00', 'test')
        """,
        (report_id,),
    )
    repository = SQLiteDeliveryIntentRepository(connection)
    intent = repository.create_intent(
        canonical_object_type="REPORT",
        canonical_object_id=report_id,
        event_type="INITIAL",
    )
    projector = SQLiteDeliveryPolicyProjector(connection)
    decision = projector.evaluate(intent.delivery_intent_id)
    assert decision.payload is not None
    projector.apply(decision)
    return intent, decision.payload


def test_p16_3_gate_is_exact():
    assert P16_3_GATE == "P16_3_PROVIDER_NEUTRAL_DELIVERY_TRANSPORT_VALIDATED"


def test_in_memory_transport_delivers_once_and_persists_receipt(tmp_path):
    connection = _connection(tmp_path)
    try:
        intent, payload = _ready_report(connection)
        sink = InMemoryDeliverySink([True])
        dispatcher = SQLiteDeliveryDispatcher(connection, sink)
        result = dispatcher.dispatch(payload)
        assert result.state == "DELIVERED"
        assert result.attempts_made == 1
        assert result.backoff_seconds == (0,)
        assert result.receipt_id is not None
        assert len(sink.sent) == 1
        attempt = connection.execute(
            "SELECT transport_name, state FROM delivery_transport_attempts WHERE delivery_intent_id = ?",
            (intent.delivery_intent_id,),
        ).fetchone()
        assert attempt == ("IN_MEMORY_TEST", "DELIVERED")
        assert connection.execute("SELECT COUNT(*) FROM delivery_receipts").fetchone()[0] == 1
    finally:
        connection.close()


def test_retry_is_bounded_deterministic_and_does_not_sleep(tmp_path):
    connection = _connection(tmp_path)
    try:
        _, payload = _ready_report(connection)
        sink = InMemoryDeliverySink([False, False, True])
        result = SQLiteDeliveryDispatcher(
            connection,
            sink,
            max_attempts=3,
            backoff_seconds=(0, 7, 21),
        ).dispatch(payload)
        assert result.state == "DELIVERED"
        assert result.attempts_made == 3
        assert result.backoff_seconds == (0, 7, 21)
        assert [entry["attempt_sequence"] for entry in sink.sent] == [1, 2, 3]
        states = [
            row[0]
            for row in connection.execute(
                "SELECT state FROM delivery_transport_attempts ORDER BY attempt_sequence"
            )
        ]
        assert states == ["FAILED", "FAILED", "DELIVERED"]
    finally:
        connection.close()


def test_provider_failure_is_isolated_from_canonical_report_state(tmp_path):
    connection = _connection(tmp_path)
    try:
        intent, payload = _ready_report(connection)
        before = connection.execute(
            "SELECT title, summary FROM report_snapshots WHERE report_id = 'REPORT-P16-3'"
        ).fetchone()
        sink = InMemoryDeliverySink([False, False])
        result = SQLiteDeliveryDispatcher(connection, sink, max_attempts=2).dispatch(payload)
        after = connection.execute(
            "SELECT title, summary FROM report_snapshots WHERE report_id = 'REPORT-P16-3'"
        ).fetchone()
        assert result.state == "FAILED"
        assert result.attempts_made == 2
        assert before == after
        assert connection.execute(
            "SELECT COUNT(*) FROM delivery_receipts"
        ).fetchone()[0] == 0
        assert connection.execute(
            "SELECT state FROM delivery_intent_audit_events WHERE delivery_intent_id = ? ORDER BY event_sequence DESC LIMIT 1",
            (intent.delivery_intent_id,),
        ).fetchone()[0] == "FAILED"
    finally:
        connection.close()


def test_persisted_delivery_idempotency_prevents_duplicate_send(tmp_path):
    connection = _connection(tmp_path)
    try:
        _, payload = _ready_report(connection)
        sink = InMemoryDeliverySink([True])
        dispatcher = SQLiteDeliveryDispatcher(connection, sink)
        first = dispatcher.dispatch(payload)
        second = dispatcher.dispatch(payload)
        assert first.state == second.state == "DELIVERED"
        assert first.attempts_made == 1
        assert second.attempts_made == 0
        assert len(sink.sent) == 1
        assert connection.execute(
            "SELECT COUNT(*) FROM delivery_transport_attempts"
        ).fetchone()[0] == 1
    finally:
        connection.close()


def test_transport_requires_ready_intent(tmp_path):
    connection = _connection(tmp_path)
    try:
        connection.execute(
            """
            INSERT INTO report_snapshots(
                report_id, report_type, scope_key, subject_ref_type, subject_ref_id,
                title, summary, as_of, created_at, generator_version
            ) VALUES ('REPORT-PENDING', 'GLOBAL_GEOPOLITICAL_BRIEF', 'GLOBAL', NULL, NULL,
                      'Pending', 'Pending', '2026-09-04T00:00:00+00:00',
                      '2026-09-04T00:00:00+00:00', 'test')
            """
        )
        repository = SQLiteDeliveryIntentRepository(connection)
        intent = repository.create_intent(
            canonical_object_type="REPORT",
            canonical_object_id="REPORT-PENDING",
            event_type="INITIAL",
        )
        decision = SQLiteDeliveryPolicyProjector(connection).evaluate(intent.delivery_intent_id)
        assert decision.payload is not None
        with pytest.raises(ValueError, match="must be READY"):
            SQLiteDeliveryDispatcher(connection, InMemoryDeliverySink()).dispatch(decision.payload)
    finally:
        connection.close()


def test_transport_records_error_evidence_without_credentials(tmp_path):
    connection = _connection(tmp_path)
    try:
        _, payload = _ready_report(connection)
        sink = InMemoryDeliverySink(
            [
                TransportSendResult(
                    success=False,
                    error_code="LOCAL_FAILURE",
                    error_detail="bounded provider-neutral failure detail",
                )
            ]
        )
        result = SQLiteDeliveryDispatcher(connection, sink, max_attempts=1).dispatch(payload)
        assert result.state == "FAILED"
        row = connection.execute(
            "SELECT transport_name, error_code, error_detail FROM delivery_transport_attempts"
        ).fetchone()
        assert row == (
            "IN_MEMORY_TEST",
            "LOCAL_FAILURE",
            "bounded provider-neutral failure detail",
        )
        columns = {
            item[1]
            for item in connection.execute("PRAGMA table_info(delivery_transport_attempts)")
        }
        assert {"password", "api_key", "token", "secret", "credential"}.isdisjoint(columns)
    finally:
        connection.close()
