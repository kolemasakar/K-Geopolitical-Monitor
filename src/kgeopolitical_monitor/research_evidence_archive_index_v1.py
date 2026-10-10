"""Rebuildable index and non-destructive retention planning for evidence archive.

The archive remains authoritative. The index is a cache: selection verifies that
its filename manifest matches the archive directory before use.
"""
from __future__ import annotations
import hashlib
import json
import os
from pathlib import Path
from .research_request_v1 import _ID, _utc, historically_available
from .research_storage_v1 import initialize, lock as _lock, canonical_bytes, atomic_replace
from .research_source_policy_v1 import validate_source_policy, source_policy_digest
from .research_evidence_archive_v1 import _load

SCHEMA="kgm.research.evidence-archive-index.v1"

def _index_path(root,consumer):
    if not isinstance(consumer,str) or not _ID.fullmatch(consumer):
        raise ValueError("invalid archive index consumer")
    base=Path(root)/"evidence_archive_index"
    if base.is_symlink():
        raise ValueError("symlink evidence archive index denied")
    base.mkdir(mode=0o700,exist_ok=True)
    return base/(consumer+".json")

def _metadata(payload,path):
    entry=payload["entry"]; req=entry["archived_request"]
    stage=entry["stage_artifact"]["stage"]
    available=[_utc(x["available_at_utc"]) for x in stage["observations"]
               if x["status"] in {"SUCCESS","PARTIAL"}]
    max_available=(max(available).strftime("%Y-%m-%dT%H:%M:%SZ")
                   if available else None)
    return {"filename":path.name,
            "stage_sha256":entry["stage_artifact"]["sha256"],
            "staged_at_utc":stage["staged_at_utc"],
            "period_start_utc":req["period_start_utc"],
            "period_end_utc":req["period_end_utc"],
            "policy_version":req["policy_version"],
            "source_policy_digest":source_policy_digest(req,entry["source_policy"]),
            "max_available_at_utc":max_available}

def validate_archive_index(index,consumer):
    fields={"schema_version","consumer_id","generated_at_utc","entries"}
    if not isinstance(index,dict) or set(index)!=fields:
        raise ValueError("unapproved evidence archive index fields")
    if index["schema_version"]!=SCHEMA or index["consumer_id"]!=consumer:
        raise ValueError("evidence archive index correlation mismatch")
    _utc(index["generated_at_utc"])
    entries=index["entries"]
    if not isinstance(entries,list) or len(entries)>100000:
        raise ValueError("evidence archive index unbounded")
    ef={"filename","stage_sha256","staged_at_utc","period_start_utc",
        "period_end_utc","policy_version","source_policy_digest",
        "max_available_at_utc"}
    seen=set()
    previous=None
    for item in entries:
        if not isinstance(item,dict) or set(item)!=ef:
            raise ValueError("invalid archive index entry")
        if (not isinstance(item["filename"],str) or not item["filename"].endswith(".json")
            or "/" in item["filename"] or item["filename"] in seen):
            raise ValueError("invalid/duplicate archive index filename")
        seen.add(item["filename"])
        for field in ("staged_at_utc","period_start_utc","period_end_utc"):
            _utc(item[field])
        if item["max_available_at_utc"] is not None:
            _utc(item["max_available_at_utc"])
        for field in ("stage_sha256","policy_version","source_policy_digest"):
            if not isinstance(item[field],str) or not item[field]:
                raise ValueError("invalid archive index metadata")
        key=(item["staged_at_utc"],item["filename"])
        if previous is not None and key<previous:
            raise ValueError("archive index not canonically sorted")
        previous=key
    return index

def rebuild_archive_index(root,consumer,*,generated_at_utc,max_entries=100000):
    root=initialize(root); _utc(generated_at_utc)
    archive=Path(root)/"evidence_archive"/consumer
    if archive.is_symlink():
        raise ValueError("symlink evidence archive denied")
    paths=sorted(archive.glob("*.json")) if archive.is_dir() else []
    if len(paths)>max_entries:
        raise ValueError("archive index rebuild bound exceeded")
    entries=[]
    for path in paths:
        entries.append(_metadata(_load(path),path))
    entries.sort(key=lambda x:(x["staged_at_utc"],x["filename"]))
    index={"schema_version":SCHEMA,"consumer_id":consumer,
           "generated_at_utc":generated_at_utc,"entries":entries}
    validate_archive_index(index,consumer)
    payload={"index":index}
    payload["sha256"]=hashlib.sha256(canonical_bytes(payload)).hexdigest()
    encoded=canonical_bytes(payload)
    fd=_lock(root)
    try:
        target=_index_path(root,consumer)
        atomic_replace(target,encoded)
    finally:
        os.close(fd)
    return payload

def load_archive_index(root,consumer):
    path=Path(root)/"evidence_archive_index"/(consumer+".json")
    if path.is_symlink() or not path.is_file():
        return None
    payload=json.loads(path.read_bytes())
    if not isinstance(payload,dict) or set(payload)!={"index","sha256"}:
        raise ValueError("invalid archive index artifact")
    expected=hashlib.sha256(canonical_bytes({"index":payload["index"]})).hexdigest()
    if payload["sha256"]!=expected:
        raise ValueError("archive index integrity mismatch")
    validate_archive_index(payload["index"],consumer)
    return payload

