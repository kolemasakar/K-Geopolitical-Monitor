import errno
import fcntl
import hashlib
import json
import os
import pytest
from kgeopolitical_monitor import bounded_recovery_p242 as recovery
from kgeopolitical_monitor import ledger_migration_rehearsal_p242 as migration
from kgeopolitical_monitor import exchange_ledger_atomic_v1 as atomic
from kgeopolitical_monitor.exchange_generation_v1 import publish_generation
from test_exchange_contract_v1 import base

NOW = "2026-10-16T10:45:00Z"


def invoke(root, **kw):
    return recovery.run(root, allowed_consumers={"ktrader": "review-v1"},
                        observed_at_utc=NOW, **kw)


def test_bounded_retries_and_exhaustion(tmp_path, monkeypatch):
    calls = []
    def fail(*a, **kw):
        calls.append(1)
        raise OSError(errno.EIO, "injected")
    monkeypatch.setattr(recovery, "recover_durable", fail)
    assert invoke(tmp_path)["status"] == "IO_FAILURE"
    assert len(calls) == 3


def test_policy_error_is_not_retried(tmp_path, monkeypatch):
    def fail(*a, **kw):
        raise PermissionError("denied")
    # PermissionError is OSError: must not retry identity/policy denials.
    monkeypatch.setattr(recovery, "recover_durable", fail)
    with pytest.raises(PermissionError):
        invoke(tmp_path)


def test_deadline_stops_before_work(tmp_path, monkeypatch):
    ticks = iter([0, 11])
    monkeypatch.setattr(recovery, "recover_durable", lambda *a, **k: pytest.fail("called"))
    assert invoke(tmp_path, clock=lambda: next(ticks))["status"] == "DEADLINE"


def test_overlap_is_denied(tmp_path):
    fd = os.open(tmp_path / ".p242-invocation.lock", os.O_CREAT | os.O_RDWR, 0o600)
    try:
        fcntl.flock(fd, fcntl.LOCK_EX)
        assert invoke(tmp_path)["status"] == "BUSY"
    finally:
        os.close(fd)


def test_empty_recovery_no_send(tmp_path):
    result = invoke(tmp_path)
    assert result["status"] == "COMPLETE" and result["send"] is False


def test_report_errors_fail_closed(tmp_path, monkeypatch):
    monkeypatch.setattr(recovery, "recover_durable", lambda *a, **k: {"errors": ["synthetic"]})
    assert invoke(tmp_path)["status"] == "FAIL_CLOSED"


@pytest.mark.parametrize("args", [{"attempts": 0}, {"attempts": 4},
    {"budget_seconds": float("nan")}, {"budget_seconds": True}, {"max_items": 0}])
def test_invalid_bounds(tmp_path, args):
    with pytest.raises(ValueError):
        invoke(tmp_path, **args)


def snapshot(tmp_path, raw=None):
    path = tmp_path / "source.jsonl"
    if raw is None:
        raw = (json.dumps({"sequence": 1, "batch_id": "batch1", "sha256": "a"*64})+"\n").encode()
    path.write_bytes(raw)
    work = tmp_path / "work"
    work.mkdir(mode=0o700)
    return path, work, raw


def test_migration_and_rollback_source_unchanged(tmp_path):
    path, work, raw = snapshot(tmp_path)
    result = migration.rehearse(path, work)
    assert result == {"records": 1, "sha256": hashlib.sha256(raw).hexdigest(),
                      "rollback": "PASS", "source_unchanged": True, "send": False}
    assert path.read_bytes() == raw and list(work.iterdir()) == []


@pytest.mark.parametrize("raw", [b'{"sequence":1', b'{}\n',
    b'{"sequence":1,"batch_id":"x","sha256":"z"}\n'])
def test_migration_bad_input_preserves_source(tmp_path, raw):
    path, work, original = snapshot(tmp_path, raw)
    with pytest.raises(ValueError):
        migration.rehearse(path, work)
    assert path.read_bytes() == original


def test_migration_denies_alias(tmp_path):
    path, work, raw = snapshot(tmp_path)
    alias = tmp_path / "alias"
    alias.symlink_to(path)
    with pytest.raises(OSError):
        migration.rehearse(alias, work)
    assert path.read_bytes() == raw


