from __future__ import annotations

from datetime import datetime, timezone
import sqlite3

from kgeopolitical_monitor.database import initialize_database
from kgeopolitical_monitor.delivery_intent_persistence import SQLiteDeliveryIntentRepository
from kgeopolitical_monitor.delivery_policy import SQLiteDeliveryPolicyProjector
from kgeopolitical_monitor.delivery_transport import InMemoryDeliverySink, SQLiteDeliveryDispatcher
from kgeopolitical_monitor.operator_quality_feedback import SQLiteOperatorQualityFeedbackRepository
from kgeopolitical_monitor.quality_feedback_metrics import (
    P16_6_GATE,
    SQLiteAdvisoryQualityMetrics,
)


def _connection(tmp_path):
    path = tmp_path / "kgm.db"
    initialize_database(str(path))
    return sqlite3.connect(path)


def _report(connection, report_id: str, created_at: datetime):
    timestamp = created_at.astimezone(timezone.utc).isoformat()
    connection.execute(
        """
        INSERT INTO report_snapshots(
            report_id, report_type, scope_key, subject_ref_type, subject_ref_id,
            title, summary, as_of, created_at, generator_version
        ) VALUES (?, 'GLOBAL_GEOPOLITICAL_BRIEF', 'GLOBAL', NULL, NULL,
                  'Quality metrics fixture', 'Persisted evidence only', ?, ?, 'test')
        """,
        (report_id, timestamp, timestamp),
    )
    intent = SQLiteDeliveryIntentRepository(connection).create_intent(
        canonical_object_type="REPORT",
        canonical_object_id=report_id,
        event_type="INITIAL",
        created_at=created_at,
    )
    projector = SQLiteDeliveryPolicyProjector(connection)
    decision = projector.evaluate(intent.delivery_intent_id)
    projector.apply(decision)
    assert decision.payload is not None
    return intent, decision.payload


def test_p16_6_gate_is_exact():
    assert P16_6_GATE == "P16_6_ADVISORY_QUALITY_FEEDBACK_LOOP_VALIDATED"


def test_quality_snapshot_is_deterministic_and_exposes_denominators(tmp_path):
    connection = _connection(tmp_path)
    try:
        first, first_payload = _report(
            connection, "REPORT-P16-6-A", datetime(2026, 9, 4, 10, tzinfo=timezone.utc)
        )
        second, second_payload = _report(
            connection, "REPORT-P16-6-B", datetime(2026, 9, 5, 10, tzinfo=timezone.utc)
        )
        SQLiteDeliveryDispatcher(connection, InMemoryDeliverySink([True])).dispatch(first_payload)
        SQLiteDeliveryDispatcher(
            connection,
            InMemoryDeliverySink([False, True]),
            max_attempts=2,
            backoff_seconds=(0, 5),
        ).dispatch(second_payload)

        feedback = SQLiteOperatorQualityFeedbackRepository(connection)
        feedback.record_feedback(delivery_intent_id=first.delivery_intent_id, feedback_type="USEFUL")
        feedback.record_feedback(delivery_intent_id=first.delivery_intent_id, feedback_type="TIMELY")
        feedback.record_feedback(
            delivery_intent_id=second.delivery_intent_id, feedback_type="DUPLICATE_NOISY"
        )
        feedback.record_feedback(
            delivery_intent_id=second.delivery_intent_id,
            feedback_type="FACTUAL_CORRECTION_REQUESTED",
        )

        before_changes = connection.total_changes
        snapshot = SQLiteAdvisoryQualityMetrics(connection).snapshot()
        assert connection.total_changes == before_changes

        assert snapshot.cohort_definition == "delivery_intents"
        assert snapshot.sample_size == 2
        assert snapshot.delivery_intent_count == 2
        assert snapshot.terminal_delivery_count == 2
        assert snapshot.delivered_count == 2
        assert snapshot.failed_count == 0
        assert snapshot.suppressed_count == 0
        assert snapshot.attempted_intent_count == 2
        assert snapshot.retry_intent_count == 1
        assert snapshot.transport_attempt_count == 3
        assert snapshot.receipt_count == 2
        assert snapshot.feedback_count == 4
        assert snapshot.useful_count == 1
        assert snapshot.timely_count == 1
        assert snapshot.duplicate_noisy_count == 1
        assert snapshot.correction_request_count == 1
        assert snapshot.delivery_success_rate == 1.0
        assert snapshot.delivery_failure_rate == 0.0
        assert snapshot.retry_rate == 0.5
        assert snapshot.usefulness_rate == 1.0
        assert snapshot.timeliness_rate == 1.0
        assert snapshot.noise_feedback_rate == 0.25
        assert snapshot.latest_state_distribution == (("DELIVERED", 2),)
        assert snapshot.event_type_distribution == (("INITIAL", 2),)
        assert "PROPOSAL_REVIEW_DUPLICATE_SUPPRESSION_POLICY" in snapshot.advisory_proposals
        assert "PROPOSAL_ROUTE_CORRECTION_REQUESTS_TO_PROVENANCE_REVIEW" in snapshot.advisory_proposals
        assert "NO_AUTOMATIC_POLICY_MUTATION" in snapshot.limitations
    finally:
        connection.close()


