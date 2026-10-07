import pytest
from kgeopolitical_monitor.research_typed_workflow_v1 import accept_request
from kgeopolitical_monitor.research_worker_v1 import execute_deterministic
from kgeopolitical_monitor.research_source_usgs_v1 import build_query as usgs_query, fetch as usgs_fetch
from kgeopolitical_monitor.research_source_gdelt_v1 import fetch as gdelt_fetch
from kgeopolitical_monitor.research_source_cooldown_v1 import record_cooldown
from test_research_typed_result_v1 import typed
from test_research_completion_v1 import POLICY

def current_request():
    req,_=typed()
    req["mode"]="CURRENT"; req.pop("as_of_utc")
    return req

def accepted(root):
    req=current_request()
    accept_request(root,req,allowed_consumers=POLICY,
                   accepted_at_utc="2026-09-28T12:01:00Z")
    return req

def observation(req,source,oid,summary,url,status="SUCCESS",event_identity=None,claim_signature=None):
    ok=status in {"SUCCESS","PARTIAL"}
    return {"schema_version":"kgm.source.observation.v1","request_id":req["request_id"],
      "source_id":source,"observation_id":oid,"status":status,
      "observed_at_utc":"2026-09-28T12:02:00Z",
      "published_at_utc":"2026-09-28T11:00:00Z" if ok else None,
      "available_at_utc":"2026-09-28T12:02:00Z" if ok else None,
      "public_url":url if ok else None,"summary":summary if ok else None,
      "error_code":None if ok else "RATE_LIMITED","event_identity":event_identity if ok else None,
      "claim_signature":claim_signature if ok else None}

def test_cross_source_same_claim_deduplicates_and_merges_evidence(tmp_path):
    req=accepted(tmp_path)
    def a(r): return observation(r,"source-a","a-001","same claim","https://a.example/event",event_identity="eq-20260928T110000-n1000-e02000",claim_signature="mag-50")
    def b(r): return observation(r,"source-b","b-991","same claim","https://b.example/event",event_identity="eq-20260928T110000-n1000-e02000",claim_signature="mag-50")
    artifact=execute_deterministic(tmp_path,"ktrader","req-01",request=req,
        allowed_consumers=POLICY,adapters=[a,b],
        processing_at_utc="2026-09-28T12:02:00Z",completed_at_utc="2026-09-28T12:04:00Z")
    result=artifact["result"]
    assert result["research_status"]=="COMPLETE"
    assert len(result["records"])==1
    assert len(result["records"][0]["evidence"])==2

def test_same_claim_key_with_conflicting_summaries_is_disputed_partial(tmp_path):
    req=accepted(tmp_path)
    def a(r): return observation(r,"source-a","a-001","magnitude 5.0","https://a.example/event",event_identity="eq-20260928T110000-n1000-e02000",claim_signature="mag-50")
    def b(r): return observation(r,"source-b","b-991","magnitude 6.0","https://b.example/event",event_identity="eq-20260928T110000-n1000-e02000",claim_signature="mag-60")
    artifact=execute_deterministic(tmp_path,"ktrader","req-01",request=req,
        allowed_consumers=POLICY,adapters=[a,b],
        processing_at_utc="2026-09-28T12:02:00Z",completed_at_utc="2026-09-28T12:04:00Z")
    result=artifact["result"]
    assert result["research_status"]=="PARTIAL"
    assert result["source_health"]=="DEGRADED"
    assert len(result["records"])==2
    assert all(x["verification"]=="DISPUTED" and x["contradictions"] for x in result["records"])

def test_mixed_success_and_unavailable_is_partial(tmp_path):
    req=accepted(tmp_path)
    def gdacs(r): return observation(r,"gdacs-events","gdacs-1","Flood event","https://gdacs.example/event")
    def gdelt(r): return observation(r,"gdelt-doc-v2","gdelt-cooldown",None,None,"UNAVAILABLE")
    def usgs(r): return observation(r,"usgs-earthquake","usgs-1","Earthquake event","https://usgs.example/event")
    artifact=execute_deterministic(tmp_path,"ktrader","req-01",request=req,
        allowed_consumers=POLICY,adapters=[gdacs,gdelt,usgs],
        processing_at_utc="2026-09-28T12:02:00Z",completed_at_utc="2026-09-28T12:04:00Z")
    result=artifact["result"]
    assert result["research_status"]=="PARTIAL"
    assert result["coverage"]=="PARTIAL"
    assert result["source_health"]=="DEGRADED"
    assert len(result["records"])==2