def test_existing_workspace_not_overwritten(tmp_path):
    path, work, raw = snapshot(tmp_path)
    (work / "keep").write_text("keep")
    with pytest.raises(ValueError):
        migration.rehearse(path, work)
    assert (work / "keep").read_text() == "keep"


@pytest.mark.parametrize("error", [errno.EIO, errno.ENOSPC])
def test_migration_io_failure_preserves_source(tmp_path, monkeypatch, error):
    path, work, raw = snapshot(tmp_path)
    def fail(*a):
        raise OSError(error, "injected")
    monkeypatch.setattr(migration.os, "fsync", fail)
    with pytest.raises(OSError):
        migration.rehearse(path, work)
    assert path.read_bytes() == raw and list(work.iterdir()) == []


@pytest.mark.parametrize("boundary", ["file", "directory"])
@pytest.mark.parametrize("error", [errno.EIO, errno.ENOSPC])
def test_atomic_storage_failure_and_reconcile(tmp_path, monkeypatch, boundary, error):
    publish_generation(base(), tmp_path)
    first = atomic.append(tmp_path, "batch1")
    batch = base()
    batch["batch_id"] = "batch2"
    publish_generation(batch, tmp_path)
    original = atomic.os.fsync
    def fail(fd):
        import stat
        is_dir = stat.S_ISDIR(os.fstat(fd).st_mode)
        if is_dir == (boundary == "directory"):
            raise OSError(error, "injected")
        return original(fd)
    with monkeypatch.context() as patch:
        patch.setattr(atomic.os, "fsync", fail)
        with pytest.raises(OSError):
            atomic.append(tmp_path, "batch2")
    rows = atomic.replay(tmp_path, 0)
    assert rows[0] == first
    assert len(rows) == (1 if boundary == "file" else 2)
    atomic.append(tmp_path, "batch2")
    assert [x["sequence"] for x in atomic.replay(tmp_path, 0)] == [1, 2]


@pytest.mark.parametrize("boundary", ["replace", "directory"])
def test_interrupted_migration_cleanup(tmp_path, monkeypatch, boundary):
    path, work, raw = snapshot(tmp_path)
    def stop(*a):
        raise OSError(errno.EIO, "interrupted")
    monkeypatch.setattr(migration.os if boundary == "replace" else migration.atomic,
                        "replace" if boundary == "replace" else "_sync_directory", stop)
    with pytest.raises(OSError):
        migration.rehearse(path, work)
    assert path.read_bytes() == raw and list(work.iterdir()) == []


def test_rehearsal_process_kill_and_restart(tmp_path):
    import subprocess
    import sys
    path, work, raw = snapshot(tmp_path)
    script = """
import os,signal,sys
from kgeopolitical_monitor import ledger_migration_rehearsal_p242 as m
def kill(*a):
    os.kill(os.getpid(), signal.SIGKILL)
m.atomic._sync_directory=kill
m.rehearse(sys.argv[1],sys.argv[2])
"""
    result = subprocess.run([sys.executable, "-c", script, str(path), str(work)], timeout=10)
    assert result.returncode == -9 and path.read_bytes() == raw
    # An abandoned workspace is rejected, never silently reused or deleted.
    with pytest.raises(ValueError):
        migration.rehearse(path, work)
    fresh = tmp_path / "fresh"
    fresh.mkdir(mode=0o700)
    assert migration.rehearse(path, fresh)["rollback"] == "PASS"


def test_rollback_uses_legacy_reader_and_canonical_namespace(tmp_path, monkeypatch):
    path, work, raw = snapshot(tmp_path)
    reader = migration.replay_published
    checked = []
    def inspect(root, cursor):
        assert (root / "ledger.jsonl").read_bytes() == raw
        assert not (root / "ledger-v2.jsonl").exists()
        checked.append(True)
        return reader(root, cursor)
    monkeypatch.setattr(migration, "replay_published", inspect)
    assert migration.rehearse(path, work)["rollback"] == "PASS"
    assert checked == [True]
