"""Durable explicit synthetic deadlines for the canonical KGM offline workflow.

Separate immutable per-request metadata; missing deadline never implies expiry.
Registration is cooperative-lock protected and crash-safe via atomic fsync.
"""
from __future__ import annotations
import json
import os
from .research_storage_v1 import initialize, lock as _lock, atomic_replace as _atomic, canonical_bytes as _bytes
from .research_durable_lifecycle_v1 import _read, _path
from .research_request_v1 import _ID, _utc


def _deadline_path(root, consumer, request_id):
    return root / "inbox" / (consumer + "--" + request_id + ".deadline.json")


def register_deadline(root, consumer, request_id, *, allowed_consumers, deadline_utc):
    root = initialize(root)
    if not isinstance(consumer, str) or not isinstance(request_id, str) or not _ID.fullmatch(consumer) or not _ID.fullmatch(request_id):
        raise ValueError("invalid identity")
    deadline = _utc(deadline_utc)
    if consumer not in allowed_consumers:
        raise PermissionError("consumer denied")
    fd = _lock(root)
    try:
        request = _read(_path(root, consumer, request_id))
        req = request["request"]
        if (req["consumer_id"], req["request_id"], req["policy_version"]) != (
            consumer, request_id, allowed_consumers[consumer]):
            raise PermissionError("policy revoked or identity mismatch")
        if request.get("deadline_utc") is not None and request["deadline_utc"] != deadline_utc:
            raise ValueError("immutable admission deadline conflict")
        if deadline < _utc(req["requested_at_utc"]):
            raise ValueError("deadline predates request")
        target = _deadline_path(root, consumer, request_id)
        record = {"consumer_id": consumer, "request_id": request_id,
                  "request_digest": request["request_digest"],
                  "deadline_utc": deadline_utc}
        if target.is_symlink():
            raise ValueError("deadline alias")
        if target.exists():
            if json.loads(target.read_bytes()) != record:
                raise ValueError("immutable deadline conflict")
            return record
        if request["status"] in {"COMPLETE", "PARTIAL", "FAILED", "EXPIRED"}:
            raise ValueError("cannot register terminal deadline")
        _atomic(target, _bytes(record))
        return record
    finally:
        os.close(fd)


def registered_deadlines(root, *, allowed_consumers):
    root = initialize(root)
    fd = _lock(root)
    try:
        found = {}
        for target in sorted((root / "inbox").glob("*.deadline.json")):
            if target.is_symlink() or not target.is_file():
                raise ValueError("invalid deadline artifact")
            record = json.loads(target.read_bytes())
            if not isinstance(record, dict) or set(record) != {"consumer_id", "request_id", "request_digest", "deadline_utc"}:
                raise ValueError("invalid deadline schema")
            consumer, request_id = record["consumer_id"], record["request_id"]
            if not isinstance(consumer, str) or not isinstance(request_id, str) or not _ID.fullmatch(consumer) or not _ID.fullmatch(request_id):
                raise ValueError("invalid deadline identity")
            if target.name != consumer + "--" + request_id + ".deadline.json":
                raise ValueError("invalid deadline namespace")
            request = _read(_path(root, consumer, request_id))
            req = request["request"]
            if req["consumer_id"] != consumer or req["request_id"] != request_id or request["request_digest"] != record["request_digest"]:
                raise ValueError("deadline/request mismatch")
            _utc(record["deadline_utc"])
            if _utc(record["deadline_utc"]) < _utc(req["requested_at_utc"]):
                raise ValueError("deadline predates request")
            if consumer in allowed_consumers and req["policy_version"] == allowed_consumers[consumer]:
                found[(consumer, request_id)] = record["deadline_utc"]
        # New canonical admission stores deadline in the same fsynced request
        # record, eliminating the admission-to-sidecar crash window.
        for target in sorted((root / "inbox").glob("*.json")):
            if target.name.endswith(".deadline.json"):
                continue
            saved = _read(target)
            req = saved["request"]
            consumer, request_id = req["consumer_id"], req["request_id"]
            if target.name != consumer + "--" + request_id + ".json":
                raise ValueError("invalid request namespace")
            embedded = saved.get("deadline_utc")
            if embedded is None:
                continue
            _utc(embedded)
            if _utc(embedded) < _utc(req["requested_at_utc"]):
                raise ValueError("invalid embedded deadline")
            key = (consumer, request_id)
            if key in found and found[key] != embedded:
                raise ValueError("sidecar/admission deadline conflict")
            if consumer in allowed_consumers and req["policy_version"] == allowed_consumers[consumer]:
                found[key] = embedded
        return found
    finally:
        os.close(fd)