def test_quality_cohort_definition_includes_exact_bounds(tmp_path):
    connection = _connection(tmp_path)
    try:
        first, first_payload = _report(
            connection, "REPORT-P16-6-C", datetime(2026, 9, 4, 10, tzinfo=timezone.utc)
        )
        second, second_payload = _report(
            connection, "REPORT-P16-6-D", datetime(2026, 9, 5, 10, tzinfo=timezone.utc)
        )
        SQLiteDeliveryDispatcher(connection, InMemoryDeliverySink([True])).dispatch(first_payload)
        SQLiteDeliveryDispatcher(connection, InMemoryDeliverySink([True])).dispatch(second_payload)
        snapshot = SQLiteAdvisoryQualityMetrics(connection).snapshot(
            created_from="2026-09-05T00:00:00+00:00",
            created_before="2026-09-06T00:00:00+00:00",
        )
        assert snapshot.sample_size == 1
        assert snapshot.delivery_intent_count == 1
        assert "created_at>=2026-09-05T00:00:00+00:00" in snapshot.cohort_definition
        assert "created_at<2026-09-06T00:00:00+00:00" in snapshot.cohort_definition
    finally:
        connection.close()


def test_quality_metrics_cannot_mutate_truth_or_policy_tables(tmp_path):
    connection = _connection(tmp_path)
    try:
        _, payload = _report(
            connection, "REPORT-P16-6-E", datetime(2026, 9, 5, 12, tzinfo=timezone.utc)
        )
        SQLiteDeliveryDispatcher(connection, InMemoryDeliverySink([False]), max_attempts=1).dispatch(
            payload
        )
        truth_before = connection.execute(
            "SELECT COUNT(*) FROM semantic_verification_decision_versions"
        ).fetchone()[0]
        policy_before = connection.execute(
            "SELECT COUNT(*) FROM semantic_verification_policy_versions"
        ).fetchone()[0]
        source_before = connection.execute("SELECT COUNT(*) FROM source_reputation_history").fetchone()[0]
        report_before = connection.execute(
            "SELECT title, summary FROM report_snapshots WHERE report_id = 'REPORT-P16-6-E'"
        ).fetchone()
        before_changes = connection.total_changes

        snapshot = SQLiteAdvisoryQualityMetrics(connection).snapshot()

        assert connection.total_changes == before_changes
        assert connection.execute(
            "SELECT COUNT(*) FROM semantic_verification_decision_versions"
        ).fetchone()[0] == truth_before
        assert connection.execute(
            "SELECT COUNT(*) FROM semantic_verification_policy_versions"
        ).fetchone()[0] == policy_before
        assert connection.execute("SELECT COUNT(*) FROM source_reputation_history").fetchone()[0] == source_before
        assert connection.execute(
            "SELECT title, summary FROM report_snapshots WHERE report_id = 'REPORT-P16-6-E'"
        ).fetchone() == report_before
        assert snapshot.failed_count == 1
        assert snapshot.advisory_proposals == ("PROPOSAL_REVIEW_DELIVERY_FAILURE_EVIDENCE",)
    finally:
        connection.close()
