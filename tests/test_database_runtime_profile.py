import threading
import time

from kgeopolitical_monitor.database import (
    RUNTIME_BUSY_TIMEOUT_MS,
    RUNTIME_ISOLATION_LEVEL,
    RUNTIME_JOURNAL_MODE,
    connect_runtime_database,
    initialize_database,
)


def test_runtime_connection_profile_is_explicit(tmp_path):
    database_path = tmp_path / "data" / "kgeopolitical_monitor.db"
    initialize_database(database_path)

    connection = connect_runtime_database(database_path)
    try:
        assert connection.isolation_level == RUNTIME_ISOLATION_LEVEL
        assert connection.execute("PRAGMA foreign_keys").fetchone()[0] == 1
        assert connection.execute("PRAGMA busy_timeout").fetchone()[0] == RUNTIME_BUSY_TIMEOUT_MS
        assert str(connection.execute("PRAGMA journal_mode").fetchone()[0]).lower() == (
            RUNTIME_JOURNAL_MODE
        )
        assert connection.execute("PRAGMA synchronous").fetchone()[0] == 2
    finally:
        connection.close()


def test_reader_can_observe_committed_state_while_writer_has_uncommitted_change(tmp_path):
    database_path = tmp_path / "data" / "kgeopolitical_monitor.db"
    initialize_database(database_path)

    writer = connect_runtime_database(database_path)
    try:
        writer.execute(
            "INSERT INTO metadata(key, value) VALUES (?, ?)",
            ("concurrency", "committed"),
        )
        writer.commit()
        writer.execute(
            "UPDATE metadata SET value = ? WHERE key = ?",
            ("uncommitted", "concurrency"),
        )

        reader = connect_runtime_database(database_path)
        try:
            value = reader.execute(
                "SELECT value FROM metadata WHERE key = ?",
                ("concurrency",),
            ).fetchone()[0]
        finally:
            reader.close()

        assert value == "committed"
    finally:
        writer.rollback()
        writer.close()


def test_second_writer_waits_within_busy_timeout_and_commits_after_release(tmp_path):
    database_path = tmp_path / "data" / "kgeopolitical_monitor.db"
    initialize_database(database_path)

    first_writer = connect_runtime_database(database_path)
    first_writer.execute(
        "INSERT INTO metadata(key, value) VALUES (?, ?)",
        ("first_writer", "holding"),
    )

    outcome: dict[str, object] = {}

    def write_after_lock() -> None:
        second_writer = connect_runtime_database(database_path)
        try:
            started = time.monotonic()
            second_writer.execute(
                "INSERT INTO metadata(key, value) VALUES (?, ?)",
                ("second_writer", "completed"),
            )
            second_writer.commit()
            outcome["elapsed"] = time.monotonic() - started
        except BaseException as exc:  # pragma: no cover - asserted below.
            outcome["error"] = exc
        finally:
            second_writer.close()

    thread = threading.Thread(target=write_after_lock)
    thread.start()
    time.sleep(0.1)
    first_writer.commit()
    first_writer.close()
    thread.join(timeout=2.0)

    assert not thread.is_alive()
    assert "error" not in outcome
    assert float(outcome["elapsed"]) >= 0.05

    verifier = connect_runtime_database(database_path)
    try:
        assert verifier.execute(
            "SELECT value FROM metadata WHERE key = ?",
            ("second_writer",),
        ).fetchone()[0] == "completed"
    finally:
        verifier.close()


def test_runtime_database_reopens_with_integrity_after_committed_write(tmp_path):
    database_path = tmp_path / "data" / "kgeopolitical_monitor.db"
    initialize_database(database_path)

    connection = connect_runtime_database(database_path)
    connection.execute(
        "INSERT INTO metadata(key, value) VALUES (?, ?)",
        ("reopen", "preserved"),
    )
    connection.commit()
    connection.close()

    reopened = connect_runtime_database(database_path)
    try:
        assert reopened.execute("PRAGMA integrity_check").fetchone()[0] == "ok"
        assert reopened.execute(
            "SELECT value FROM metadata WHERE key = ?",
            ("reopen",),
        ).fetchone()[0] == "preserved"
    finally:
        reopened.close()
