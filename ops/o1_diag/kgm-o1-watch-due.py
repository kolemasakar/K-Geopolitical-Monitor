#!/usr/bin/env python3
"""Read-only, aggregate-only watch scheduling audit. No watch IDs, names, queries or raw rows."""
import datetime as dt
import json
import os
import sqlite3
import sys
import time

DB = "/opt/k-geopolitical-monitor/data/kgeopolitical_monitor.db"
DEADLINE = time.monotonic() + 20

def parse_time(value):
    if value is None:
        return None
    try:
        x = dt.datetime.fromisoformat(str(value).replace("Z", "+00:00"))
        if x.tzinfo is None:
            return None
        return x.astimezone(dt.timezone.utc)
    except (ValueError, TypeError):
        return None

def assess(watches, runs, now):
    result = {"watches_total": len(watches), "enabled": 0, "disabled": 0,
              "due": 0, "not_due": 0, "no_prior_run_due": 0,
              "running_blocked": 0, "invalid_cadence": 0,
              "invalid_run_timestamp": 0, "latest_run_missing": 0,
              "latest_run_status": {"COMPLETED": 0, "FAILED": 0, "RUNNING": 0, "OTHER": 0},
              "next_due_earliest_utc": None, "most_overdue_minutes": None,
              "cadence_min_minutes": None, "cadence_max_minutes": None}
    next_due = []
    overdue = []
    for watch_id, enabled, cadence in watches:
        if not bool(enabled):
            result["disabled"] += 1
            continue
        result["enabled"] += 1
        try:
            cadence = int(cadence)
            if cadence <= 0:
                raise ValueError("invalid cadence")
        except (ValueError, TypeError):
            result["invalid_cadence"] += 1
            continue
        result["cadence_min_minutes"] = min(result["cadence_min_minutes"], cadence) if result["cadence_min_minutes"] is not None else cadence
        result["cadence_max_minutes"] = max(result["cadence_max_minutes"], cadence) if result["cadence_max_minutes"] is not None else cadence
        last = runs.get(watch_id)
        if last is None:
            result["latest_run_missing"] += 1
            result["no_prior_run_due"] += 1
            result["due"] += 1
            continue
        status, started_at = last
        category = str(status).upper() if str(status).upper() in result["latest_run_status"] else "OTHER"
        result["latest_run_status"][category] += 1
        if category == "RUNNING":
            result["running_blocked"] += 1
            continue
        started = parse_time(started_at)
        if started is None:
            result["invalid_run_timestamp"] += 1
            continue
        due_at = started + dt.timedelta(minutes=cadence)
        next_due.append(due_at)
        if now >= due_at:
            result["due"] += 1
            overdue.append((now - due_at).total_seconds() / 60)
        else:
            result["not_due"] += 1
    if next_due:
        result["next_due_earliest_utc"] = min(next_due).isoformat()
    if overdue:
        result["most_overdue_minutes"] = round(max(overdue), 1)
    return result

def main():
    now = dt.datetime.now(dt.timezone.utc)
    out = {"format": "KGM_O1_WATCH_DUE_AGGREGATES_V1", "observed_at": now.isoformat(),
           "state": "UNVERIFIED", "source_activation": "NOT_CHECKED",
           "loaded_code_sha": "UNKNOWN"}
    if os.geteuid() != 0:
        out["state"] = "DENIED_NOT_ROOT"
        print(json.dumps(out, sort_keys=True))
        return 2
    try:
        conn = sqlite3.connect("file:" + DB + "?mode=ro", uri=True, timeout=3, isolation_level=None)
        try:
            conn.execute("PRAGMA query_only=ON")
            conn.execute("PRAGMA busy_timeout=3000")
            conn.set_progress_handler(lambda: int(time.monotonic() >= DEADLINE), 1000)
            conn.execute("BEGIN")
            schema = {r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}
            if not {"monitoring_watches", "monitoring_runs"} <= schema:
                out["state"] = "SCHEMA_MISSING"
            else:
                wc = {r[1] for r in conn.execute("PRAGMA table_info(monitoring_watches)")}
                rc = {r[1] for r in conn.execute("PRAGMA table_info(monitoring_runs)")}
                if not {"watch_id", "enabled", "cadence_minutes"} <= wc or not {"watch_id", "status", "started_at", "run_id"} <= rc:
                    out["state"] = "SCHEMA_UNEXPECTED"
                else:
                    watches = conn.execute("SELECT watch_id, enabled, cadence_minutes FROM monitoring_watches").fetchall()
                    last = {}
                    for wid, status, started in conn.execute(
                        "SELECT watch_id, status, started_at FROM monitoring_runs "
                        "WHERE run_id = (SELECT run_id FROM monitoring_runs m2 "
                        "WHERE m2.watch_id = monitoring_runs.watch_id "
                        "ORDER BY m2.started_at DESC, m2.run_id DESC LIMIT 1)"):
                        last[wid] = (status, started)
                    out["watch_schedule"] = assess(watches, last, now)
                    out["state"] = "AGGREGATES_COLLECTED_REVIEW_REQUIRED"
            conn.execute("ROLLBACK")
        finally:
            conn.close()
    except Exception as e:
        out["state"] = "ERROR"
        out["error_type"] = type(e).__name__
    print(json.dumps(out, sort_keys=True))
    return 0 if out["state"] == "AGGREGATES_COLLECTED_REVIEW_REQUIRED" else 3

if __name__ == "__main__":
    sys.exit(main())
