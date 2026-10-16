"""Explicitly invoked disposable-ledger rehearsal; never a live migration tool."""
import hashlib
import os
from pathlib import Path
import tempfile
from . import exchange_ledger_atomic_v1 as atomic
from .exchange_ledger_v1 import replay_published

LIMIT = 8 * 1024 * 1024


def _snapshot(path):
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW)
    try:
        import stat
        st = os.fstat(fd)
        if not stat.S_ISREG(st.st_mode) or st.st_nlink != 1 or st.st_size > LIMIT:
            raise ValueError("unsafe or oversized snapshot")
        with os.fdopen(fd, "rb", closefd=False) as stream:
            data = stream.read(LIMIT + 1)
        if len(data) > LIMIT:
            raise ValueError("oversized snapshot")
        return data
    finally:
        os.close(fd)


def rehearse(snapshot, workspace):
    """Copy validated v1 bytes into a new v2 file, then rehearse rollback.
    
    Workspace must be empty and private, supplied explicitly by the caller.
    Source is opened read-only; existing workspaces/files are never overwritten.
    All records are validated by the canonical v2 reader before acceptance.
    """
    workspace = Path(workspace)
    if workspace.is_symlink() or not workspace.is_dir():
        raise ValueError("private empty workspace required")
    if workspace.stat().st_mode & 0o077 or any(workspace.iterdir()):
        raise ValueError("private empty workspace required")
    raw = _snapshot(snapshot)
    digest = hashlib.sha256(raw).hexdigest()
    # Validate source in a disposable child; append/replay cannot touch source.
    with tempfile.TemporaryDirectory(dir=workspace) as child:
        root = Path(child)
        stage = root / "ledger.jsonl"
        with stage.open("xb") as stream:
            stream.write(raw)
            stream.flush()
            os.fsync(stream.fileno())
        rows = atomic._read(stage)
        fd = atomic._lock(root, True)
        try:
            candidate = root / "ledger-v2.jsonl"
            os.replace(stage, candidate)
            atomic._sync_directory(root)
            if atomic._read(candidate) != rows:
                raise ValueError("conversion mismatch")
            # Restore original format in the rehearsal directory only.
            os.replace(candidate, stage)
            atomic._sync_directory(root)
            if (candidate.exists() or _snapshot(stage) != raw
                    or atomic._read(stage) != rows
                    or replay_published(root, 0) != rows[:100]):
                raise ValueError("rollback namespace or content mismatch")
        finally:
            os.close(fd)
    if _snapshot(snapshot) != raw:
        raise ValueError("source changed during rehearsal")
    return {"records": len(rows), "sha256": digest, "rollback": "PASS",
            "source_unchanged": True, "send": False}
