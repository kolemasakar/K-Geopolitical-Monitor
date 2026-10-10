import copy
import pytest
from kgeopolitical_monitor.research_typed_result_v1 import validate_typed_result
from kgeopolitical_monitor.research_typed_workflow_v1 import accept_request
from kgeopolitical_monitor.research_worker_v2 import execute_policy_bound
from test_research_worker_v2 import accepted,policy,obs
from test_research_completion_v1 import POLICY

def run(root, adapters):
    req=accepted(root)
    p=policy(req)
    return req,execute_policy_bound(root,"ktrader","req-01",request=req,
        allowed_consumers=POLICY,source_policy=p,adapters=adapters,
        processing_at_utc="2026-09-28T12:02:00Z",
        staged_at_utc="2026-09-28T12:03:00Z",
        completed_at_utc="2026-09-28T12:04:00Z")

def test_result_v3_exposes_required_source_contributions(tmp_path):
    req,artifact=run(tmp_path,{"source-a":obs("source-a","a1"),
                               "source-b":obs("source-b","b1")})
    result=artifact["result"]
    assert result["schema_version"]=="kgm.research.result.v3"
    assert [x["contribution_status"] for x in result["source_contributions"]]==["CONTRIBUTED","CONTRIBUTED"]
    sem=result["completeness_semantics"]
    assert sem["portfolio_execution_complete"] is True
    assert sem["all_required_sources_contributed"] is True
    assert sem["required_source_empty_present"] is False
    assert sem["complete_does_not_imply_all_sources_contributed"] is True
    validate_typed_result(req,result)

def test_complete_with_healthy_empty_is_explicit_not_universal_corroboration(tmp_path):
    req,artifact=run(tmp_path,{"source-a":obs("source-a","a1"),
                               "source-b":lambda _req:[]})
    result=artifact["result"]
    assert result["research_status"]=="COMPLETE"
    sem=result["completeness_semantics"]
    assert sem["portfolio_execution_complete"] is True
    assert sem["all_required_sources_healthy"] is True
    assert sem["all_required_sources_contributed"] is False
    assert sem["required_source_empty_present"] is True
    by_source={x["source_id"]:x for x in result["source_contributions"]}
    assert by_source["source-b"]["contribution_status"]=="EMPTY"

def test_degraded_required_source_is_explicit_in_v3(tmp_path):
    req,artifact=run(tmp_path,{"source-a":obs("source-a","a1"),
                               "source-b":obs("source-b","b1","UNAVAILABLE")})
    result=artifact["result"]
    assert result["research_status"]=="PARTIAL"
    sem=result["completeness_semantics"]
    assert sem["all_required_sources_healthy"] is False
    by_source={x["source_id"]:x for x in result["source_contributions"]}
    assert by_source["source-b"]["contribution_status"]=="DEGRADED"

def test_validator_rejects_false_all_sources_contributed_claim(tmp_path):
    req,artifact=run(tmp_path,{"source-a":obs("source-a","a1"),
                               "source-b":lambda _req:[]})
    result=copy.deepcopy(artifact["result"])
    result["completeness_semantics"]["all_required_sources_contributed"]=True
    with pytest.raises(ValueError,match="contribution semantics mismatch"):
        validate_typed_result(req,result)
