"""Explicit offline candidate qualification; all mutations use an owned temporary copy.

This is a trusted-code isolation harness, not a sandbox for hostile candidate code.
Never accepts a production destination. Output contains aggregates, not DB contents.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import re
import resource
import shutil
import sqlite3
import stat
import subprocess
import sys
import tempfile
import time

MAX_SNAPSHOT = 8 * 1024 * 1024
LIMITS = {"address_space": 256*1024*1024, "file_bytes": 16*1024*1024,
          "descriptors": 64, "cpu_seconds": 30}


def _digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _check(connection):
    if connection.execute("PRAGMA integrity_check").fetchall() != [("ok",)]:
        raise ValueError("integrity check failed")
    if connection.execute("PRAGMA foreign_key_check").fetchone() is not None:
        raise ValueError("foreign key check failed")


def _inventory(connection):
    # Hash rows in SQLite storage order; no values leave the child. Compare only
    # the unchanged pre-migration tables at migration time, before runtime writes.
    result = {}
    tables = connection.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    for (name,) in tables.fetchall():
        quoted = '"' + name.replace('"', '""') + '"'
        rows = connection.execute("SELECT * FROM " + quoted).fetchall()
        result[name] = (len(rows), hashlib.sha256(repr(rows).encode()).hexdigest())
    return result


class DeniedTransport:
    def __init__(self):
        self.attempts = 0

    def get(self, url, *, headers=None):
        self.attempts += 1
        raise RuntimeError("OFFLINE_NETWORK_DENIED")


def _run_copy(root):
    """Child entry; root is created privately by qualify(), never user-selected."""
    for key, value in [(resource.RLIMIT_AS, LIMITS["address_space"]),
                       (resource.RLIMIT_FSIZE, LIMITS["file_bytes"]),
                       (resource.RLIMIT_NOFILE, LIMITS["descriptors"]),
                       (resource.RLIMIT_CPU, LIMITS["cpu_seconds"])]:
        resource.setrlimit(key, (value, value))
    # Defense in depth: fail before socket creation, DNS, or connect. Transport
    # injection is the primary offline boundary for the actual monitoring stack.
    socket_attempts = [0]
    def audit(event, args):
        if event.startswith("socket."):
            socket_attempts[0] += 1
            raise RuntimeError("OFFLINE_SOCKET_DENIED")
    sys.addaudithook(audit)
    from .database import initialize_database
    from .unattended_runner import build_unattended_service
    from .resource_observation_p243 import observe
    from .retention_plan_p243 import plan
    from .retention_rehearsal_p243 import rehearse, TTL

    root = Path(root)
    db = root / "data" / "kgeopolitical_monitor.db"
    db.parent.mkdir()
    shutil.copyfile(root / "baseline.db", db)
    with sqlite3.connect(db) as conn:
        _check(conn)
        before = _inventory(conn)
        old_versions = [r[0] for r in conn.execute("SELECT version FROM schema_migrations ORDER BY version")]
    expected = sorted(p.name for p in (Path(__file__).resolve().parents[2]/"migrations").glob("*.sql"))
    if not set(old_versions) <= set(expected):
        raise ValueError("unknown snapshot migration")
    initialize_database(str(db))
    with sqlite3.connect(db) as conn:
        _check(conn)
        migrated = _inventory(conn)
        versions = [r[0] for r in conn.execute("SELECT version FROM schema_migrations ORDER BY version")]
        if versions != expected:
            raise ValueError("candidate migration set mismatch")
        if any(migrated.get(t) != v for t, v in before.items() if t != "schema_migrations"):
            raise ValueError("migration changed existing rows")
    initialize_database(str(db))
    with sqlite3.connect(db) as conn:
        if _inventory(conn) != migrated:
            raise ValueError("migration is not idempotent")

    transport = DeniedTransport()
    service = build_unattended_service(root, transport=transport)
    due = service.runtime.due_watches()
    # Queue means due watches; bytes measure their serialized metadata in this
    # candidate process. This is not a production queue measurement.
    def observation(sources):
        return observe(queue_depth=len(due), queue_bytes=sum(len(json.dumps(vars(w), default=str).encode()) for w in due),
                       disk_free_bytes=shutil.disk_usage(root).free,
                       rss_bytes=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024,
                       retries=0, sources=sources)
    pre = observation(["UNKNOWN"])
    # UNKNOWN prevents live admission; allow only this explicitly offline tick
    # when hard resource gates pass. It cannot admit network work.
    if pre["status"] == "BLOCKED":
        raise ValueError("resource admission blocked")
    tick = service.run_once()
    statuses = ["UNAVAILABLE" if e.status == "FAILED" else "UNKNOWN" for e in tick.executions]
    post = observation(statuses)
    if post["status"] == "BLOCKED":
        raise ValueError("post-tick resource limit exceeded")
    with sqlite3.connect(db) as conn:
        _check(conn)
    artifacts = root / "artifacts"
    artifacts.mkdir()
    payload = json.dumps({"execution_count": len(tick.executions),
                          "recovered_runs": tick.recovered_runs, "send": False}).encode()
    now = time.time()
    for name in ["artifact-expired.json", "artifact-current.json"]:
        (artifacts/name).write_bytes(payload)
    os.utime(artifacts/"artifact-expired.json", (now-TTL["artifact"]-1,)*2)
    retention = plan(artifacts, now=now, min_age_seconds=TTL["artifact"], keep_last=1)
    rehearsal = rehearse([
        {"id":"expired", "kind":"artifact", "created":now-TTL["artifact"]-1, "payload":payload},
        {"id":"current", "kind":"artifact", "created":now, "payload":payload},
    ], now=now, protected_ids=["current"])
    if retention["eligible"] != ["artifact-expired.json"] or rehearsal["deleted_in_disposable_copy"] != ["expired"]:
        raise ValueError("retention integration failed")
    # Roll back the entire private database from the original baseline; no
    # downgrade SQL or claim of rollback after real external side effects.
    db.unlink()
    shutil.copyfile(root/"baseline.db", db)
    with sqlite3.connect(db) as conn:
        _check(conn)
        if _inventory(conn) != before:
            raise ValueError("rollback mismatch")
    if _digest(db) != _digest(root/"baseline.db"):
        raise ValueError("rollback byte mismatch")
    return {"status":"PASS_WITH_LIMITATIONS", "migrations_before":len(old_versions),
            "migrations_after":len(versions), "tables_before":len(before),
            "tables_after":len(migrated), "existing_rows_preserved":True,
            "migration_idempotent":True, "offline_tick_executions":len(tick.executions),
            "transport_attempts_denied":transport.attempts, "socket_attempts_denied":socket_attempts[0],
            "observation_before":pre, "observation_after":post,
            "retention":retention, "retention_rehearsal":rehearsal,
            "rollback":"BYTE_EXACT_BASELINE_RESTORE", "limits":LIMITS,
            "production_modified":False, "send":False}


def qualify(snapshot, *, expected_sha256, timeout_seconds=60):
    """Pin bounded immutable snapshot bytes, then qualify only a private copy."""
    if not isinstance(expected_sha256, str) or not re.fullmatch(r"[0-9a-f]{64}", expected_sha256):
        raise ValueError("SHA256 required")
    if type(timeout_seconds) not in (int, float) or not 0 < timeout_seconds <= 120:
        raise ValueError("invalid timeout")
    fd = os.open(snapshot, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
    with os.fdopen(fd, "rb") as source:
        info = os.fstat(source.fileno())
        if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1 or info.st_size > MAX_SNAPSHOT:
            raise ValueError("bounded single-link regular snapshot required")
        data = source.read(MAX_SNAPSHOT+1)
    if len(data)>MAX_SNAPSHOT or hashlib.sha256(data).hexdigest()!=expected_sha256:
        raise ValueError("snapshot hash or size mismatch")
    with tempfile.TemporaryDirectory(prefix="kgm-candidate-qualification-") as temp:
        root = Path(temp)
        (root/"baseline.db").write_bytes(data)
        script = "import json,sys; from kgeopolitical_monitor.candidate_qualification_p244 import _run_copy; print(json.dumps(_run_copy(sys.argv[1]),sort_keys=True))"
        # Import trusted checked-out candidate via absolute source path. No
        # credentials or inherited Python startup configuration in the child.
        env = {"PATH": os.defpath, "PYTHONPATH": str(Path(__file__).resolve().parents[1])}
        try:
            result = subprocess.run([sys.executable, "-c", script, temp], cwd=temp,
                                    env=env, capture_output=True, text=True, timeout=timeout_seconds)
        except subprocess.TimeoutExpired:
            return {"status":"FAIL", "cause":"TIMEOUT", "child_reaped":True, "send":False}
        if result.returncode:
            # Do not leak errors or DB values from candidate processing.
            return {"status":"FAIL", "cause":"CHILD_FAILED", "returncode":result.returncode, "send":False}
        report = json.loads(result.stdout)
        report["snapshot_sha256"] = expected_sha256
        report["temporary_workspace_removed"] = True
    return report


def main(argv=None):
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('snapshot', type=Path)
    parser.add_argument('--expected-sha256', required=True)
    args = parser.parse_args(argv)
    report = qualify(args.snapshot, expected_sha256=args.expected_sha256)
    print(json.dumps(report, sort_keys=True))
    return 0 if report['status'] == 'PASS_WITH_LIMITATIONS' else 1


if __name__ == '__main__':
    raise SystemExit(main())
