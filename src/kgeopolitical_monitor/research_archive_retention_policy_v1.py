"""Guarded evidence-archive retention policy.

Retention is never automatic. Deletion requires an explicit execution flag and
is permitted only against a verified current archive index. The immutable
archive remains authoritative until a policy execution is explicitly invoked.
"""
from __future__ import annotations
import json, os
from pathlib import Path
from .research_request_v1 import _ID, _utc
from .research_evidence_archive_index_v1 import load_archive_index, maintain_archive_index
from .research_storage_v1 import initialize, lock as _lock

SCHEMA="kgm.research.archive-retention-policy.v1"

def validate_retention_policy(policy):
    fields={"schema_version","consumer_id","keep_latest","min_age_days",
            "max_delete_count","max_delete_fraction"}
    if not isinstance(policy,dict) or set(policy)!=fields:
        raise ValueError("invalid retention policy fields")
    if policy["schema_version"]!=SCHEMA:
        raise ValueError("invalid retention policy schema")
    if not isinstance(policy["consumer_id"],str) or not _ID.fullmatch(policy["consumer_id"]):
        raise ValueError("invalid retention consumer")
    if type(policy["keep_latest"]) is not int or not 1<=policy["keep_latest"]<=100000:
        raise ValueError("invalid keep_latest")
    if type(policy["min_age_days"]) is not int or not 0<=policy["min_age_days"]<=3650:
        raise ValueError("invalid min_age_days")
    if type(policy["max_delete_count"]) is not int or not 1<=policy["max_delete_count"]<=10000:
        raise ValueError("invalid max_delete_count")
    if not isinstance(policy["max_delete_fraction"],(int,float)) or isinstance(policy["max_delete_fraction"],bool):
        raise ValueError("invalid max_delete_fraction")
    if not 0<policy["max_delete_fraction"]<=0.5:
        raise ValueError("invalid max_delete_fraction")
    return policy

def plan_retention(root,policy,*,observed_at_utc):
    validate_retention_policy(policy); now=_utc(observed_at_utc)
    consumer=policy["consumer_id"]
    idx=load_archive_index(root,consumer)
    if idx is None:
        raise ValueError("verified archive index required")
    entries=idx["index"]["entries"]
    n=len(entries)
    keep_floor=max(0,n-policy["keep_latest"])
    candidates=[]
    for item in entries[:keep_floor]:
        age_days=(now-_utc(item["staged_at_utc"])).total_seconds()/86400
        if age_days>=policy["min_age_days"]:
            candidates.append(item["filename"])
    hard_cap=min(policy["max_delete_count"],int(n*policy["max_delete_fraction"]))
    if hard_cap<0: hard_cap=0
    candidates=candidates[:hard_cap]
    return {"consumer_id":consumer,"observed_at_utc":observed_at_utc,
            "archive_entries":n,"keep_latest":policy["keep_latest"],
            "delete_candidates":candidates,"delete_count":len(candidates),
            "execution_allowed":bool(candidates)}

def execute_retention(root,policy,*,observed_at_utc,allow_delete=False):
    root=initialize(root); validate_retention_policy(policy)
    plan=plan_retention(root,policy,observed_at_utc=observed_at_utc)
    if not allow_delete:
        return {**plan,"deleted":[],"executed":False}
    consumer=policy["consumer_id"]
    archive=Path(root)/"evidence_archive"/consumer
    if archive.is_symlink() or not archive.is_dir():
        raise ValueError("invalid retention archive directory")
    fd=_lock(root)
    deleted=[]
    try:
        for name in plan["delete_candidates"]:
            target=archive/name
            if target.is_symlink() or not target.is_file():
                raise ValueError("invalid retention target")
            target.unlink()
            deleted.append(name)
    finally:
        os.close(fd)
    maintain_archive_index(root,consumer,generated_at_utc=observed_at_utc)
    return {**plan,"deleted":deleted,"executed":True}
