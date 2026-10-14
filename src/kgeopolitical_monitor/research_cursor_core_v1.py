"""Isolated crash-safe cursor primitive; caller explicitly supplies recovery pass.

No network, worker, scheduler, producer activation or implicit import of typed workflow.
"""
from __future__ import annotations
import fcntl
import json
import os
from .research_storage_v1 import initialize, atomic_replace, canonical_bytes
from .research_request_v1 import _ID

def _key(value, *, stored=False):
    if value is None:
        return None
    if not isinstance(value, (list if stored else tuple)) or len(value) != 2 or not all(
        isinstance(part, str) and _ID.fullmatch(part) for part in value
    ):
        raise ValueError("invalid recovery cursor")
    return tuple(value)

def recover_with_cursor(root, *, recover_fn, allowed_consumers, observed_at_utc, max_items=10):
    """Commit next cursor only after injected bounded recovery pass succeeds."""
    if not callable(recover_fn):
        raise ValueError("recovery callback required")
    if type(max_items) is not int or not 1 <= max_items <= 100:
        raise ValueError("invalid recovery bound")
    root = initialize(root)
    cursor_path = root / ".research-recovery-cursor.json"
    lock_path = root / ".research-recovery-run.lock"
    fd = os.open(lock_path, os.O_CREAT | os.O_RDWR | os.O_NOFOLLOW, 0o600)
    try:
        fcntl.flock(fd, fcntl.LOCK_EX)
        if cursor_path.is_symlink():
            raise ValueError("cursor alias")
        if cursor_path.exists():
            if not cursor_path.is_file():
                raise ValueError("invalid cursor file")
            data = json.loads(cursor_path.read_bytes())
            if not isinstance(data, dict) or set(data) != {"version", "after_key"} or data["version"] != 1:
                raise ValueError("invalid cursor record")
            after_key = _key(data["after_key"], stored=True)
        else:
            after_key = None
        report = recover_fn(root, allowed_consumers=allowed_consumers,
                            observed_at_utc=observed_at_utc, max_items=max_items,
                            after_key=after_key)
        if not isinstance(report, dict) or "next_cursor" not in report:
            raise ValueError("invalid recovery report")
        next_key = _key(report["next_cursor"])
        atomic_replace(cursor_path, canonical_bytes({"version": 1,
                       "after_key": list(next_key) if next_key else None}))
        return report
    finally:
        os.close(fd)
