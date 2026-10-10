import copy
import pytest
from kgeopolitical_monitor.research_generic_identity_v1 import (
    generic_event_identity,generic_claim_signature)
from kgeopolitical_monitor.research_worker_v1 import _build_records
from kgeopolitical_monitor.research_origin_assessment_v1 import assess_origin_groups
from kgeopolitical_monitor.research_source_adapter_v1 import normalize_observations
from kgeopolitical_monitor.research_typed_workflow_v1 import accept_request
from kgeopolitical_monitor.research_worker_v2 import execute_policy_bound
from kgeopolitical_monitor.research_observation_stage_v1 import load_observation_stage
from test_research_worker_v2 import accepted,policy,obs,execute,historical_from
from test_research_completion_v1 import POLICY

BASE_EVENT={"family":"DIPLOMATIC","event_date_utc":"2026-10-10T00:00:00Z",
 "action_key":"MEET","actor_keys":["actor-a","actor-b"],"target_keys":[],
 "subject_key":"subject-a","location_key":"city-a"}
CLAIM_OK={"claim_type":"STATUS","value_keys":["meeting-held"],"unit_key":None}
CLAIM_ALT={"claim_type":"STATUS","value_keys":["meeting-cancelled"],"unit_key":None}

def item(source,oid,summary,event,claim,origin):
    return {"schema_version":"kgm.source.observation.v1","request_id":"req-01",
      "source_id":source,"observation_id":oid,"status":"SUCCESS",
      "observed_at_utc":"2026-09-28T12:02:10Z",
      "published_at_utc":"2026-09-02T11:00:00Z",
      "available_at_utc":"2026-09-02T11:30:00Z",
      "public_url":f"https://{source}.example/{oid}","summary":summary,
      "error_code":None,"origin_group":origin,
      "event_descriptor":event,"claim_descriptor":claim,
      "event_identity":generic_event_identity(event),
      "claim_signature":generic_claim_signature(claim)}

def test_false_merge_resistance_different_subjects_do_not_merge():
    e1=copy.deepcopy(BASE_EVENT)
    e2=copy.deepcopy(BASE_EVENT);e2["subject_key"]="subject-b"
    records,disagreement=_build_records([
        item("source-a","a1","first",e1,CLAIM_OK,"origin-a"),
        item("source-b","b1","second",e2,CLAIM_OK,"origin-b")])
    assert len(records)==2
    assert disagreement is False
    assert records[0]["record_id"]!=records[1]["record_id"]

def test_false_split_resistance_same_descriptor_different_wording_merges():
    records,disagreement=_build_records([
        item("source-a","a1","leaders met in the capital",BASE_EVENT,CLAIM_OK,"origin-a"),
        item("source-b","b1","bilateral talks took place",BASE_EVENT,CLAIM_OK,"origin-b")])
    assert len(records)==1
    assert len(records[0]["evidence"])==2
    assert records[0]["verification"]=="UNVERIFIED"
    assert disagreement is False

def test_claim_disagreement_never_silently_merges_or_verifies():
    records,disagreement=_build_records([
        item("source-a","a1","meeting occurred",BASE_EVENT,CLAIM_OK,"origin-a"),
        item("source-b","b1","meeting cancelled",BASE_EVENT,CLAIM_ALT,"origin-b")])
    assert disagreement is True
    assert len(records)==2
    assert {r["verification"] for r in records}=={"DISPUTED"}
    assert all(r["contradictions"] for r in records)

def test_same_origin_paths_do_not_receive_independence_credit():
    result=assess_origin_groups([
        {"origin_group":"origin-a"},{"origin_group":"origin-a"}])
    assert result["assessment"]=="SAME_ORIGIN"
    assert result["independent_origin_credit"] is False

def test_distinct_origins_do_not_auto_verify():
    result=assess_origin_groups([
        {"origin_group":"origin-a"},{"origin_group":"origin-b"}])
    assert result["assessment"]=="DISTINCT_ORIGIN"
    assert result["independent_origin_credit"] is True
    records,_=_build_records([
        item("source-a","a1","first",BASE_EVENT,CLAIM_OK,"origin-a"),
        item("source-b","b1","second",BASE_EVENT,CLAIM_OK,"origin-b")])
    assert records[0]["verification"]=="UNVERIFIED"

def test_duplicate_publication_path_cannot_masquerade_as_two_evidence_items():
    from test_research_request_v1 import sample
    req=sample()
    a=item("source-a","a1","first",BASE_EVENT,CLAIM_OK,"origin-a")
    b=item("source-b","b1","second",BASE_EVENT,CLAIM_OK,"origin-b")
    a["request_id"]=req["request_id"];b["request_id"]=req["request_id"]
    b["public_url"]=a["public_url"]
    with pytest.raises(ValueError,match="duplicate evidence fingerprint"):
        normalize_observations(req,[a,b])

def test_required_source_unavailable_prevents_false_complete(tmp_path):
    req=accepted(tmp_path);p=policy(req)
    artifact=execute(tmp_path,req,p,{"source-a":obs("source-a","a1"),
                                    "source-b":obs("source-b","b1","UNAVAILABLE")})
    assert artifact["result"]["research_status"]=="PARTIAL"
    assert artifact["result"]["coverage"]=="PARTIAL"
    assert artifact["result"]["source_health"]=="DEGRADED"

def test_missing_required_adapter_denied_before_processing_quality_gate(tmp_path):
    req=accepted(tmp_path);p=policy(req)
    with pytest.raises(ValueError,match="required source adapter missing"):
        execute(tmp_path,req,p,{"source-a":obs("source-a","a1")})

def test_archive_backed_historical_replay_is_semantically_reproducible(tmp_path):
    current=accepted(tmp_path);p=policy(current)
    execute(tmp_path,current,p,{"source-a":obs("source-a","a1"),
                                "source-b":obs("source-b","b1")})
    results=[]
    for rid,accepted_at,processing,staged,completed in [
        ("hist-qa-1","2026-09-28T12:10:01Z","2026-09-28T12:10:02Z","2026-09-28T12:10:03Z","2026-09-28T12:10:04Z"),
        ("hist-qa-2","2026-09-28T12:11:01Z","2026-09-28T12:11:02Z","2026-09-28T12:11:03Z","2026-09-28T12:11:04Z")]:
        hist=historical_from(current,request_id=rid,as_of="2026-09-28T12:03:00Z")
        accept_request(tmp_path,hist,allowed_consumers=POLICY,accepted_at_utc=accepted_at)
        hp=policy(hist)
        art=execute_policy_bound(tmp_path,"ktrader",rid,request=hist,
            allowed_consumers=POLICY,source_policy=hp,adapters={},
            processing_at_utc=processing,staged_at_utc=staged,completed_at_utc=completed)
        stage=load_observation_stage(tmp_path,"ktrader",rid,request=hist,source_policy=hp)
        results.append((art["result"]["records"],stage["stage"]["observations"]))
    assert results[0][0]==results[1][0]
    normalize=lambda xs:[{k:v for k,v in x.items() if k!="request_id"} for x in xs]
    assert normalize(results[0][1])==normalize(results[1][1])
