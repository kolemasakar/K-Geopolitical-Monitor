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

def observation(req,source,oid,summary,url,status="SUCCESS"):
    ok=status in {"SUCCESS","PARTIAL"}
    return {"schema_version":"kgm.source.observation.v1","request_id":req["request_id"],
      "source_id":source,"observation_id":oid,"status":status,
      "observed_at_utc":"2026-09-28T12:02:00Z",
      "published_at_utc":"2026-09-28T11:00:00Z" if ok else None,
      "available_at_utc":"2026-09-28T12:02:00Z" if ok else None,
      "public_url":url if ok else None,"summary":summary if ok else None,
      "error_code":None if ok else "RATE_LIMITED"}

def test_cross_source_same_claim_deduplicates_and_merges_evidence(tmp_path):
    req=accepted(tmp_path)
    def a(r): return observation(r,"source-a","event-1","same claim","https://a.example/event")
    def b(r): return observation(r,"source-b","event-1","same claim","https://b.example/event")
    artifact=execute_deterministic(tmp_path,"ktrader","req-01",request=req,
        allowed_consumers=POLICY,adapters=[a,b],
        processing_at_utc="2026-09-28T12:02:00Z",completed_at_utc="2026-09-28T12:04:00Z")
    result=artifact["result"]
    assert result["research_status"]=="COMPLETE"
    assert len(result["records"])==1
    assert len(result["records"][0]["evidence"])==2

def test_same_claim_key_with_conflicting_summaries_is_disputed_partial(tmp_path):
    req=accepted(tmp_path)
    def a(r): return observation(r,"source-a","event-1","magnitude 5.0","https://a.example/event")
    def b(r): return observation(r,"source-b","event-1","magnitude 6.0","https://b.example/event")
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
    assert url.startswith("https://earthquake.usgs.gov/") and "format=geojson" in url
    payload={"features":[{"id":"us123","properties":{
        "title":"M 5.1 - Test Region","url":"https://earthquake.usgs.gov/earthquakes/eventpage/us123",
        "updated":1789992000000}}]}
    items=usgs_fetch(req,observed_at_utc="2026-09-28T12:02:00Z",http_get=lambda _:payload)
    assert items[0]["source_id"]=="usgs-earthquake"
    assert items[0]["status"]=="SUCCESS"
    assert items[0]["published_at_utc"].endswith("Z")
