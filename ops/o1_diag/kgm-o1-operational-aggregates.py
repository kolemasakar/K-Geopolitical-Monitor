#!/usr/bin/env python3
"""O1 read-only operational evidence. Emits ONLY schema names and aggregates.

No raw row values, environment, logs, process memory, uploaded database, or file writes.
A completed run is NOT an operational acceptance decision.
"""
import datetime
import json
import os
import re
import sqlite3
import subprocess
import sys
import time

DB = "/opt/k-geopolitical-monitor/data/kgeopolitical_monitor.db"
TABLES = (
    "monitoring_runs", "live_analysis_runs", "live_source_provenance",
    "source_collection_runs", "source_collection_attempts",
    "source_freshness", "owner_runtime_health",
)
TIME_NAMES = (
    "completed_at", "finished_at", "ended_at", "success_at",
    "last_success_at", "last_successful_at", "last_successful_run_at",
    "collected_at", "checked_at", "observed_at", "updated_at",
    "created_at", "started_at", "timestamp", "run_at",
)
STATUS_NAMES = ("status", "run_status", "state", "result", "outcome")
SOURCE_NAMES = ("source", "source_name", "source_id", "provider", "provider_name")
STATUS_MAP = {
    "success": "SUCCESS", "succeeded": "SUCCESS", "ok": "SUCCESS",
    "complete": "SUCCESS", "completed": "SUCCESS", "pass": "SUCCESS",
    "partial": "PARTIAL", "degraded": "PARTIAL",
    "failed": "FAIL", "failure": "FAIL", "error": "FAIL",
    "rejected": "FAIL", "timeout": "FAIL",
    "running": "RUNNING", "in_progress": "RUNNING",
    "pending": "PENDING", "queued": "PENDING",
}
STOP = time.monotonic() + 25

def quoted(s):
    return '"' + s.replace('"', '""') + '"'

def date_value(v):
    if v is None:
        return None
    try:
        if isinstance(v, (int, float)):
            n = float(v)
            if n > 1e14: n /= 1e6
            elif n > 1e11: n /= 1e3
            if not (946684800 <= n <= 4102444800): return None
            return datetime.datetime.fromtimestamp(n, datetime.timezone.utc).isoformat()
        x = str(v).strip()
        if len(x) > 40 or not re.match(r"^\d{4}-\d\d-\d\d", x):
            return None
        d = datetime.datetime.fromisoformat(x.replace("Z", "+00:00"))
        if d.tzinfo is None: d = d.replace(tzinfo=datetime.timezone.utc)
        return d.astimezone(datetime.timezone.utc).isoformat()
    except (ValueError, TypeError, OverflowError, OSError):
        return None

def select_scalar(conn, sql, params=()):
    return conn.execute(sql, params).fetchone()[0]

def table_summary(conn, table):
    columns = [row[1] for row in conn.execute(
        "PRAGMA table_info(" + quoted(table) + ")")]
    names = {c.lower(): c for c in columns}
    name = quoted(table)
    info = {"columns": columns, "rows": select_scalar(conn, "SELECT COUNT(*) FROM " + name)}
    status_col = next((names[c] for c in STATUS_NAMES if c in names), None)
    if status_col:
        totals = {k: 0 for k in ("SUCCESS", "PARTIAL", "FAIL", "RUNNING", "PENDING", "OTHER")}
        for status, count in conn.execute(
            "SELECT " + quoted(status_col) + ", COUNT(*) FROM " + name +
            " GROUP BY " + quoted(status_col)):
            key = STATUS_MAP.get(str(status).strip().lower(), "OTHER")
            totals[key] += int(count)
        info["status_column"] = status_col
        info["status_groups"] = totals
    else:
        info["status_groups"] = "UNVERIFIED_NO_RECOGNIZED_COLUMN"

    latest = {}
    for c in TIME_NAMES:
        if c in names:
            val = select_scalar(conn, "SELECT MAX(" + quoted(names[c]) + ") FROM " + name)
            latest[c] = date_value(val) or ("EMPTY" if val is None else "UNPARSEABLE")
    info["latest_time_fields_utc"] = latest or "UNVERIFIED_NO_RECOGNIZED_COLUMN"

    sc = next((names[c] for c in SOURCE_NAMES if c in names), None)
    if sc:
        results = {}
        for source in ("GDACS", "GDELT"):
            predicate = "UPPER(CAST(" + quoted(sc) + " AS TEXT)) = ?"
            results[source] = {"rows": select_scalar(
                conn, "SELECT COUNT(*) FROM " + name + " WHERE " + predicate, (source,))}
            for col in ("completed_at", "finished_at", "collected_at", "updated_at", "created_at"):
                if col in names:
                    value = select_scalar(conn,
                        "SELECT MAX(" + quoted(names[col]) + ") FROM " + name +
                        " WHERE " + predicate, (source,))
                    results[source]["latest_" + col + "_utc"] = (
                        date_value(value) or ("EMPTY" if value is None else "UNPARSEABLE"))
        info["specific_source_counts"] = results
        info["source_match_column"] = sc
    else:
        info["specific_source_counts"] = "UNVERIFIED_NO_DIRECT_SOURCE_COLUMN"
    return info

def main():
    result = {
        "format": "KGM_O1_OPERATIONAL_AGGREGATES_V1",
        "timestamp_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "euid": os.geteuid(),
        "status": "INCOMPLETE",
        "live_cycle_success": "UNVERIFIED_PENDING_SEMANTIC_MAPPING",
        "source_freshness": "UNVERIFIED_PENDING_SEMANTIC_MAPPING",
        "loaded_code_sha": "UNKNOWN",
        "tables": {},
    }
    if os.geteuid() != 0:
        result["status"] = "BLOCKED_PRIVILEGES"
        print(json.dumps(result, sort_keys=True))
        return 2
    try:
        con = sqlite3.connect("file:" + DB + "?mode=ro", uri=True, timeout=3,
                              isolation_level=None)
        try:
            con.execute("PRAGMA query_only=ON")
            con.execute("PRAGMA busy_timeout=3000")
            con.set_progress_handler(lambda: int(time.monotonic() > STOP), 1000)
            con.execute("BEGIN")
            actual = {r[0] for r in con.execute(
                "SELECT name FROM sqlite_master WHERE type='table'")}
            for name in TABLES:
                if name not in actual:
                    result["tables"][name] = {"status": "MISSING"}
                    continue
                result["tables"][name] = table_summary(con, name)
            con.execute("ROLLBACK")
            result["status"] = "AGGREGATES_COLLECTED_REVIEW_REQUIRED"
        finally:
            con.close()
    except Exception as exc:
        result["status"] = "ERROR"
        result["error_type"] = type(exc).__name__
    print(json.dumps(result, sort_keys=True))
    return 0 if result["status"] == "AGGREGATES_COLLECTED_REVIEW_REQUIRED" else 3

if __name__ == "__main__":
    sys.exit(main())
