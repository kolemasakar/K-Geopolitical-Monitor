"""Explicit offline expiration for bounded synthetic KGM requests.

Never expire a request when an artifact exists; reconcile first.
No background timer, provider work or production scheduler.
"""
from __future__ import annotations
import os
from .research_storage_v1 import initialize, lock as _lock, atomic_replace as _atomic, canonical_bytes as _bytes
from .research_durable_lifecycle_v1 import _read, _path
from .research_request_v1 import _ID, _utc


def expire_stale(root, consumer, request_id, *, allowed_consumers,
                 deadline_utc, observed_at_utc):
    root = initialize(root)
    if not isinstance(consumer, str) or not isinstance(request_id, str) or not _ID.fullmatch(consumer) or not _ID.fullmatch(request_id):
        raise ValueError("invalid identity")
    if consumer not in allowed_consumers:
        raise PermissionError("consumer denied")
    deadline = _utc(deadline_utc)
    observed = _utc(observed_at_utc)
    if observed < deadline:
        raise ValueError("deadline not reached")
    fd = _lock(root)
    try:
        path = _path(root, consumer, request_id)
        saved = _read(path)
        req = saved["request"]
        if (req["consumer_id"], req["request_id"], req["policy_version"]) != (
            consumer, request_id, allowed_consumers[consumer]):
            raise PermissionError("policy revoked or identity mismatch")
        if saved["status"] == "EXPIRED":
            return saved
        if saved["status"] not in {"RECEIVED", "ACCEPTED", "PROCESSING"}:
            raise ValueError("cannot expire terminal state")
        if deadline < _utc(req["requested_at_utc"]) or observed < _utc(saved["updated_at_utc"]):
            raise ValueError("invalid deadline or observation")
        artifact = root / "outbox" / consumer / (request_id + ".json")
        if artifact.is_symlink() or artifact.exists():
            raise ValueError("published artifact present; reconcile first")
        saved["status"] = "EXPIRED"
        saved["updated_at_utc"] = observed_at_utc
        _atomic(path, _bytes(saved))
        return saved
    finally:
        os.close(fd)
