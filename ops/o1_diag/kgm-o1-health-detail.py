#!/usr/bin/env python3
"""O1 bounded live health read-only attestation: only approved aggregates.

Do not emit raw errors, URLs, payloads, watch IDs or secrets.
"""
import datetime as dt
import json
import os
import sqlite3
import sys
import time

DB="/opt/k-geopolitical-monitor/data/kgeopolitical_monitor.db"
DEADLINE=time.monotonic()+20
ALLOWED_SOURCE={"GDACS","GDELT","CONSILIUM","GCC"}
HEALTH_TIME=("last_supervisor_tick_at","last_completed_tick_at","last_successful_execution_at")
HEALTH_COUNTS=("recovered_runs","execution_count","completed_execution_count","failed_execution_count")

def canonical_time(v):
    if v is None: return "EMPTY"
    try:
        if isinstance(v,(int,float)):
            n=float(v)
            if n>1e14: n/=1e6
            elif n>1e11: n/=1e3
            d=dt.datetime.fromtimestamp(n,dt.timezone.utc)
        else:
            d=dt.datetime.fromisoformat(str(v).replace("Z","+00:00"))
            if d.tzinfo is None: d=d.replace(tzinfo=dt.timezone.utc)
        if not (2000<=d.year<=2100): return "UNPARSEABLE"
        return d.astimezone(dt.timezone.utc).isoformat()
    except (ValueError,TypeError,OverflowError,OSError):
        return "UNPARSEABLE"

def columns(conn, name):
    return {r[1] for r in conn.execute("PRAGMA table_info(\""+name+"\")")}

def main():
    out={"format":"KGM_O1_HEALTH_DETAIL_V1","observed_at":dt.datetime.now(dt.timezone.utc).isoformat(),
         "status":"UNVERIFIED","service_health":{},"attempt_sources":{}}
    if os.geteuid()!=0:
        out["status"]="BLOCKED_NONROOT";print(json.dumps(out,sort_keys=True));return 2
    try:
        c=sqlite3.connect("file:"+DB+"?mode=ro",uri=True,timeout=3,isolation_level=None)
        try:
            c.execute("PRAGMA query_only=ON")
            c.execute("PRAGMA busy_timeout=3000")
            c.set_progress_handler(lambda:int(time.monotonic()>DEADLINE),1000)
            c.execute("BEGIN")
            tables={r[0] for r in c.execute("SELECT name FROM sqlite_master WHERE type='table'")}
            if "owner_runtime_health" not in tables:
                out["service_health"]["status"]="TABLE_MISSING"
            else:
                cols=columns(c,"owner_runtime_health")
                expected=set(HEALTH_TIME+HEALTH_COUNTS+("tick_status",))
                available=sorted(expected&cols)
                out["service_health"]["available_columns"]=available
                out["service_health"]["row_count"]=c.execute("SELECT COUNT(*) FROM owner_runtime_health").fetchone()[0]
                if out["service_health"]["row_count"]==1:
                    fields=[x for x in HEALTH_TIME+HEALTH_COUNTS+("tick_status",) if x in cols]
                    values=c.execute("SELECT "+",".join('"'+x+'"' for x in fields)+" FROM owner_runtime_health LIMIT 1").fetchone()
                    record=dict(zip(fields,values))
                    out["service_health"]["timestamps_utc"]={x:canonical_time(record.get(x)) for x in HEALTH_TIME if x in cols}
                    out["service_health"]["counters"]={}
                    for x in HEALTH_COUNTS:
                        if x in cols:
                            v=record.get(x)
                            out["service_health"]["counters"][x]=v if type(v)==int and v>=0 else "UNVERIFIED"
                    st=str(record.get("tick_status") or "").lower()
                    out["service_health"]["tick_status_category"]=(
                        "SUCCESS" if st in {"ok","success","succeeded","complete","completed"} else
                        "FAIL" if st in {"failed","error","failure"} else
                        "PARTIAL" if st in {"partial","degraded"} else "OTHER_OR_EMPTY")
                else:
                    out["service_health"]["status"]="UNEXPECTED_ROW_COUNT"
            if "source_collection_attempts" in tables:
                cols=columns(c,"source_collection_attempts")
                if {"source_name","status"}<=cols:
                    count={}
                    for src,st,n in c.execute("SELECT source_name,status,COUNT(*) FROM source_collection_attempts GROUP BY source_name,status"):
                        key=str(src or "").strip().upper()
                        key=key if key in ALLOWED_SOURCE else "OTHER"
                        bucket=count.setdefault(key,{"rows":0,"success":0,"fail":0,"other":0})
                        bucket["rows"]+=int(n)
                        cat=str(st or "").lower()
                        if cat in ("success","succeeded","ok","complete","completed"): bucket["success"]+=int(n)
                        elif cat in ("fail","failed","error","failure"): bucket["fail"]+=int(n)
                        else: bucket["other"]+=int(n)
                    out["attempt_sources"]=count
                else: out["attempt_sources"]={"status":"SCHEMA_UNEXPECTED"}
            else: out["attempt_sources"]={"status":"TABLE_MISSING"}
            c.execute("ROLLBACK")
            out["status"]="SUMMARY_COLLECTED_REVIEW_REQUIRED"
        finally: c.close()
    except Exception as exc:
        out["status"]="ERROR"
        out["error_type"]=type(exc).__name__
    print(json.dumps(out,sort_keys=True))
    return 0 if out["status"]=="SUMMARY_COLLECTED_REVIEW_REQUIRED" else 3

if __name__=="__main__":sys.exit(main())
