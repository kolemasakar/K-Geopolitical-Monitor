import pytest
from kgeopolitical_monitor.research_typed_workflow_v1 import accept_request, recover_pending
from kgeopolitical_monitor.research_worker_v1 import execute_deterministic
from kgeopolitical_monitor.research_completion_v1 import complete_or_reconcile
from test_research_typed_result_v1 import typed
from test_research_completion_v1 import POLICY

def adapter(status="SUCCESS", oid="obs-01"):
    def run(req):
        ok=status in {"SUCCESS","PARTIAL"}
        return {"schema_version":"kgm.source.observation.v1","request_id":req["request_id"],
            "source_id":"source-a","observation_id":oid,"status":status,
            "observed_at_utc":"2026-09-28T12:00:00Z",
            "published_at_utc":"2026-09-28T11:00:00Z" if ok else None,
            "available_at_utc":"2026-09-28T11:30:00Z" if ok else None,
            "public_url":"https://example.test/item" if ok else None,
            "summary":"deterministic evidence" if ok else None,
            "error_code":None if ok else "TIMEOUT"}
    return run

def accepted(root):
    req,_=typed()
    accept_request(root,req,allowed_consumers=POLICY,
                   accepted_at_utc="2026-09-28T12:01:00Z")
    return req

def test_worker_complete_end_to_end(tmp_path):
    req=accepted(tmp_path)
    artifact=execute_deterministic(tmp_path,"ktrader","req-01",request=req,
        allowed_consumers=POLICY,adapters=[adapter()],
        processing_at_utc="2026-09-28T12:02:00Z",completed_at_utc="2026-09-28T12:04:00Z")
    assert artifact["result"]["research_status"]=="COMPLETE"
    assert recover_pending(tmp_path,allowed_consumers=POLICY,
        observed_at_utc="2026-09-28T12:05:00Z")["items"]==[]

def test_worker_unavailable_is_partial_not_false_complete(tmp_path):
    req=accepted(tmp_path)
    artifact=execute_deterministic(tmp_path,"ktrader","req-01",request=req,
        allowed_consumers=POLICY,adapters=[adapter("UNAVAILABLE")],
        processing_at_utc="2026-09-28T12:02:00Z",completed_at_utc="2026-09-28T12:04:00Z")
    assert artifact["result"]["research_status"]=="PARTIAL"
    assert artifact["result"]["source_health"]=="UNAVAILABLE"

def test_adapter_crash_leaves_processing_recoverable(tmp_path):
    req=accepted(tmp_path)
    def crash(_): raise RuntimeError("injected adapter crash")
    with pytest.raises(RuntimeError,match="injected"):
        execute_deterministic(tmp_path,"ktrader","req-01",request=req,
            allowed_consumers=POLICY,adapters=[crash],
            processing_at_utc="2026-09-28T12:02:00Z",completed_at_utc="2026-09-28T12:04:00Z")
    report=recover_pending(tmp_path,allowed_consumers=POLICY,
        observed_at_utc="2026-09-28T12:05:00Z")
    assert report["items"][0]["status"]=="PROCESSING"

def test_invalid_observation_leaves_processing_recoverable(tmp_path):
    req=accepted(tmp_path)
    bad=adapter()
    def corrupt(r):
        item=bad(r); item["public_url"]="file:///forbidden"; return item
    with pytest.raises(ValueError):
        execute_deterministic(tmp_path,"ktrader","req-01",request=req,
            allowed_consumers=POLICY,adapters=[corrupt],
            processing_at_utc="2026-09-28T12:02:00Z",completed_at_utc="2026-09-28T12:04:00Z")
    assert recover_pending(tmp_path,allowed_consumers=POLICY,
        observed_at_utc="2026-09-28T12:05:00Z")["items"][0]["status"]=="PROCESSING"
