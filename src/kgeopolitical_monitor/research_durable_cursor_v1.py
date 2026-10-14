"""Crash-safe owner-only cursor for explicitly invoked synthetic recovery.

A separate advisory run lock serializes cooperating recovery invocations.
The cursor is committed only after a recovery pass returns; replay after a
crash is safe because completion/expiry operations are idempotent.
"""
from __future__ import annotations
import fcntl
import json
import os
from .research_storage_v1 import initialize, atomic_replace as _atomic, canonical_bytes as _bytes
from .research_typed_workflow_v1 import recover_registered
from .research_request_v1 import _ID


def _cursor_key(value):
    if value is None:
        return None
    if not isinstance(value, list) or len(value) != 2 or not all(
        isinstance(part, str) and _ID.fullmatch(part) for part in value
    ):
        raise ValueError("invalid stored recovery cursor")
    return tuple(value)


def recover_durable(root, *, allowed_consumers, observed_at_utc, max_items=10):
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
            stored = json.loads(cursor_path.read_bytes())
            if not isinstance(stored, dict) or set(stored) != {"version", "after_key"} or stored["version"] != 1:
                raise ValueError("invalid cursor record")
            after_key = _cursor_key(stored["after_key"])
        else:
            after_key = None
        report = recover_registered(
            root, allowed_consumers=allowed_consumers,
            observed_at_utc=observed_at_utc, max_items=max_items,
            after_key=after_key)
        next_key = report["next_cursor"]
        if next_key is not None and (
            not isinstance(next_key, tuple) or len(next_key) != 2 or
            not all(isinstance(part, str) and _ID.fullmatch(part) for part in next_key)
        ):
            raise ValueError("invalid next cursor")
        _atomic(cursor_path, _bytes({"version": 1,
                                     "after_key": list(next_key) if next_key is not None else None}))
        return report
    finally:
        os.close(fd)
