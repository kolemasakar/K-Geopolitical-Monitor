from __future__ import annotations

from datetime import datetime, timezone
import sqlite3

import pytest

from kgeopolitical_monitor.database import initialize_database
from kgeopolitical_monitor.delivery_intent_persistence import (
    P16_1_GATE,
    SQLiteDeliveryIntentRepository,
    build_delivery_idempotency_key,
    build_delivery_intent_id,
)


def _connection(tmp_path):
    path = tmp_path / "kgm.db"
    initialize_database(str(path))
    connection = sqlite3.connect(path)
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def _insert_report(connection: sqlite3.Connection, report_id: str = "REPORT-P16-1") -> None:
    connection.execute(
        """
        INSERT INTO report_snapshots(
            report_id, report_type, scope_key, subject_ref_type, subject_ref_id,
            title, summary, as_of, created_at, generator_version
        ) VALUES (?, 'GLOBAL_GEOPOLITICAL_BRIEF', 'GLOBAL', NULL, NULL,
                  'P16 test report', 'Canonical report snapshot', ?, ?, 'test')
        """,
        (report_id, "2026-09-04T00:00:00+00:00", "2026-09-04T00:00:00+00:00"),
    )


def test_p16_1_gate_and_migration_are_explicit(tmp_path):
    connection = _connection(tmp_path)
    try:
        assert P16_1_GATE == "P16_1_DELIVERY_INTENT_AUDIT_PERSISTENCE_VALIDATED"
        migrations = {
            row[0] for row in connection.execute("SELECT version FROM schema_migrations")
        }
        assert "031_delivery_intent_audit.sql" in migrations
        tables = {
            row[0]
            for row in connection.execute(
                "SELECT name FROM sqlite_master WHERE type = 'table'"
            )
        }
        assert {
            "delivery_intents",
            "delivery_intent_audit_events",
            "delivery_transport_attempts",
            "delivery_receipts",
        } <= tables
    finally:
        connection.close()


def test_delivery_intent_identity_and_idempotency_are_deterministic(tmp_path):
    connection = _connection(tmp_path)
    try:
        _insert_report(connection)
        repository = SQLiteDeliveryIntentRepository(connection)
        fixed_time = datetime(2026, 9, 4, 12, 0, tzinfo=timezone.utc)
        first = repository.create_intent(
            canonical_object_type="REPORT",
            canonical_object_id="REPORT-P16-1",
            event_type="INITIAL",
            policy_key="OWNER_DEFAULT",
            created_at=fixed_time,
        )
        second = repository.create_intent(
            canonical_object_type="REPORT",
            canonical_object_id="REPORT-P16-1",
            event_type="INITIAL",
            policy_key="OWNER_DEFAULT",
            created_at=datetime(2026, 9, 4, 13, 0, tzinfo=timezone.utc),
        )
        expected_key = build_delivery_idempotency_key(
            "REPORT", "REPORT-P16-1", "INITIAL", policy_key="OWNER_DEFAULT"
        )
        assert first == second
        assert first.idempotency_key == expected_key
        assert first.delivery_intent_id == build_delivery_intent_id(expected_key)
        assert connection.execute("SELECT COUNT(*) FROM delivery_intents").fetchone()[0] == 1
        assert connection.execute(
            "SELECT COUNT(*) FROM delivery_intent_audit_events"
        ).fetchone()[0] == 1
    finally:
        connection.close()


def test_delivery_intent_requires_existing_canonical_reference(tmp_path):
    connection = _connection(tmp_path)
    try:
        repository = SQLiteDeliveryIntentRepository(connection)
        with pytest.raises(LookupError, match="canonical delivery reference does not exist"):
            repository.create_intent(
                canonical_object_type="REPORT",
                canonical_object_id="MISSING-REPORT",
                event_type="INITIAL",
            )
        assert connection.execute("SELECT COUNT(*) FROM delivery_intents").fetchone()[0] == 0
    finally:
        connection.close()


def test_p16_1_creation_records_pending_only_and_never_attempts_transport(tmp_path):
    connection = _connection(tmp_path)
    try:
        _insert_report(connection)
        repository = SQLiteDeliveryIntentRepository(connection)
        intent = repository.create_intent(
            canonical_object_type="REPORT",
            canonical_object_id="REPORT-P16-1",
            event_type="INITIAL",
        )
        events = repository.list_audit_events(intent.delivery_intent_id)
        assert [event.state for event in events] == ["PENDING"]
        assert connection.execute(
            "SELECT COUNT(*) FROM delivery_transport_attempts"
        ).fetchone()[0] == 0
        assert connection.execute("SELECT COUNT(*) FROM delivery_receipts").fetchone()[0] == 0
    finally:
        connection.close()


def test_p16_1_intent_state_history_is_append_only_and_transition_checked(tmp_path):
    connection = _connection(tmp_path)
    try:
        _insert_report(connection)
        repository = SQLiteDeliveryIntentRepository(connection)
        intent = repository.create_intent(
            canonical_object_type="REPORT",
            canonical_object_id="REPORT-P16-1",
            event_type="INITIAL",
        )
        repository.append_intent_state(
            intent.delivery_intent_id,
            state="SUPPRESSED",
            reason_code="QUIET_HOURS",
        )
        assert repository.current_state(intent.delivery_intent_id) == "SUPPRESSED"
        assert [event.state for event in repository.list_audit_events(intent.delivery_intent_id)] == [
            "PENDING",
            "SUPPRESSED",
        ]
        with pytest.raises(ValueError, match="invalid delivery intent transition"):
            repository.append_intent_state(intent.delivery_intent_id, state="READY")
        with pytest.raises(sqlite3.IntegrityError, match="append-only"):
            connection.execute(
                "UPDATE delivery_intents SET policy_key = 'CHANGED' WHERE delivery_intent_id = ?",
                (intent.delivery_intent_id,),
            )
    finally:
        connection.close()


def test_delivery_state_cannot_mutate_canonical_report(tmp_path):
    connection = _connection(tmp_path)
    try:
        _insert_report(connection)
        before = connection.execute(
            "SELECT title, summary, as_of FROM report_snapshots WHERE report_id = 'REPORT-P16-1'"
        ).fetchone()
        repository = SQLiteDeliveryIntentRepository(connection)
        intent = repository.create_intent(
            canonical_object_type="REPORT",
            canonical_object_id="REPORT-P16-1",
            event_type="INITIAL",
        )
        repository.append_intent_state(intent.delivery_intent_id, state="READY")
        after = connection.execute(
            "SELECT title, summary, as_of FROM report_snapshots WHERE report_id = 'REPORT-P16-1'"
        ).fetchone()
        assert before == after
    finally:
        connection.close()


def test_p16_1_schema_contains_no_truth_promotion_or_secret_fields(tmp_path):
    connection = _connection(tmp_path)
    try:
        forbidden = {
            "verification_status",
            "verification_confidence",
            "factual_confidence",
            "independent_origin_count",
            "forecast_probability",
            "source_reputation",
            "password",
            "api_key",
            "token",
            "secret",
            "database_path",
        }
        for table in (
            "delivery_intents",
            "delivery_intent_audit_events",
            "delivery_transport_attempts",
            "delivery_receipts",
        ):
            columns = {row[1] for row in connection.execute(f"PRAGMA table_info({table})")}
            assert forbidden.isdisjoint(columns)
    finally:
        connection.close()
