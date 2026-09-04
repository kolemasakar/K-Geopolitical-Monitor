from __future__ import annotations

from datetime import datetime, timezone
import sqlite3

from kgeopolitical_monitor.database import initialize_database
from kgeopolitical_monitor.delivery_intent_persistence import SQLiteDeliveryIntentRepository
from kgeopolitical_monitor.delivery_policy import (
    P16_2_GATE,
    DeliveryPolicyConfig,
    QuietHours,
    SQLiteDeliveryPolicyProjector,
)


def _connection(tmp_path):
    path = tmp_path / "kgm.db"
    initialize_database(str(path))
    return sqlite3.connect(path)


def _insert_report(connection, report_id="REPORT-P16-2", *, summary="Canonical summary"):
    connection.execute(
        """
        INSERT INTO report_snapshots(
            report_id, report_type, scope_key, subject_ref_type, subject_ref_id,
            title, summary, as_of, created_at, generator_version
        ) VALUES (?, 'GLOBAL_GEOPOLITICAL_BRIEF', 'GLOBAL', NULL, NULL,
                  'Owner brief', ?, '2026-09-04T00:00:00+00:00',
                  '2026-09-04T00:00:00+00:00', 'test')
        """,
        (report_id, summary),
    )


def _report_intent(connection, report_id="REPORT-P16-2"):
    return SQLiteDeliveryIntentRepository(connection).create_intent(
        canonical_object_type="REPORT",
        canonical_object_id=report_id,
        event_type="INITIAL",
    )


def test_p16_2_gate_is_exact():
    assert P16_2_GATE == "P16_2_DELIVERY_POLICY_REDACTION_VALIDATED"


def test_policy_projects_only_allowlisted_minimized_payload_and_redacts_sensitive_text(tmp_path):
    connection = _connection(tmp_path)
    try:
        _insert_report(
            connection,
            summary="token=abc123 path=/opt/k-geopolitical-monitor/data/private.db retained context",
        )
        intent = _report_intent(connection)
        decision = SQLiteDeliveryPolicyProjector(connection).evaluate(
            intent.delivery_intent_id,
            evaluated_at=datetime(2026, 9, 4, 12, 0, tzinfo=timezone.utc),
        )
        assert decision.state == "READY"
        assert decision.payload is not None
        payload = decision.payload.as_transport_dict()
        assert set(payload) == {
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
        assert "abc123" not in str(payload)
        assert "/opt/k-geopolitical-monitor" not in str(payload)
        assert payload["redactions_applied"] is True
        assert "NOT_FACTUAL_VERIFICATION" in payload["limitations"]
    finally:
        connection.close()


def test_policy_fails_closed_for_stale_or_ambiguous_reference(tmp_path):
    connection = _connection(tmp_path)
    try:
        _insert_report(connection)
        intent = _report_intent(connection)
        projector = SQLiteDeliveryPolicyProjector(connection)
        stale = projector.evaluate(intent.delivery_intent_id, reference_stale=True)
        ambiguous = projector.evaluate(intent.delivery_intent_id, reference_ambiguous=True)
        assert stale.state == "SUPPRESSED" and stale.reason_code == "CANONICAL_REFERENCE_STALE"
        assert ambiguous.state == "SUPPRESSED" and ambiguous.reason_code == "CANONICAL_REFERENCE_AMBIGUOUS"
        assert stale.payload is None and ambiguous.payload is None
    finally:
        connection.close()


def test_quiet_hours_are_deterministic_and_do_not_attempt_transport(tmp_path):
    connection = _connection(tmp_path)
    try:
        _insert_report(connection)
        intent = _report_intent(connection)
        projector = SQLiteDeliveryPolicyProjector(
            connection,
            DeliveryPolicyConfig(quiet_hours=QuietHours(22, 7)),
        )
        decision = projector.evaluate(
            intent.delivery_intent_id,
            evaluated_at=datetime(2026, 9, 4, 23, 0, tzinfo=timezone.utc),
        )
        assert decision.state == "SUPPRESSED"
        assert decision.reason_code == "QUIET_HOURS"
        projector.apply(decision)
        assert connection.execute("SELECT COUNT(*) FROM delivery_transport_attempts").fetchone()[0] == 0
        assert SQLiteDeliveryIntentRepository(connection).current_state(intent.delivery_intent_id) == "SUPPRESSED"
    finally:
        connection.close()


def test_alert_priority_is_loaded_from_persisted_canonical_state(tmp_path):
    connection = _connection(tmp_path)
    try:
        connection.execute(
            """
            INSERT INTO operational_findings(
                finding_id, run_id, watch_id, title, summary, importance, confidence,
                evidence_refs, explanation, created_at
            ) VALUES ('F-P16-2', 'RUN-X', 'WATCH-X', 'Finding', 'Summary', 0.5, 0.5,
                      '[]', 'test', '2026-09-04T00:00:00+00:00')
            """
        )
        connection.execute(
            """
            INSERT INTO strategic_alerts(
                alert_id, watch_id, finding_id, trigger_type, dedup_key, priority,
                status, first_triggered_at, last_updated_at, evidence_refs, explanation
            ) VALUES ('A-P16-2', 'WATCH-X', 'F-P16-2', 'TEST', 'D', 'NORMAL', 'OPEN',
                      '2026-09-04T00:00:00+00:00', '2026-09-04T00:00:00+00:00', '[]', 'test')
            """
        )
        intent = SQLiteDeliveryIntentRepository(connection).create_intent(
            canonical_object_type="STRATEGIC_ALERT",
            canonical_object_id="A-P16-2",
            event_type="INITIAL",
        )
        decision = SQLiteDeliveryPolicyProjector(
            connection,
            DeliveryPolicyConfig(minimum_alert_priority="HIGH"),
        ).evaluate(intent.delivery_intent_id)
        assert decision.state == "SUPPRESSED"
        assert decision.reason_code == "PRIORITY_BELOW_POLICY"
    finally:
        connection.close()


def test_ready_policy_application_changes_delivery_state_only(tmp_path):
    connection = _connection(tmp_path)
    try:
        _insert_report(connection)
        before = connection.execute(
            "SELECT title, summary FROM report_snapshots WHERE report_id = 'REPORT-P16-2'"
        ).fetchone()
        intent = _report_intent(connection)
        projector = SQLiteDeliveryPolicyProjector(connection)
        decision = projector.evaluate(intent.delivery_intent_id)
        projector.apply(decision)
        after = connection.execute(
            "SELECT title, summary FROM report_snapshots WHERE report_id = 'REPORT-P16-2'"
        ).fetchone()
        assert before == after
        assert SQLiteDeliveryIntentRepository(connection).current_state(intent.delivery_intent_id) == "READY"
        assert connection.execute("SELECT COUNT(*) FROM delivery_transport_attempts").fetchone()[0] == 0
    finally:
        connection.close()