def select_historical_snapshot_indexed(root,consumer,*,request,source_policy):
    validate_source_policy(request,source_policy)
    if request["mode"]!="HISTORICAL_AS_OF":
        raise ValueError("historical request required")
    payload=load_archive_index(root,consumer)
    if payload is None:
        raise ValueError("evidence archive index missing")
    archive=Path(root)/"evidence_archive"/consumer
    actual={x.name for x in archive.glob("*.json")} if archive.is_dir() else set()
    indexed={x["filename"] for x in payload["index"]["entries"]}
    if actual!=indexed:
        raise ValueError("stale evidence archive index")
    cutoff=_utc(request["as_of_utc"])
    start=_utc(request["period_start_utc"]); end=_utc(request["period_end_utc"])
    digest=source_policy_digest(request,source_policy)
    candidates=[]
    for item in payload["index"]["entries"]:
        if item["policy_version"]!=request["policy_version"] or item["source_policy_digest"]!=digest:
            continue
        if _utc(item["staged_at_utc"])>cutoff:
            continue
        if _utc(item["period_start_utc"])>start or _utc(item["period_end_utc"])<end:
            continue
        if item["max_available_at_utc"] is not None and _utc(item["max_available_at_utc"])>cutoff:
            continue
        candidates.append(item)
    for item in reversed(candidates):
        snapshot=_load(archive/item["filename"])
        stage=snapshot["entry"]["stage_artifact"]["stage"]
        if any(x["status"] in {"SUCCESS","PARTIAL"} and
               not historically_available(x,request["as_of_utc"])
               for x in stage["observations"]):
            continue
        return snapshot
    raise ValueError("no eligible historical snapshot")

def plan_archive_retention(root,consumer,*,keep_latest=10000):
    if type(keep_latest) is not int or not 1<=keep_latest<=100000:
        raise ValueError("invalid archive retention bound")
    payload=load_archive_index(root,consumer)
    if payload is None:
        raise ValueError("evidence archive index missing")
    entries=payload["index"]["entries"]
    split=max(0,len(entries)-keep_latest)
    return {"keep":[x["filename"] for x in entries[split:]],
            "delete_candidates":[x["filename"] for x in entries[:split]],
            "destructive_action_performed":False}


def select_historical_snapshot_fast(root,consumer,*,request,source_policy,fallback_scan_limit=10000):
    """Use verified index when valid; bounded authoritative scan otherwise."""
    if type(fallback_scan_limit) is not int or not 1<=fallback_scan_limit<=100000:
        raise ValueError("invalid fallback scan limit")
    from .research_evidence_archive_v1 import select_historical_snapshot
    try:
        snapshot=select_historical_snapshot_indexed(
            root,consumer,request=request,source_policy=source_policy)
        return snapshot,"INDEX"
    except (ValueError,OSError,json.JSONDecodeError):
        snapshot=select_historical_snapshot(
            root,consumer,request=request,source_policy=source_policy,
            max_scan=fallback_scan_limit)
        return snapshot,"AUTHORITATIVE_SCAN_FALLBACK"


def _write_index_locked(root,consumer,index):
    validate_archive_index(index,consumer)
    payload={"index":index}
    payload["sha256"]=hashlib.sha256(canonical_bytes(payload)).hexdigest()
    atomic_replace(_index_path(root,consumer),canonical_bytes(payload))
    return payload

def maintain_archive_index(root,consumer,*,generated_at_utc,max_entries=100000):
    """Keep index synchronized after CURRENT archive append.

    Normal path is O(1) archive parsing plus canonical index rewrite. Unexpected
    index loss/corruption/drift triggers a bounded authoritative rebuild.
    """
    root=initialize(root); _utc(generated_at_utc)
    archive=Path(root)/"evidence_archive"/consumer
    if archive.is_symlink():
        raise ValueError("symlink evidence archive denied")
    paths=sorted(archive.glob("*.json")) if archive.is_dir() else []
    if len(paths)>max_entries:
        raise ValueError("archive index maintenance bound exceeded")
    actual={x.name for x in paths}
    fd=_lock(root)
    try:
        try:
            current=load_archive_index(root,consumer)
        except (ValueError,OSError,json.JSONDecodeError):
            current=None
        if current is not None:
            indexed={x["filename"] for x in current["index"]["entries"]}
            missing=actual-indexed
            extra=indexed-actual
            if not missing and not extra:
                return current,"CURRENT"
            if len(missing)==1 and not extra:
                name=next(iter(missing))
                entry=_metadata(_load(archive/name),archive/name)
                entries=list(current["index"]["entries"])+[entry]
                entries.sort(key=lambda x:(x["staged_at_utc"],x["filename"]))
                index={"schema_version":SCHEMA,"consumer_id":consumer,
                       "generated_at_utc":generated_at_utc,"entries":entries}
                return _write_index_locked(root,consumer,index),"APPEND"
        entries=[_metadata(_load(path),path) for path in paths]
        entries.sort(key=lambda x:(x["staged_at_utc"],x["filename"]))
        index={"schema_version":SCHEMA,"consumer_id":consumer,
               "generated_at_utc":generated_at_utc,"entries":entries}
        return _write_index_locked(root,consumer,index),"REBUILD"
    finally:
        os.close(fd)
