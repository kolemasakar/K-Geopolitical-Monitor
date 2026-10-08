import copy
import pytest
from kgeopolitical_monitor.research_durable_lifecycle_v1 import admit, advance
from kgeopolitical_monitor.research_completion_v1 import complete_or_reconcile
from kgeopolitical_monitor.research_verification_decision_v1 import (
    publish_decision, effective_verification)
from test_research_typed_result_v1 import _v2
from test_research_completion_v1 import POLICY

ACTORS={"owner":"review-v1"}

def completed(tmp_path):
    req,result=_v2()
    result["records"][0]["verification"]="UNVERIFIED"
    result["records"][0]["contradictions"]=[]
    admit(tmp_path,req,allowed_consumers=POLICY)
    advance(tmp_path,"ktrader","req-01","ACCEPTED",allowed_consumers=POLICY,
            at_utc="2026-09-28T12:01:00Z")
    advance(tmp_path,"ktrader","req-01","PROCESSING",allowed_consumers=POLICY,
            at_utc="2026-09-28T12:02:00Z")
    artifact=complete_or_reconcile(tmp_path,"ktrader","req-01",
        allowed_consumers=POLICY,result=result,at_utc="2026-09-28T12:04:00Z")
    return req,result,artifact

def decision(artifact, action="VERIFY"):
    return {"schema_version":"kgm.verification.decision.v1",
        "decision_id":"verify-01","request_id":"req-01","consumer_id":"ktrader",
        "result_id":artifact["result"]["result_id"],"corroboration_id":"corr-1",
        "decision":action,"decided_at_utc":"2026-09-28T12:05:00Z",
        "actor_id":"owner","policy_version":"review-v1",
        "rationale":"Independent origins agree on the structured claim.",
        "result_artifact_sha256":artifact["sha256"]}

def test_explicit_eligible_verify_publishes_immutable_artifact(tmp_path):
    _,_,artifact=completed(tmp_path)
    d=decision(artifact)
    published=publish_decision(tmp_path,"ktrader","req-01",d,
        allowed_consumers=POLICY,allowed_actors=ACTORS)
    assert effective_verification(published)=="VERIFIED"
    assert publish_decision(tmp_path,"ktrader","req-01",d,
        allowed_consumers=POLICY,allowed_actors=ACTORS)==published

def test_ineligible_corroboration_cannot_be_verified(tmp_path):
    req,result=_v2()
    result["records"][0]["verification"]="UNVERIFIED"; result["records"][0]["contradictions"]=[]
    c=result["corroboration"][0]
    c["verification_eligibility"]="INELIGIBLE"
    c["verification_blockers"]=["NO_INDEPENDENT_ORIGIN_CREDIT"]
    c["independent_origin_credit"]=False
    c["origin_assessment"]="SAME_ORIGIN"
    c["origin_groups"]=["origin-a"]
    admit(tmp_path,req,allowed_consumers=POLICY)
    advance(tmp_path,"ktrader","req-01","ACCEPTED",allowed_consumers=POLICY,at_utc="2026-09-28T12:01:00Z")
    advance(tmp_path,"ktrader","req-01","PROCESSING",allowed_consumers=POLICY,at_utc="2026-09-28T12:02:00Z")
    artifact=complete_or_reconcile(tmp_path,"ktrader","req-01",allowed_consumers=POLICY,result=result,at_utc="2026-09-28T12:04:00Z")
    with pytest.raises(ValueError,match="not eligible"):
        publish_decision(tmp_path,"ktrader","req-01",decision(artifact),
            allowed_consumers=POLICY,allowed_actors=ACTORS)

def test_actor_must_be_explicitly_authorized(tmp_path):
    _,_,artifact=completed(tmp_path)
    d=decision(artifact); d["actor_id"]="other"
    with pytest.raises(PermissionError,match="actor denied"):
        publish_decision(tmp_path,"ktrader","req-01",d,
            allowed_consumers=POLICY,allowed_actors=ACTORS)

def test_decision_is_bound_to_exact_result_artifact(tmp_path):
    _,_,artifact=completed(tmp_path)
    d=decision(artifact); d["result_artifact_sha256"]="0"*64
    with pytest.raises(ValueError,match="snapshot mismatch"):
        publish_decision(tmp_path,"ktrader","req-01",d,
            allowed_consumers=POLICY,allowed_actors=ACTORS)

def test_decision_cannot_predate_result(tmp_path):
    _,_,artifact=completed(tmp_path)
    d=decision(artifact); d["decided_at_utc"]="2026-09-28T11:59:00Z"
    with pytest.raises(ValueError,match="predates"):
        publish_decision(tmp_path,"ktrader","req-01",d,
            allowed_consumers=POLICY,allowed_actors=ACTORS)

def test_same_decision_id_conflict_is_denied(tmp_path):
    _,_,artifact=completed(tmp_path)
    d=decision(artifact)
    publish_decision(tmp_path,"ktrader","req-01",d,
        allowed_consumers=POLICY,allowed_actors=ACTORS)
    changed=copy.deepcopy(d); changed["rationale"]="A different rationale that is also long enough."
    with pytest.raises(ValueError,match="immutable verification decision conflict"):
        publish_decision(tmp_path,"ktrader","req-01",changed,
            allowed_consumers=POLICY,allowed_actors=ACTORS)
