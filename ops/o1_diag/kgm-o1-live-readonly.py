#!/usr/bin/env python3
"""KGM O1: bounded summary-only inspection of canonical live SQLite.

Run only through an approved, audited admin channel. No deployment, no exports,
no journal bodies, no raw rows, no attempts to impersonate the kgm user.
"""
import datetime as dt
import json
import os
import sqlite3
import subprocess
import sys
import time

DB = "/opt/k-geopolitical-monitor/data/kgeopolitical_monitor.db"
DEADLINE = time.monotonic() + 25.0

def now():
    return dt.datetime.now(dt.timezone.utc).isoformat()

def systemd():
    p = subprocess.run(
        ["systemctl", "show", "kgm-monitor.service",
         "-p", "ActiveState", "-p", "SubState", "-p", "MainPID",
         "-p", "NRestarts", "-p", "ExecMainStartTimestamp"],
        capture_output=True, text=True, timeout=8, check=False)
    if p.returncode != 0:
        return {"error": "systemctl_failed", "exit_code": p.returncode}
    return dict(line.split("=", 1) for line in p.stdout.splitlines()
                if "=" in line)

def main():
    out = {"format": "KGM_O1_LIVE_READONLY_V1",
           "observed_at": now(), "uid": os.geteuid(),
           "service": systemd(), "db": {}}
    if os.geteuid() != 0:
        out["db"]["status"] = "DENIED_NOT_ROOT"
        print(json.dumps(out, sort_keys=True))
        return 2
    if not os.path.isfile(DB):
        out["db"]["status"] = "MISSING"
        print(json.dumps(out, sort_keys=True))
        return 2
    try:
        uri = "file:" + DB + "?mode=ro"
        conn = sqlite3.connect(uri, uri=True, timeout=3)
        try:
            conn.execute("PRAGMA query_only=ON")
            conn.execute("PRAGMA busy_timeout=3000")
            conn.set_progress_handler(lambda: int(time.monotonic() >= DEADLINE), 1000)
            check = conn.execute("PRAGMA integrity_check").fetchone()
            out["db"]["integrity_check"] = check[0] if check else "NO_RESULT"
            fk = conn.execute("PRAGMA foreign_key_check")
            count = 0
            for _ in fk:
                count += 1
                if count > 100000:
                    raise RuntimeError("fk_violation_count_limit")
            out["db"]["foreign_key_violations"] = count
            tables = [r[0] for r in conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table'")]
            out["db"]["table_count"] = len(tables)
            if "schema_migrations" in tables:
                out["db"]["migration_count"] = conn.execute(
                    "SELECT count(*) FROM schema_migrations").fetchone()[0]
            else:
                out["db"]["migration_count"] = None
            out["db"]["possible_cycle_tables"] = sorted(
                name for name in tables if any(
                    token in name.lower() for token in
                    ("cycle", "run", "worker", "source", "ingest", "heartbeat"))
                )[:30]
            out["db"]["cycle_success_at"] = "UNVERIFIED_SCHEMA_SPECIFIC_QUERY_REQUIRED"
            out["db"]["source_freshness"] = "UNVERIFIED_SCHEMA_SPECIFIC_QUERY_REQUIRED"
            out["db"]["loaded_code_identity"] = "UNKNOWN"
            out["db"]["status"] = (
                "INTEGRITY_PASS" if out["db"]["integrity_check"] == "ok"
                and count == 0 else "INTEGRITY_SHORTFALL")
        finally:
            conn.close()
    except Exception as e:
        out["db"]["status"] = "ERROR"
        out["db"]["error_type"] = type(e).__name__
    print(json.dumps(out, sort_keys=True))
    return 0 if out["db"].get("status") == "INTEGRITY_PASS" else 3

if __name__ == "__main__":
    sys.exit(main())
