"""Explicit source-contribution semantics for typed research results."""
from __future__ import annotations

CONTRIBUTION_STATUSES={"CONTRIBUTED","EMPTY","DEGRADED"}

def build_source_contributions(source_policy, source_runs, observations, corroboration):
    required=set(source_policy["required_source_ids"])
    obs_by_source={}
    for item in observations:
        obs_by_source.setdefault(item["source_id"],[]).append(item)
    corr_counts={}
    for group in corroboration:
        for source_id in group["source_ids"]:
            corr_counts[source_id]=corr_counts.get(source_id,0)+1
    out=[]
    for run in sorted(source_runs,key=lambda x:x["source_id"]):
        sid=run["source_id"]
        items=obs_by_source.get(sid,[])
        evidence_count=sum(x.get("status") in {"SUCCESS","PARTIAL"} for x in items)
        if run["status"]=="EMPTY":
            status="EMPTY"
        elif run["status"]=="DEGRADED":
            status="DEGRADED"
        else:
            status="CONTRIBUTED" if evidence_count else "DEGRADED"
        out.append({"source_id":sid,"required":sid in required,
                    "run_status":run["status"],
                    "observation_count":run["observation_count"],
                    "evidence_observation_count":evidence_count,
                    "corroboration_group_count":corr_counts.get(sid,0),
                    "contribution_status":status})
    return out

def summarize_completeness(result_status, contributions):
    required=[x for x in contributions if x["required"]]
    all_invoked=bool(required)
    all_healthy=all(x["run_status"] in {"OBSERVED","EMPTY"} for x in required)
    all_contributed=all(x["contribution_status"]=="CONTRIBUTED" for x in required)
    any_empty=any(x["contribution_status"]=="EMPTY" for x in required)
    return {"semantics_version":"kgm.completeness.v2",
            "portfolio_execution_complete":result_status=="COMPLETE",
            "all_required_sources_invoked":all_invoked,
            "all_required_sources_healthy":all_healthy,
            "all_required_sources_contributed":all_contributed,
            "required_source_empty_present":any_empty,
            "complete_does_not_imply_all_sources_contributed":True}
