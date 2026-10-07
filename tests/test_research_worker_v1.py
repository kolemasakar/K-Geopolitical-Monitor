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
            "published_at_utc":"2026-09-02T11:00:00Z" if ok else None,
            "available_at_utc":"2026-09-02T11:30:00Z" if ok else None,
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
        observed_at_utc="2026-09-28T12:05:00Z")["pending"]==[]

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
    assert report["pending"]==[("ktrader","req-01")]

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
        observed_at_utc="2026-09-28T12:05:00Z")["pending"]==[("ktrader","req-01")]

def test_retry_after_adapter_crash_is_idempotent(tmp_path):
    req=accepted(tmp_path)
    calls={"n":0}
    def flaky(r):
        calls["n"]+=1
        if calls["n"]==1: raise RuntimeError("injected adapter crash")
        return adapter()(r)
    with pytest.raises(RuntimeError):
        execute_deterministic(tmp_path,"ktrader","req-01",request=req,
            allowed_consumers=POLICY,adapters=[flaky],
            processing_at_utc="2026-09-28T12:02:00Z",completed_at_utc="2026-09-28T12:04:00Z")
    artifact=execute_deterministic(tmp_path,"ktrader","req-01",request=req,
        allowed_consumers=POLICY,adapters=[flaky],
        processing_at_utc="2026-09-28T12:03:00Z",completed_at_utc="2026-09-28T12:04:00Z")
    assert artifact["result"]["research_status"]=="COMPLETE"
    assert recover_pending(tmp_path,allowed_consumers=POLICY,
        observed_at_utc="2026-09-28T12:05:00Z")["pending"]==[]

def test_worker_replay_after_terminal_does_not_rerun_adapter(tmp_path):
    req=accepted(tmp_path)
    first=execute_deterministic(tmp_path,"ktrader","req-01",request=req,
        allowed_consumers=POLICY,adapters=[adapter()],
        processing_at_utc="2026-09-28T12:02:00Z",completed_at_utc="2026-09-28T12:04:00Z")
    calls={"n":0}
    def must_not_run(_):
        calls["n"]+=1
        raise AssertionError("terminal replay invoked adapter")
    with pytest.raises(ValueError):
        execute_deterministic(tmp_path,"ktrader","req-01",request=req,
            allowed_consumers=POLICY,adapters=[must_not_run],
            processing_at_utc="2026-09-28T12:06:00Z",completed_at_utc="2026-09-28T12:07:00Z")
    assert calls["n"]==0
    assert complete_or_reconcile(tmp_path,"ktrader","req-01",
        allowed_consumers=POLICY)==first

def test_worker_accepts_bounded_observation_batch(tmp_path):
    req=accepted(tmp_path)
    def batch(r):
        a=adapter(oid="obs-01")(r); b=adapter(oid="obs-02")(r)
        b["public_url"]="https://example.test/item-2"
        return [a,b]
    artifact=execute_deterministic(tmp_path,"ktrader","req-01",request=req,
        allowed_consumers=POLICY,adapters=[batch],
        processing_at_utc="2026-09-28T12:02:00Z",completed_at_utc="2026-09-28T12:04:00Z")
    assert artifact["result"]["research_status"]=="COMPLETE"
    assert len(artifact["result"]["records"])==2

def test_worker_rejects_unbounded_observation_batch(tmp_path):
    req=accepted(tmp_path)
    def batch(r):
        out=[]
        for n in range(101):
            item=adapter(oid=f"obs-{n:03d}")(r); item["public_url"]=f"https://example.test/{n}"
            out.append(item)
        return out
    with pytest.raises(ValueError,match="unbounded adapter observations"):
        execute_deterministic(tmp_path,"ktrader","req-01",request=req,
            allowed_consumers=POLICY,adapters=[batch],
            processing_at_utc="2026-09-28T12:02:00Z",completed_at_utc="2026-09-28T12:04:00Z")
