import json
import pytest
from kgeopolitical_monitor.research_evidence_archive_index_v1 import (
    rebuild_archive_index, load_archive_index, select_historical_snapshot_indexed,
    select_historical_snapshot_fast, maintain_archive_index, plan_archive_retention)
from kgeopolitical_monitor.research_evidence_archive_v1 import select_historical_snapshot
from kgeopolitical_monitor.research_typed_workflow_v1 import accept_request
from kgeopolitical_monitor.research_worker_v2 import execute_policy_bound
from test_research_worker_v2 import accepted, policy, obs, execute, historical_from
from test_research_completion_v1 import POLICY

def seed(root, request_id="req-01"):
    req=accepted(root,request_id=request_id)
    p=policy(req)
    execute_policy_bound(root,"ktrader",request_id,request=req,
        allowed_consumers=POLICY,source_policy=p,
        adapters={"source-a":obs("source-a","a-"+request_id),
                  "source-b":obs("source-b","b-"+request_id)},
        processing_at_utc="2026-09-28T12:02:00Z",
        staged_at_utc="2026-09-28T12:03:00Z",
        completed_at_utc="2026-09-28T12:04:00Z")
    return req,p

def historical(current, request_id="hist-01"):
    h=historical_from(current,request_id=request_id,
                      as_of="2026-09-28T12:03:00Z")
    return h,policy(h)

def test_rebuilt_index_selects_same_snapshot_as_authoritative_scan(tmp_path):
    current,p=seed(tmp_path)
    index=rebuild_archive_index(tmp_path,"ktrader",
        generated_at_utc="2026-09-28T12:05:00Z")
    assert len(index["index"]["entries"])==1
    hist,hp=historical(current)
    scan=select_historical_snapshot(tmp_path,"ktrader",request=hist,source_policy=hp)
    indexed=select_historical_snapshot_indexed(tmp_path,"ktrader",
        request=hist,source_policy=hp)
    assert indexed["sha256"]==scan["sha256"]

def test_stale_index_fails_closed_after_new_archive_entry(tmp_path):
    current,_=seed(tmp_path,"req-01")
    rebuild_archive_index(tmp_path,"ktrader",
        generated_at_utc="2026-09-28T12:05:00Z")
    seed(tmp_path,"req-02")
    hist,hp=historical(current)
    with pytest.raises(ValueError,match="stale"):
        select_historical_snapshot_indexed(tmp_path,"ktrader",
            request=hist,source_policy=hp)

def test_corrupt_index_integrity_is_denied(tmp_path):
    seed(tmp_path)
    rebuild_archive_index(tmp_path,"ktrader",
        generated_at_utc="2026-09-28T12:05:00Z")
    path=tmp_path/"evidence_archive_index"/"ktrader.json"
    obj=json.loads(path.read_text())
    obj["index"]["generated_at_utc"]="2026-09-28T12:06:00Z"
    path.write_text(json.dumps(obj))
    with pytest.raises(ValueError,match="integrity"):
        load_archive_index(tmp_path,"ktrader")

def test_retention_planner_is_non_destructive(tmp_path):
    seed(tmp_path,"req-01")
    seed(tmp_path,"req-02")
    rebuild_archive_index(tmp_path,"ktrader",
        generated_at_utc="2026-09-28T12:05:00Z")
    before=sorted((tmp_path/"evidence_archive"/"ktrader").glob("*.json"))
    plan=plan_archive_retention(tmp_path,"ktrader",keep_latest=1)
    after=sorted((tmp_path/"evidence_archive"/"ktrader").glob("*.json"))
    assert len(plan["keep"])==1
    assert len(plan["delete_candidates"])==1
    assert plan["destructive_action_performed"] is False
    assert [x.name for x in before]==[x.name for x in after]


def test_fast_path_uses_verified_index(tmp_path):
    current,_=seed(tmp_path)
    rebuild_archive_index(tmp_path,"ktrader",
        generated_at_utc="2026-09-28T12:05:00Z")
    hist,hp=historical(current)
    snapshot,path=select_historical_snapshot_fast(
        tmp_path,"ktrader",request=hist,source_policy=hp)
    assert path=="INDEX"
    assert snapshot["entry"]["archived_request"]["request_id"]=="req-01"

def test_fast_path_falls_back_when_index_stale(tmp_path):
    current,_=seed(tmp_path,"req-01")
    rebuild_archive_index(tmp_path,"ktrader",
        generated_at_utc="2026-09-28T12:05:00Z")
    seed(tmp_path,"req-02")
    hist,hp=historical(current)
    snapshot,path=select_historical_snapshot_fast(
        tmp_path,"ktrader",request=hist,source_policy=hp)
    assert path=="AUTHORITATIVE_SCAN_FALLBACK"
    assert snapshot["entry"]["archived_request"]["request_id"] in {"req-01","req-02"}

def test_fast_path_falls_back_when_index_missing(tmp_path):
    current,_=seed(tmp_path)
    hist,hp=historical(current)
    snapshot,path=select_historical_snapshot_fast(
        tmp_path,"ktrader",request=hist,source_policy=hp)
    assert path=="AUTHORITATIVE_SCAN_FALLBACK"
    assert snapshot["entry"]["archived_request"]["request_id"]=="req-01"


def test_index_maintenance_rebuilds_then_appends(tmp_path):
    seed(tmp_path,"req-01")
    payload,mode=maintain_archive_index(tmp_path,"ktrader",
        generated_at_utc="2026-09-28T12:05:00Z")
    assert mode=="REBUILD"
    assert len(payload["index"]["entries"])==1
    seed(tmp_path,"req-02")
    payload,mode=maintain_archive_index(tmp_path,"ktrader",
        generated_at_utc="2026-09-28T12:06:00Z")
    assert mode=="APPEND"
    assert len(payload["index"]["entries"])==2

def test_index_maintenance_repairs_corrupt_index(tmp_path):
    seed(tmp_path,"req-01")
    maintain_archive_index(tmp_path,"ktrader",
        generated_at_utc="2026-09-28T12:05:00Z")
    path=tmp_path/"evidence_archive_index"/"ktrader.json"
    path.write_text('{"broken":true}')
    payload,mode=maintain_archive_index(tmp_path,"ktrader",
        generated_at_utc="2026-09-28T12:06:00Z")
    assert mode=="REBUILD"
    assert len(payload["index"]["entries"])==1

def test_worker_current_execution_maintains_index(tmp_path):
    req=accepted(tmp_path); p=policy(req)
    execute(tmp_path,req,p,{"source-a":obs("source-a","a-1"),
                            "source-b":obs("source-b","b-1")})
    payload=load_archive_index(tmp_path,"ktrader")
    assert payload is not None
    assert len(payload["index"]["entries"])==1
