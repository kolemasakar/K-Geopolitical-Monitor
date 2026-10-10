"""Immutable archive of first-seen policy-bound observation stages.

Historical replay may use only archived CURRENT snapshots staged no later than the
requested as-of cutoff and whose original request window covers the replay
window. No provider/network access is performed here.
"""
from __future__ import annotations
import hashlib
import json
import os
from pathlib import Path
from .research_storage_v1 import initialize, lock as _lock, canonical_bytes, atomic_replace
from .research_request_v1 import validate_request, historically_available, _utc
from .research_source_policy_v1 import validate_source_policy, source_policy_digest
from .research_observation_stage_v1 import validate_stage

SCHEMA="kgm.research.evidence-archive.v1"

def _archive_dir(root, consumer):
    base=root/"evidence_archive"
    if base.is_symlink():
        raise ValueError("symlink evidence archive root denied")
    base.mkdir(mode=0o700,exist_ok=True)
    path=base/consumer
    if path.is_symlink():
        raise ValueError("symlink evidence archive consumer denied")
    path.mkdir(mode=0o700,exist_ok=True)
    return path

def validate_archive_entry(entry):
    fields={"schema_version","archived_request","source_policy","stage_artifact"}
    if not isinstance(entry,dict) or set(entry)!=fields:
        raise ValueError("unapproved evidence archive fields")
    if entry["schema_version"]!=SCHEMA:
        raise ValueError("invalid evidence archive schema")
    request=entry["archived_request"]; policy=entry["source_policy"]
    validate_request(request); validate_source_policy(request,policy)
    if request["mode"]!="CURRENT":
        raise ValueError("only CURRENT snapshots may seed evidence archive")
    artifact=entry["stage_artifact"]
    if not isinstance(artifact,dict) or set(artifact)!={"stage","sha256"}:
        raise ValueError("invalid archived stage artifact")
    expected=hashlib.sha256(canonical_bytes({"stage":artifact["stage"]})).hexdigest()
    if artifact["sha256"]!=expected:
        raise ValueError("archived stage integrity mismatch")
    stage=validate_stage(artifact["stage"],request=request,source_policy=policy)
    staged=_utc(stage["staged_at_utc"])
    for item in stage["observations"]:
        if item["status"] in {"SUCCESS","PARTIAL"}:
            if _utc(item["available_at_utc"])>staged or _utc(item["published_at_utc"])>staged:
                raise ValueError("archive evidence not available by stage time")
    return entry

def archive_observation_stage(root, consumer, request_id, *, request, source_policy,
                              stage_artifact):
    root=initialize(root)
    if (consumer,request_id)!=(request["consumer_id"],request["request_id"]):
        raise ValueError("evidence archive identity mismatch")
    entry={"schema_version":SCHEMA,"archived_request":request,
           "source_policy":source_policy,"stage_artifact":stage_artifact}
    validate_archive_entry(entry)
    payload={"entry":entry}
    payload["sha256"]=hashlib.sha256(canonical_bytes(payload)).hexdigest()
    encoded=canonical_bytes(payload)
    stage_sha=stage_artifact["sha256"]
    fd=_lock(root)
    try:
        target=_archive_dir(root,consumer)/(stage_sha+".json")
        if target.is_symlink():
            raise ValueError("symlink evidence archive entry denied")
        if target.exists():
            if target.read_bytes()!=encoded:
                raise ValueError("immutable evidence archive conflict")
        else:
            atomic_replace(target,encoded)
        return payload
    finally:
        os.close(fd)

def _load(path):
    if path.is_symlink() or not path.is_file():
        raise ValueError("invalid evidence archive path")
    payload=json.loads(path.read_bytes())
    if not isinstance(payload,dict) or set(payload)!={"entry","sha256"}:
        raise ValueError("invalid evidence archive artifact")
    expected=hashlib.sha256(canonical_bytes({"entry":payload["entry"]})).hexdigest()
    if payload["sha256"]!=expected:
        raise ValueError("evidence archive artifact integrity mismatch")
    validate_archive_entry(payload["entry"])
    return payload

def select_historical_snapshot(root, consumer, *, request, source_policy, max_scan=1000):
    validate_request(request); validate_source_policy(request,source_policy)
    if request["mode"]!="HISTORICAL_AS_OF":
        raise ValueError("historical request required")
    directory=Path(root)/"evidence_archive"/consumer
    if directory.is_symlink():
        raise ValueError("symlink evidence archive denied")
    if not directory.is_dir():
        raise ValueError("no historical evidence archive")
    paths=sorted(directory.glob("*.json"))
    if len(paths)>max_scan:
        raise ValueError("evidence archive scan bound exceeded")
    cutoff=_utc(request["as_of_utc"])
    start=_utc(request["period_start_utc"]); end=_utc(request["period_end_utc"])
    candidates=[]
    for path in paths:
        payload=_load(path); entry=payload["entry"]
        archived=entry["archived_request"]; policy=entry["source_policy"]
        if (archived["consumer_id"],archived["policy_version"]) != (
            request["consumer_id"],request["policy_version"]):
            continue
        if source_policy_digest(archived,policy)!=source_policy_digest(request,source_policy):
            continue
        stage=entry["stage_artifact"]["stage"]
        staged=_utc(stage["staged_at_utc"])
        if staged>cutoff:
            continue
        if _utc(archived["period_start_utc"])>start or _utc(archived["period_end_utc"])<end:
            continue
        if any(item["status"] in {"SUCCESS","PARTIAL"} and
               not historically_available(item,request["as_of_utc"])
               for item in stage["observations"]):
            continue
        candidates.append((staged,path.name,payload))
    if not candidates:
        raise ValueError("no eligible historical snapshot")
    candidates.sort(key=lambda x:(x[0],x[1]))
    return candidates[-1][2]

def rebind_historical_snapshot(snapshot, *, request, source_policy, staged_at_utc):
    if request["mode"]!="HISTORICAL_AS_OF":
        raise ValueError("historical request required")
    entry=snapshot["entry"]; archived_stage=entry["stage_artifact"]["stage"]
    observations=[]
    for item in archived_stage["observations"]:
        rebound=dict(item)
        rebound["request_id"]=request["request_id"]
        observations.append(rebound)
    stage={"schema_version":"kgm.research.observation-stage.v1",
           "request_id":request["request_id"],"consumer_id":request["consumer_id"],
           "request_digest":hashlib.sha256(canonical_bytes(request)).hexdigest(),
           "source_policy_digest":source_policy_digest(request,source_policy),
           "staged_at_utc":staged_at_utc,
           "source_runs":archived_stage["source_runs"],
           "observations":observations}
    validate_stage(stage,request=request,source_policy=source_policy)
    payload={"stage":stage}
    payload["sha256"]=hashlib.sha256(canonical_bytes(payload)).hexdigest()
    return payload
