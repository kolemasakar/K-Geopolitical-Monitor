from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import sqlite3

import pytest

from kgeopolitical_monitor.database import initialize_database
from kgeopolitical_monitor.delivery_intent_persistence import SQLiteDeliveryIntentRepository
from kgeopolitical_monitor.delivery_policy import SQLiteDeliveryPolicyProjector
from kgeopolitical_monitor.delivery_transport import InMemoryDeliverySink, SQLiteDeliveryDispatcher
from kgeopolitical_monitor.operator_quality_feedback import (
    P16_5_GATE,
    SQLiteOperatorQualityFeedbackRepository,
)


ROOT = Path(__file__).resolve().parents[1]


def _connection(tmp_path):
    path = tmp_path / "kgm.db"
    initialize_database(str(path))
    return sqlite3.connect(path)


def _delivered_report(connection, report_id="REPORT-P16-5"):
    connection.execute(
        """
        INSERT INTO report_snapshots(
            report_id, report_type, scope_key, subject_ref_type, subject_ref_id,
            title, summary, as_of, created_at, generator_version
        ) VALUES (?, 'GLOBAL_GEOPOLITICAL_BRIEF', 'GLOBAL', NULL, NULL,
                  'Feedback fixture', 'Canonical report must remain unchanged',
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
    dispatch = SQLiteDeliveryDispatcher(connection, InMemoryDeliverySink([True])).dispatch(
        decision.payload
    )
    attempt_id = connection.execute(
        "SELECT transport_attempt_id FROM delivery_transport_attempts WHERE delivery_intent_id = ?",
        (intent.delivery_intent_id,),
    ).fetchone()[0]
    return intent, dispatch, attempt_id


def test_p16_5_gate_and_migration_are_exact(tmp_path):
    connection = _connection(tmp_path)
    try:
        assert P16_5_GATE == "P16_5_OPERATOR_QUALITY_FEEDBACK_PERSISTENCE_VALIDATED"
        applied = {row[0] for row in connection.execute("SELECT version FROM schema_migrations")}
        assert "032_operator_quality_feedback.sql" in applied
        columns = {
            row[1] for row in connection.execute("PRAGMA table_info(operator_quality_feedback)")
        }
        assert {
            "feedback_id",
            "delivery_intent_id",
            "reviewed_transport_attempt_id",
            "canonical_object_type",
            "canonical_object_id",
            "feedback_type",
            "note",
            "created_at",
        } <= columns
        assert {
            "verification_status",
            "factual_confidence",
            "independent_origin_count",
            "api_key",
            "token",
            "secret",
        }.isdisjoint(columns)
    finally:
        connection.close()


def test_feedback_references_exact_intent_attempt_and_canonical_object(tmp_path):
    connection = _connection(tmp_path)
    try:
        intent, _, attempt_id = _delivered_report(connection)
        repository = SQLiteOperatorQualityFeedbackRepository(connection)
        record = repository.record_feedback(
            delivery_intent_id=intent.delivery_intent_id,
            reviewed_transport_attempt_id=attempt_id,
            feedback_type="USEFUL",
            created_at=datetime(2026, 9, 4, 14, 0, tzinfo=timezone.utc),
        )
        assert record.canonical_object_type == "REPORT"
        assert record.canonical_object_id == "REPORT-P16-5"
        assert record.reviewed_transport_attempt_id == attempt_id
        assert repository.list_feedback(intent.delivery_intent_id) == (record,)
    finally:
        connection.close()


def test_feedback_rejects_attempt_from_another_delivery_intent(tmp_path):
    connection = _connection(tmp_path)
    try:
        first_intent, _, first_attempt = _delivered_report(connection, "REPORT-P16-5-A")
        second_intent, _, _ = _delivered_report(connection, "REPORT-P16-5-B")
        repository = SQLiteOperatorQualityFeedbackRepository(connection)
        with pytest.raises(LookupError, match="does not belong"):
            repository.record_feedback(
                delivery_intent_id=second_intent.delivery_intent_id,
                reviewed_transport_attempt_id=first_attempt,
                feedback_type="USEFUL",
            )
        assert repository.list_feedback(first_intent.delivery_intent_id) == ()
    finally:
        connection.close()


def test_free_text_feedback_is_bounded_and_redacts_secrets_and_local_paths(tmp_path):
    connection = _connection(tmp_path)
    try:
        intent, _, _ = _delivered_report(connection)
        record = SQLiteOperatorQualityFeedbackRepository(connection).record_feedback(
            delivery_intent_id=intent.delivery_intent_id,
            feedback_type="NOTE",
            note="token=abc123 database=/opt/k-geopolitical-monitor/data/private.db " + "x" * 1200,
        )
        assert record.note is not None
        assert "abc123" not in record.note
        assert "/opt/k-geopolitical-monitor" not in record.note
        assert len(record.note) <= 1000
    finally:
        connection.close()


def test_factual_correction_request_is_feedback_only_and_cannot_rewrite_truth(tmp_path):
    connection = _connection(tmp_path)
    try:
        intent, _, attempt_id = _delivered_report(connection)
        before = connection.execute(
            "SELECT title, summary FROM report_snapshots WHERE report_id = 'REPORT-P16-5'"
        ).fetchone()
        repository = SQLiteOperatorQualityFeedbackRepository(connection)
        record = repository.record_feedback(
            delivery_intent_id=intent.delivery_intent_id,
            reviewed_transport_attempt_id=attempt_id,
            feedback_type="FACTUAL_CORRECTION_REQUESTED",
            note="Operator requests provenance review; this is not truth evidence.",
        )
        after = connection.execute(
            "SELECT title, summary FROM report_snapshots WHERE report_id = 'REPORT-P16-5'"
        ).fetchone()
        assert before == after
        assert record.feedback_type == "FACTUAL_CORRECTION_REQUESTED"
        assert connection.execute("SELECT COUNT(*) FROM semantic_verification_decision_versions").fetchone()[0] == 0
    finally:
        connection.close()


def test_feedback_history_is_append_only(tmp_path):
    connection = _connection(tmp_path)
    try:
        intent, _, _ = _delivered_report(connection)
        record = SQLiteOperatorQualityFeedbackRepository(connection).record_feedback(
            delivery_intent_id=intent.delivery_intent_id,
            feedback_type="TIMELY",
        )
        with pytest.raises(sqlite3.IntegrityError, match="append-only"):
            connection.execute(
                "UPDATE operator_quality_feedback SET feedback_type='LATE' WHERE feedback_id = ?",
                (record.feedback_id,),
            )
        with pytest.raises(sqlite3.IntegrityError, match="append-only"):
            connection.execute(
                "DELETE FROM operator_quality_feedback WHERE feedback_id = ?",
                (record.feedback_id,),
            )
    finally:
        connection.close()


def test_feedback_mutation_is_not_exposed_through_public_backend():
    backend = (ROOT / "src" / "kgeopolitical_monitor" / "backend_action_api.py").read_text(
        encoding="utf-8"
    )
    assert "operator_quality_feedback" not in backend
    assert "SQLiteOperatorQualityFeedbackRepository" not in backend
