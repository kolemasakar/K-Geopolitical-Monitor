"""Policy-bound durable research worker with immutable observation staging."""
from __future__ import annotations
import copy
import hashlib
from .research_typed_workflow_v1 import begin_processing, publish_and_complete
from .research_source_adapter_v1 import normalize_observations
from .research_source_policy_v1 import validate_adapter_mapping, validate_source_policy
from .research_observation_stage_v1 import stage_observations, load_observation_stage
from .research_evidence_archive_v1 import archive_observation_stage, rebind_historical_snapshot
from .research_evidence_archive_index_v1 import select_historical_snapshot_fast, maintain_archive_index
from .research_worker_v1 import _build_records, _select_records
from .research_corroboration_v1 import build_corroboration_report
from .research_storage_v1 import canonical_bytes

def _fetch_and_normalize(request, source_policy, adapters):
    all_observations=[]
    source_runs=[]
    for source_id in sorted(adapters):
        produced=adapters[source_id](copy.deepcopy(request))
        if isinstance(produced,list):
            items=produced
        else:
            items=[produced]
        if len(items)+len(all_observations)>source_policy["max_observations"]:
            raise ValueError("source observation bound exceeded")
        for item in items:
            if not isinstance(item,dict) or item.get("source_id")!=source_id:
                raise ValueError("adapter emitted mismatched source identity")
        if items:
            statuses={x.get("status") for x in items}
            run_status=("DEGRADED" if statuses & {"PARTIAL","UNAVAILABLE","INVALID"}
                        else "OBSERVED")
            all_observations.extend(items)
        else:
            run_status="EMPTY"
        source_runs.append({"source_id":source_id,"status":run_status,
                            "observation_count":len(items)})
    normalized=(normalize_observations(request,all_observations)
                if all_observations else [])
    return source_runs,normalized

def execute_policy_bound(root, consumer, request_id, *, request, allowed_consumers,
                         source_policy, adapters, processing_at_utc, staged_at_utc,
                         completed_at_utc, producer_snapshot_id="policy-worker-v2",
                         after_stage=None):
    validate_source_policy(request,source_policy)
    if request["mode"]=="CURRENT":
        validate_adapter_mapping(request,source_policy,adapters)
    else:
        if adapters not in ({},None):
            raise ValueError("historical replay forbids live adapters")
    if (consumer,request_id)!=(request["consumer_id"],request["request_id"]):
        raise ValueError("worker request identity mismatch")

    begin_processing(root,consumer,request_id,allowed_consumers=allowed_consumers,
                     at_utc=processing_at_utc)

    staged=load_observation_stage(root,consumer,request_id,request=request,
                                  source_policy=source_policy)
    if staged is None:
        if request["mode"]=="CURRENT":
            source_runs,observations=_fetch_and_normalize(request,source_policy,adapters)
            staged=stage_observations(root,consumer,request_id,request=request,
                                      source_policy=source_policy,source_runs=source_runs,
                                      observations=observations,staged_at_utc=staged_at_utc)
        else:
            snapshot,_selection_path=select_historical_snapshot_fast(root,consumer,request=request,
                                                source_policy=source_policy)
            rebound=rebind_historical_snapshot(snapshot,request=request,
                                               source_policy=source_policy,
                                               staged_at_utc=staged_at_utc)
            rstage=rebound["stage"]
            staged=stage_observations(root,consumer,request_id,request=request,
                                      source_policy=source_policy,
                                      source_runs=rstage["source_runs"],
                                      observations=rstage["observations"],
                                      staged_at_utc=staged_at_utc)
    if request["mode"]=="CURRENT":
        archive_observation_stage(root,consumer,request_id,request=request,
                                  source_policy=source_policy,stage_artifact=staged)
        maintain_archive_index(root,consumer,generated_at_utc=staged_at_utc)
    if after_stage is not None:
        after_stage(staged)

    stage=staged["stage"]
    observations=stage["observations"]
    usable=[x for x in observations if x["status"] in {"SUCCESS","PARTIAL"}]
    unhealthy_obs=[x for x in observations
                   if x["status"] in {"PARTIAL","UNAVAILABLE","INVALID"}]
    required_sources=set(source_policy["required_source_ids"])\n    degraded_runs=[x for x in stage["source_runs"]\n                   if x["status"]=="DEGRADED" or\n                   (x["status"]=="EMPTY" and x["source_id"] in required_sources)]

    all_records,disagreement=_build_records(usable)
    records=_select_records(all_records,request["max_results"])
    corroboration=build_corroboration_report(observations)

    complete=bool(records) and not unhealthy_obs and not degraded_runs and not disagreement
    status="COMPLETE" if complete else "PARTIAL"
    if not degraded_runs and not unhealthy_obs:
        source_health="HEALTHY"
    else:
        source_health="DEGRADED" if records else "UNAVAILABLE"
    result={"schema_version":"kgm.research.result.v2","request_id":request_id,
        "consumer_id":consumer,
        "result_id":"result-"+hashlib.sha256(canonical_bytes({
            "stage_sha256":staged["sha256"],"corroboration":corroboration
        })).hexdigest()[:24],
        "generated_at_utc":completed_at_utc,
        "producer_snapshot_id":producer_snapshot_id,
        "policy_version":request["policy_version"],
        "research_status":status,
        "coverage":"COMPLETE" if complete else "PARTIAL",
        "source_health":source_health,
        "records":records,
        "corroboration":corroboration}
    return publish_and_complete(root,consumer,request_id,result,
                                allowed_consumers=allowed_consumers,
                                at_utc=completed_at_utc)
