"""Immutable durable staging of normalized source observations."""
from __future__ import annotations
import hashlib
import json
import os
from .research_storage_v1 import initialize, lock as _lock, canonical_bytes, atomic_replace
from .research_request_v1 import validate_request, _ID, _utc
from .research_source_adapter_v1 import validate_source_observation
from .research_source_policy_v1 import validate_source_policy, source_policy_digest

SCHEMA="kgm.research.observation-stage.v1"
RUN_STATUSES={"OBSERVED","EMPTY","DEGRADED"}

def _stage_dir(root, consumer):
    base=root/"observation_stage"
    if base.is_symlink():
        raise ValueError("symlink observation stage root denied")
    base.mkdir(mode=0o700,exist_ok=True)
    path=base/consumer
    if path.is_symlink():
        raise ValueError("symlink observation stage consumer denied")
    path.mkdir(mode=0o700,exist_ok=True)
    return path

def validate_stage(stage, *, request, source_policy):
    validate_request(request)
    validate_source_policy(request,source_policy)
    fields={"schema_version","request_id","consumer_id","request_digest",
            "source_policy_digest","staged_at_utc","source_runs","observations"}
    if not isinstance(stage,dict) or set(stage)!=fields:
        raise ValueError("unapproved observation stage fields")
    if stage["schema_version"]!=SCHEMA:
        raise ValueError("invalid observation stage schema")
    if (stage["request_id"],stage["consumer_id"]) != (
        request["request_id"],request["consumer_id"]):
        raise ValueError("observation stage correlation mismatch")
    expected_request=hashlib.sha256(canonical_bytes(request)).hexdigest()
    if stage["request_digest"]!=expected_request:
        raise ValueError("observation stage request digest mismatch")
    if stage["source_policy_digest"]!=source_policy_digest(request,source_policy):
        raise ValueError("observation stage source policy digest mismatch")
    _utc(stage["staged_at_utc"])
    runs=stage["source_runs"]
    if not isinstance(runs,list) or not 1<=len(runs)<=100:
        raise ValueError("invalid source run ledger")
    run_fields={"source_id","status","observation_count"}
    seen=set()
    for run in runs:
        if not isinstance(run,dict) or set(run)!=run_fields:
            raise ValueError("invalid source run")
        sid=run["source_id"]
        if not isinstance(sid,str) or not _ID.fullmatch(sid) or sid in seen:
            raise ValueError("invalid/duplicate source run")
        seen.add(sid)
        if run["status"] not in RUN_STATUSES:
            raise ValueError("invalid source run status")
        if type(run["observation_count"]) is not int or not 0<=run["observation_count"]<=100:
            raise ValueError("invalid source run observation count")
        if run["status"]=="EMPTY" and run["observation_count"]!=0:
            raise ValueError("empty source run carries observations")
        if run["status"]!="EMPTY" and run["observation_count"]==0:
            raise ValueError("non-empty source run missing observations")
    required=set(source_policy["required_source_ids"])
    if not required <= seen:
        raise ValueError("observation stage missing required source run")
    allowed=required|set(source_policy["optional_source_ids"])
    if not seen <= allowed:
        raise ValueError("observation stage contains unapproved source run")
    observations=stage["observations"]
    if not isinstance(observations,list) or len(observations)>source_policy["max_observations"]:
        raise ValueError("observation stage batch unbounded")
    counts={sid:0 for sid in seen}
    for item in observations:
        validate_source_observation(request,item)
        if item["source_id"] not in seen:
            raise ValueError("observation without source run")
        counts[item["source_id"]]+=1
    for run in runs:
        if counts[run["source_id"]]!=run["observation_count"]:
            raise ValueError("source run observation count mismatch")
    return stage

def stage_observations(root, consumer, request_id, *, request, source_policy,
                       source_runs, observations, staged_at_utc):
    root=initialize(root)
    validate_request(request)
    if (consumer,request_id)!=(request["consumer_id"],request["request_id"]):
        raise ValueError("observation stage identity mismatch")
    stage={"schema_version":SCHEMA,"request_id":request_id,"consumer_id":consumer,
           "request_digest":hashlib.sha256(canonical_bytes(request)).hexdigest(),
           "source_policy_digest":source_policy_digest(request,source_policy),
           "staged_at_utc":staged_at_utc,"source_runs":source_runs,
           "observations":observations}
    validate_stage(stage,request=request,source_policy=source_policy)
    payload={"stage":stage}
    payload["sha256"]=hashlib.sha256(canonical_bytes(payload)).hexdigest()
    encoded=canonical_bytes(payload)
    fd=_lock(root)
    try:
        target=_stage_dir(root,consumer)/(request_id+".json")
        if target.is_symlink():
            raise ValueError("symlink observation stage denied")
        if target.exists():
            if target.read_bytes()!=encoded:
                raise ValueError("immutable observation stage conflict")
        else:
            atomic_replace(target,encoded)
        return payload
    finally:
        os.close(fd)

def load_observation_stage(root, consumer, request_id, *, request, source_policy):
    path=root/"observation_stage"/consumer/(request_id+".json")
    if path.is_symlink() or not path.is_file():
        return None
    artifact=json.loads(path.read_bytes())
    if not isinstance(artifact,dict) or set(artifact)!={"stage","sha256"}:
        raise ValueError("invalid observation stage artifact")
    expected=hashlib.sha256(canonical_bytes({"stage":artifact["stage"]})).hexdigest()
    if artifact["sha256"]!=expected:
        raise ValueError("observation stage integrity mismatch")
    validate_stage(artifact["stage"],request=request,source_policy=source_policy)
    return artifact
