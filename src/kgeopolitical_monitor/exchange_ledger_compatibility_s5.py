"""Read-only v1-v2 compatibility preflight; never mutates either ledger."""
import json
from pathlib import Path


def compare_ledger_formats(root):
    root=Path(root)
    if root.is_symlink() or not root.is_dir():
        raise ValueError("invalid root")
    def read(name):
        path=root/name
        if path.is_symlink():
            raise ValueError("symlink ledger denied")
        if not path.exists():
            return None
        raw=path.read_bytes()
        if raw and not raw.endswith(b"\n"):
            raise ValueError("torn ledger")
        rows=[json.loads(line) for line in raw.splitlines()]
        previous=0
        found=set()
        for row in rows:
            if set(row)!={"sequence","batch_id","sha256"} or type(row["sequence"]) is not int or row["sequence"]!=previous+1:
                raise ValueError("invalid sequence or record shape")
            if row["batch_id"] in found or not isinstance(row["sha256"],str) or len(row["sha256"])!=64:
                raise ValueError("duplicate id or invalid sha256")
            found.add(row["batch_id"])
            previous=row["sequence"]
        return rows
    left=read("ledger.jsonl")
    right=read("ledger-v2.jsonl")
    if left is None or right is None:
        return {"compatible":False,"reason":"MISSING_FORMAT","v1_count":len(left or []),"v2_count":len(right or [])}
    if left!=right:
        return {"compatible":False,"reason":"DATA_DIVERGENCE","v1_count":len(left),"v2_count":len(right)}
    return {"compatible":True,"reason":"IDENTICAL","v1_count":len(left),"v2_count":len(right)}
