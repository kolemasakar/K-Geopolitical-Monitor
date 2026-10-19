import hashlib
import sqlite3
from pathlib import Path

import pytest

from kgeopolitical_monitor.candidate_qualification_p244 import qualify
from kgeopolitical_monitor.database import initialize_database


def snapshot(tmp_path):
    migrations = tmp_path/'migrations'
    migrations.mkdir()
    for p in sorted((Path(__file__).resolve().parents[1]/'migrations').glob('*.sql'))[:21]:
        (migrations/p.name).write_bytes(p.read_bytes())
    db = tmp_path/'snapshot.db'
    initialize_database(str(db), migrations_dir=migrations)
    with sqlite3.connect(db) as conn:
        conn.execute("INSERT INTO monitoring_watches (watch_id,name,query,cadence_minutes,enabled,created_at) VALUES ('offline-watch','Offline fixture','test',1,1,'2026-01-01T00:00:00+00:00')")
    return db, hashlib.sha256(db.read_bytes()).hexdigest()


def test_real_candidate_flow_migrates_restores_and_denies_network(tmp_path):
    db, digest = snapshot(tmp_path)
    before = db.read_bytes()
    report = qualify(db, expected_sha256=digest)
    assert report['status'] == 'PASS_WITH_LIMITATIONS'
    assert (report['migrations_before'], report['migrations_after']) == (21, 32)
    assert report['existing_rows_preserved'] and report['migration_idempotent']
    assert report['offline_tick_executions'] == 1
    assert report['transport_attempts_denied'] > 0
    assert report['socket_attempts_denied'] == 0
    assert not report['observation_after']['admit_work']
    assert report['retention']['eligible'] == ['artifact-expired.json']
    assert report['retention_rehearsal']['restore'] == 'PASS'
    assert report['rollback'] == 'BYTE_EXACT_BASELINE_RESTORE'
    assert report['temporary_workspace_removed'] and not report['send']
    assert db.read_bytes() == before


def test_unknown_migration_fails_without_touching_snapshot(tmp_path):
    db, _ = snapshot(tmp_path)
    with sqlite3.connect(db) as conn:
        conn.execute("INSERT INTO schema_migrations(version) VALUES ('999_unknown.sql')")
    data = db.read_bytes()
    report = qualify(db, expected_sha256=hashlib.sha256(data).hexdigest())
    assert report['status'] == 'FAIL'
    assert db.read_bytes() == data


def test_hash_alias_and_size_guards(tmp_path):
    db, digest = snapshot(tmp_path)
    with pytest.raises(ValueError, match='hash'):
        qualify(db, expected_sha256='0'*64)
    alias = tmp_path/'alias'
    alias.symlink_to(db)
    with pytest.raises(OSError):
        qualify(alias, expected_sha256=digest)
    alias.unlink()
    alias.hardlink_to(db)
    with pytest.raises(ValueError, match='single-link'):
        qualify(db, expected_sha256=digest)


def test_timeout_reaps_child_and_preserves_snapshot(tmp_path):
    db, digest = snapshot(tmp_path)
    report = qualify(db, expected_sha256=digest, timeout_seconds=0.001)
    assert report == {'status':'FAIL','cause':'TIMEOUT','child_reaped':True,'send':False}
    assert hashlib.sha256(db.read_bytes()).hexdigest() == digest


def test_due_queue_limit_blocks_tick_before_network(tmp_path):
    db, _ = snapshot(tmp_path)
    with sqlite3.connect(db) as conn:
        for i in range(100):
            conn.execute("INSERT INTO monitoring_watches (watch_id,name,query,cadence_minutes,enabled,created_at) VALUES (?,?,?,1,1,'2026-01-01T00:00:00+00:00')", (f'watch-{i}', 'Bounded fixture', 'test'))
    data = db.read_bytes()
    report = qualify(db, expected_sha256=hashlib.sha256(data).hexdigest())
    assert report['status'] == 'FAIL'
    assert db.read_bytes() == data


def test_corrupt_and_oversized_snapshot_fail_closed(tmp_path):
    db = tmp_path/'bad.db'
    db.write_bytes(b'not sqlite')
    report = qualify(db, expected_sha256=hashlib.sha256(db.read_bytes()).hexdigest())
    assert report['status'] == 'FAIL'
    db.write_bytes(b'x'*(8*1024*1024+1))
    with pytest.raises(ValueError, match='bounded'):
        qualify(db, expected_sha256=hashlib.sha256(db.read_bytes()).hexdigest())
