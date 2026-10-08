import pytest
from kgeopolitical_monitor.research_typed_workflow_v1 import accept_request, recover_pending
from kgeopolitical_monitor.research_durable_lifecycle_v1 import recovery_snapshot
from kgeopolitical_monitor.research_worker_v2 import execute_policy_bound
from kgeopolitical_monitor.research_observation_stage_v1 import load_observation_stage
from test_research_typed_result_v1 import typed
from test_research_completion_v1 import POLICY

def accepted(root):
    req,_=typed()
    accept_request(root,req,allowed_consumers=POLICY,
                   accepted_at_utc="2026-09-28T12:01:00Z")
    return req

def policy(req, required=("source-a","source-b"), optional=()):
    return {"schema_version":"kgm.source.policy.v1",
        "consumer_id":req["consumer_id"],"policy_version":req["policy_version"],
        "required_source_ids":list(required),"optional_source_ids":list(optional),
        "max_observations":20}

def obs(source_id, oid="obs-01", status="SUCCESS", summary=None):
    def run(req):
        ok=status in {"SUCCESS","PARTIAL"}
        return {"schema_version":"kgm.source.observation.v1","request_id":req["request_id"],
            "source_id":source_id,"observation_id":oid,"status":status,
            "observed_at_utc":"2026-09-28T12:02:10Z",
            "published_at_utc":"2026-09-02T11:00:00Z" if ok else None,
            "available_at_utc":"2026-09-02T11:30:00Z" if ok else None,
            "public_url":f"https://{source_id}.example/item" if ok else None,
            "summary":summary or (f"{source_id} evidence" if ok else None),
            "error_code":None if ok else "TIMEOUT"}
    return run

def execute(root, req, source_policy, adapters, **extra):
    args=dict(request=req,allowed_consumers=POLICY,source_policy=source_policy,
        adapters=adapters,processing_at_utc="2026-09-28T12:02:00Z",
        staged_at_utc="2026-09-28T12:03:00Z",
        completed_at_utc="2026-09-28T12:04:00Z")
    args.update(extra)
    return execute_policy_bound(root,"ktrader","req-01",**args)

def test_required_source_portfolio_complete_and_staged(tmp_path):
    req=accepted(tmp_path); p=policy(req)
    artifact=execute(tmp_path,req,p,{"source-a":obs("source-a","a-1"),
                                    "source-b":obs("source-b","b-1")})
    assert artifact["result"]["research_status"]=="COMPLETE"
    assert artifact["result"]["source_health"]=="HEALTHY"
    stage=load_observation_stage(tmp_path,"ktrader","req-01",request=req,source_policy=p)
    assert stage is not None
    assert [x["source_id"] for x in stage["stage"]["source_runs"]]==["source-a","source-b"]
    assert len(stage["stage"]["observations"])==2

def test_missing_required_adapter_denied_before_processing(tmp_path):
    req=accepted(tmp_path); p=policy(req)
    with pytest.raises(ValueError,match="required source adapter missing"):
        execute(tmp_path,req,p,{"source-a":obs("source-a")})
    pending=recovery_snapshot(tmp_path,allowed_consumers=POLICY)
    assert pending[0]["status"]=="ACCEPTED"

def test_unapproved_adapter_denied(tmp_path):
    req=accepted(tmp_path); p=policy(req,required=("source-a",))
    with pytest.raises(ValueError,match="unapproved source adapter"):
        execute(tmp_path,req,p,{"source-a":obs("source-a"),"source-x":obs("source-x")})

def test_adapter_source_identity_is_policy_bound(tmp_path):
    req=accepted(tmp_path); p=policy(req,required=("source-a",))
    with pytest.raises(ValueError,match="mismatched source identity"):
        execute(tmp_path,req,p,{"source-a":obs("source-b")})

def test_staged_snapshot_reused_after_crash_without_requery(tmp_path):
    req=accepted(tmp_path); p=policy(req)
    calls={"source-a":0,"source-b":0}
    def counted(source, oid):
        base=obs(source,oid)
        def run(r):
            calls[source]+=1
            return base(r)
        return run
    adapters={"source-a":counted("source-a","a-1"),
              "source-b":counted("source-b","b-1")}
    def crash(_):
        raise RuntimeError("crash after durable stage")
    with pytest.raises(RuntimeError,match="after durable stage"):
        execute(tmp_path,req,p,adapters,after_stage=crash)
    assert calls=={"source-a":1,"source-b":1}
    stage=load_observation_stage(tmp_path,"ktrader","req-01",request=req,source_policy=p)
    assert stage is not None
    artifact=execute(tmp_path,req,p,adapters,
        processing_at_utc="2026-09-28T12:04:00Z",
        staged_at_utc="2026-09-28T12:04:10Z",
        completed_at_utc="2026-09-28T12:05:00Z")
    assert artifact["result"]["research_status"]=="COMPLETE"
    assert calls=={"source-a":1,"source-b":1}

def test_required_source_failure_forces_partial(tmp_path):
    req=accepted(tmp_path); p=policy(req)
    artifact=execute(tmp_path,req,p,{"source-a":obs("source-a","a-1"),
                                    "source-b":obs("source-b","b-1","UNAVAILABLE")})
    assert artifact["result"]["research_status"]=="PARTIAL"
    assert artifact["result"]["coverage"]=="PARTIAL"
    assert artifact["result"]["source_health"]=="DEGRADED"

def test_required_source_can_be_healthy_empty_without_false_failure(tmp_path):
    req=accepted(tmp_path); p=policy(req)
    artifact=execute(tmp_path,req,p,{"source-a":obs("source-a","a-1"),
                                    "source-b":lambda _:[]})
    assert artifact["result"]["research_status"]=="COMPLETE"
    assert artifact["result"]["source_health"]=="HEALTHY"
    stage=load_observation_stage(tmp_path,"ktrader","req-01",request=req,source_policy=p)
    runs={x["source_id"]:x for x in stage["stage"]["source_runs"]}
    assert runs["source-b"]=={"source_id":"source-b","status":"EMPTY","observation_count":0}

def test_stage_policy_digest_prevents_reuse_under_changed_portfolio(tmp_path):
    req=accepted(tmp_path); p=policy(req)
    with pytest.raises(RuntimeError):
        execute(tmp_path,req,p,{"source-a":obs("source-a"),"source-b":obs("source-b")},
                after_stage=lambda _:(_ for _ in ()).throw(RuntimeError("stop")))
    changed=policy(req,required=("source-a",),optional=("source-b",))
    with pytest.raises(ValueError,match="source policy digest mismatch"):
        execute(tmp_path,req,changed,{"source-a":obs("source-a"),"source-b":obs("source-b")})
