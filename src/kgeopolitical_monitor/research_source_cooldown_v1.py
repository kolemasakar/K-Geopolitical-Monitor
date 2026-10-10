"""Durable source cooldown state for owner-pilot adapters."""
from __future__ import annotations
import json
from pathlib import Path
from .research_request_v1 import _utc
from .research_storage_v1 import real_directory, atomic_replace, canonical_bytes

def _path(root, source_id):
    if not isinstance(source_id,str) or not source_id or "/" in source_id or ".." in source_id:
        raise ValueError("invalid source id")
    d=real_directory(root)/"source_state"; d.mkdir(mode=0o700,exist_ok=True)
    return d/(source_id+".json")

def record_cooldown(root, source_id, *, until_utc, reason):
    _utc(until_utc)
    if reason not in {"RATE_LIMITED","TRANSPORT_UNAVAILABLE"}:
        raise ValueError("invalid cooldown reason")
    p=_path(root,source_id)
    atomic_replace(p,canonical_bytes({"source_id":source_id,"until_utc":until_utc,"reason":reason}))
    return {"source_id":source_id,"until_utc":until_utc,"reason":reason}

def check_cooldown(root, source_id, *, observed_at_utc):
    now=_utc(observed_at_utc); p=_path(root,source_id)
    if not p.exists(): return None
    if p.is_symlink(): raise ValueError("symlink cooldown denied")
    saved=json.loads(p.read_text())
    if set(saved)!={"source_id","until_utc","reason"} or saved["source_id"]!=source_id:
        raise ValueError("invalid cooldown state")
    until=_utc(saved["until_utc"])
    return saved if now < until else None
