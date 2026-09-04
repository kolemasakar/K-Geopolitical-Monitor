from __future__ import annotations

from pathlib import Path
import sqlite3

from kgeopolitical_monitor.database import initialize_database
from kgeopolitical_monitor.delivery_intent_persistence import SQLiteDeliveryIntentRepository
from kgeopolitical_monitor.delivery_policy import SQLiteDeliveryPolicyProjector
from kgeopolitical_monitor.delivery_transport import InMemoryDeliverySink, SQLiteDeliveryDispatcher
from kgeopolitical_monitor.owner_delivery_experience import (
    P16_4_GATE,
    SQLiteOwnerDeliveryExperienceProjection,
)


ROOT = Path(__file__).resolve().parents[1]


def _connection(tmp_path):
    path = tmp_path / "kgm.db"
    initialize_database(str(path))
    return sqlite3.connect(path)


def _report(connection, report_id="REPORT-P16-4"):
    connection.execute(
        """
        INSERT INTO report_snapshots(
            report_id, report_type, scope_key, subject_ref_type, subject_ref_id,
            title, summary, as_of, created_at, generator_version
        ) VALUES (?, 'GLOBAL_GEOPOLITICAL_BRIEF', 'GLOBAL', NULL, NULL,
                  'Owner projection', 'Read-only projection fixture',
                  '2026-09-04T00:00:00+00:00', '2026-09-04T00:00:00+00:00', 'test')
        """,
        (report_id,),
    )
    intent = SQLiteDeliveryIntentRepository(connection).create_intent(
        canonical_object_type="REPORT",
        canonical_object_id=report_id,
        event_type="INITIAL",
    )
    projector = SQLiteDeliveryPolicyProjector(connection)
    decision = projector.evaluate(intent.delivery_intent_id)
    projector.apply(decision)
    assert decision.payload is not None
    return intent, decision.payload


def test_p16_4_gate_is_exact():
    assert P16_4_GATE == "P16_4_OWNER_OPERATOR_EXPERIENCE_PROJECTION_VALIDATED"


def test_empty_owner_projection_is_deterministic(tmp_path):
    connection = _connection(tmp_path)
    try:
        assert SQLiteOwnerDeliveryExperienceProjection(connection).list_rows() == ()
    finally:
        connection.close()


def test_owner_projection_explains_delivered_status_receipt_and_attempts(tmp_path):
    connection = _connection(tmp_path)
    try:
        intent, payload = _report(connection)
        SQLiteDeliveryDispatcher(connection, InMemoryDeliverySink([True])).dispatch(payload)
        before_changes = connection.total_changes
        rows = SQLiteOwnerDeliveryExperienceProjection(connection).list_rows()
        after_changes = connection.total_changes
        assert before_changes == after_changes
        assert len(rows) == 1
        row = rows[0]
        assert row.delivery_intent_id == intent.delivery_intent_id
        assert row.current_state == "DELIVERED"
        assert row.latest_reason_code == "TRANSPORT_DELIVERED"
        assert row.attempt_count == 1
        assert row.latest_transport_name == "IN_MEMORY_TEST"
        assert row.latest_transport_state == "DELIVERED"
        assert row.receipt_type == "LOCAL_TEST"
        assert row.receipt_reference is not None
        assert row.payload_redaction_required is True
        assert row.payload_persisted is False
        assert "DELIVERY_STATE_NOT_FACTUAL_VERIFICATION" in row.limitations
    finally:
        connection.close()


def test_owner_projection_surfaces_failure_reason_without_mutating_state(tmp_path):
    connection = _connection(tmp_path)
    try:
        _, payload = _report(connection)
        SQLiteDeliveryDispatcher(connection, InMemoryDeliverySink([False]), max_attempts=1).dispatch(payload)
        before = connection.execute(
            "SELECT title, summary FROM report_snapshots WHERE report_id = 'REPORT-P16-4'"
        ).fetchone()
        row = SQLiteOwnerDeliveryExperienceProjection(connection).list_rows()[0]
        after = connection.execute(
            "SELECT title, summary FROM report_snapshots WHERE report_id = 'REPORT-P16-4'"
        ).fetchone()
        assert before == after
        assert row.current_state == "FAILED"
        assert row.latest_reason_code == "TRANSPORT_FAILED"
        assert row.latest_error_code == "DETERMINISTIC_TEST_FAILURE"
        assert row.attempt_count == 1
    finally:
        connection.close()


def test_feedback_action_is_unavailable_before_p16_5_schema(tmp_path):
    connection = _connection(tmp_path)
    try:
        _, payload = _report(connection)
        SQLiteDeliveryDispatcher(connection, InMemoryDeliverySink([True])).dispatch(payload)
        row = SQLiteOwnerDeliveryExperienceProjection(connection).list_rows()[0]
        assert row.feedback_action_available is False
    finally:
        connection.close()


def test_p16_4_projection_is_not_added_to_public_backend_routes():
    backend = (ROOT / "src" / "kgeopolitical_monitor" / "backend_action_api.py").read_text(
        encoding="utf-8"
    )
    assert "owner_delivery_experience" not in backend
    assert "SQLiteOwnerDeliveryExperienceProjection" not in backend
