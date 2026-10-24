"""Read-only, fail-closed ledger migration inventory. NO APPLIER or production writes."""
import hashlib
import json
import os
from pathlib import Path
import stat

from .exchange_generation_v1 import read_generation
from .exchange_ledger_atomic_v1 import replay as v2_replay


def _read_legacy(path: Path):
    flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0)
    fd = os.open(path, flags)
    try:
        meta = os.fstat(fd)
        if not stat.S_ISREG(meta.st_mode) or meta.st_nlink != 1 or meta.st_size > 1048576:
            raise ValueError("legacy ledger must be private bounded regular file")
        with os.fdopen(fd, "rb", closefd=False) as source:
            raw = source.read()
    finally:
        os.close(fd)
    if raw and not raw.endswith(b"\\n"):
        raise ValueError("torn legacy ledger")
    return [json.loads(row) for row in raw.splitlines()]


def preview_ledger_migration(root):
    """Inventory independently verified rows, no state mutation or automatic backfill."""
    root = Path(root)
    if root.is_symlink() or not root.is_dir():
        raise ValueError("private root required")
    legacy_path = root / "ledger.jsonl"
    if not legacy_path.exists() or legacy_path.is_symlink():
        raise ValueError("legacy ledger missing or linked")
    legacy = _read_legacy(legacy_path)
    newer = v2_replay(root, after_sequence=0, max_records=100)
    if len(legacy) > 100 or len(newer) > 100:
        raise ValueError("review bounded population only")
    seen = set()
    v2 = {}
    for r in newer:
        if r["batch_id"] in v2:
            raise ValueError("duplicate v2 batch")
        v2[r["batch_id"]] = r
    missing = []
    for i, row in enumerate(legacy, 1):
        if set(row) != {"sequence", "batch_id", "sha256"} or row["sequence"] != i:
            raise ValueError("invalid legacy ledger order or schema")
        bid = row["batch_id"]
        if bid in seen:
            raise ValueError("duplicate legacy batch")
        seen.add(bid)
        batch = read_generation(root, bid)
        if batch["batch_id"] != bid:
            raise ValueError("generation identity mismatch")
        digest = hashlib.sha256((root / bid / "batch.json").read_bytes()).hexdigest()
        if digest != row["sha256"]:
            raise ValueError("legacy digest mismatch")
        if bid in v2:
            if v2[bid]["sha256"] != digest:
                raise ValueError("cross-version digest conflict")
        else:
            missing.append(bid)
    return {"legacy_count":len(legacy),"v2_count":len(newer),
            "missing_in_v2":tuple(missing),"migration_applied":False,
            "production_authorized":False}