def test_gdelt_active_cooldown_skips_transport(tmp_path):
    req=current_request(); calls=[]
    record_cooldown(tmp_path,"gdelt-doc-v2",until_utc="2026-09-28T13:00:00Z",reason="RATE_LIMITED")
    items=gdelt_fetch(req,query="Ukraine",observed_at_utc="2026-09-28T12:10:00Z",
        http_get=lambda _: calls.append(1),cooldown_root=tmp_path)
    assert calls==[]
    assert items[0]["status"]=="UNAVAILABLE"
    assert items[0]["error_code"]=="RATE_LIMITED"

def test_usgs_query_and_fixture_normalize():
    req=current_request()
    url=usgs_query(req)
    assert url.startswith("https://earthquake.usgs.gov/") and "format=geojson" in url and "minmagnitude=4.5" in url
    payload={"features":[{"id":"us123","properties":{
        "title":"M 5.1 - Test Region","url":"https://earthquake.usgs.gov/earthquakes/eventpage/us123",
        "updated":1789992000000,"time":1789991400000,"mag":5.1},
        "geometry":{"type":"Point","coordinates":[20.0,10.0,12.0]}}]}
    items=usgs_fetch(req,observed_at_utc="2026-09-28T12:02:00Z",http_get=lambda _:payload)
    assert items[0]["source_id"]=="usgs-earthquake"
    assert items[0]["status"]=="SUCCESS"
    assert items[0]["published_at_utc"].endswith("Z")
    assert items[0]["event_identity"].startswith("eq-")

def test_result_budget_is_balanced_across_healthy_sources(tmp_path):
    req=accepted(tmp_path); req["max_results"]=4
    # Re-admit with the modified request under a fresh root.
    fresh=tmp_path/"balanced"; fresh.mkdir()
    accept_request(fresh,req,allowed_consumers=POLICY,
                   accepted_at_utc="2026-09-28T12:01:00Z")
    def source(name,prefix):
        def run(r):
            return [observation(r,name,f"{prefix}-{n}",f"{name} event {n}",f"https://{name}.example/{n}") for n in range(4)]
        return run
    artifact=execute_deterministic(fresh,"ktrader","req-01",request=req,
        allowed_consumers=POLICY,adapters=[source("source-a","a"),source("source-b","b")],
        processing_at_utc="2026-09-28T12:02:00Z",completed_at_utc="2026-09-28T12:04:00Z")
    seen={e["source_id"] for rec in artifact["result"]["records"] for e in rec["evidence"]}
    assert seen=={"source-a","source-b"}


def test_same_native_observation_id_without_structured_identity_does_not_cross_merge(tmp_path):
    req=accepted(tmp_path)
    def a(r): return observation(r,"source-a","shared-native-id","claim A","https://a.example/event")
    def b(r): return observation(r,"source-b","shared-native-id","claim A","https://b.example/event")
    artifact=execute_deterministic(tmp_path,"ktrader","req-01",request=req,
        allowed_consumers=POLICY,adapters=[a,b],
        processing_at_utc="2026-09-28T12:02:00Z",completed_at_utc="2026-09-28T12:04:00Z")
    assert len(artifact["result"]["records"])==2


def test_same_event_same_claim_signature_merges_despite_different_wording(tmp_path):
    req=accepted(tmp_path)
    identity="eq-20260928T110000-n1000-e02000"
    def a(r): return observation(r,"source-a","a-1","Earthquake in Testland","https://a.example/event",
                                 event_identity=identity,claim_signature="mag-50")
    def b(r): return observation(r,"source-b","b-9","M 5.0 - Test Region","https://b.example/event",
                                 event_identity=identity,claim_signature="mag-50")
    artifact=execute_deterministic(tmp_path,"ktrader","req-01",request=req,
        allowed_consumers=POLICY,adapters=[a,b],
        processing_at_utc="2026-09-28T12:02:00Z",completed_at_utc="2026-09-28T12:04:00Z")
    record=artifact["result"]["records"][0]
    assert artifact["result"]["research_status"]=="COMPLETE"
    assert record["record_id"]==identity
    assert len(record["evidence"])==2
