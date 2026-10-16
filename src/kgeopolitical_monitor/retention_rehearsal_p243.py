"""Retention execution only inside internally created disposable storage."""
import math
import re
import tempfile
from pathlib import Path

TTL = {"raw": 30*86400, "observation": 90*86400,
       "artifact": 7*86400, "trace": 14*86400}
ID = re.compile(r"[a-zA-Z0-9_-]{1,64}")

def rehearse(records, *, now, protected_ids=(), max_bytes=1024*1024, max_records=100):
    if type(now) not in (int,float) or not math.isfinite(now):
        raise ValueError("invalid time")
    if type(max_bytes) is not int or not 1 <= max_bytes <= 8*1024*1024:
        raise ValueError("invalid byte limit")
    if type(max_records) is not int or not 1 <= max_records <= 1000:
        raise ValueError("invalid count limit")
    if not isinstance(records,list) or len(records)>max_records:
        raise ValueError("record count exceeded")
    protected=set(protected_ids)
    if any(not isinstance(x,str) or not ID.fullmatch(x) for x in protected):
        raise ValueError("invalid protected id")
    ids=set();total=0
    for row in records:
        if not isinstance(row,dict) or set(row)!={"id","kind","created","payload"}:
            raise ValueError("invalid record")
        key=row["id"]
        if not isinstance(key,str) or not ID.fullmatch(key) or key in ids:
            raise ValueError("invalid or duplicate id")
        if row["kind"] not in {*TTL,"ledger","replay_required","evidence"}:
            raise ValueError("unknown kind")
        if type(row["created"]) not in (int,float) or not math.isfinite(row["created"]) or row["created"]>now:
            raise ValueError("invalid creation time")
        if type(row["payload"]) is not bytes:
            raise ValueError("bytes required")
        total+=len(row["payload"]);ids.add(key)
    if total>max_bytes:
        raise ValueError("byte limit exceeded")
    if not protected <= ids:
        raise ValueError("unknown protected reference")
    removed=[];kept=[]
    with tempfile.TemporaryDirectory(prefix="kgm-retention-rehearsal-") as temp:
        root=Path(temp)
        for row in records:
            (root/row["id"]).write_bytes(row["payload"])
        for row in records:
            key=row["id"];ttl=TTL.get(row["kind"])
            if key not in protected and ttl is not None and now-row["created"]>=ttl:
                (root/key).unlink();removed.append(key)
            else:
                kept.append(key)
        # Demonstrate byte-exact restoration into canonical fixture IDs.
        for row in records:
            if row["id"] in removed:
                (root/row["id"]).write_bytes(row["payload"])
        if any((root/r["id"]).read_bytes()!=r["payload"] for r in records):
            raise ValueError("restore failed")
    return {"deleted_in_disposable_copy":sorted(removed),"retained":sorted(kept),
            "restore":"PASS","input_bytes":total,"production_modified":False}
