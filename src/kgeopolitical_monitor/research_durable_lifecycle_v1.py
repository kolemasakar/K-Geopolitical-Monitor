"""Offline durable synthetic lifecycle and bounded admission.

Not a production scheduler or authenticated endpoint. All transitions use a
cooperative exclusive POSIX lock and fsynced atomic replacement.
"""
from __future__ import annotations
import hashlib
import json
import os
from .research_storage_v1 import initialize, lock as _lock, atomic_replace as _atomic, canonical_bytes as _bytes
from .research_request_v1 import validate_request, _ID, _utc
from .research_states_v1 import TRANSITIONS


def _path(root, consumer, request_id):
    return root / "inbox" / (consumer + "--" + request_id + ".json")


def _read(path):
    if path.is_symlink() or not path.is_file():
        raise ValueError("request unavailable")
    saved = json.loads(path.read_bytes())
    if not isinstance(saved, dict) or not {"request", "request_digest", "status", "updated_at_utc", "attempts"} <= set(saved):
        raise ValueError("noncanonical durable request record")
    if type(saved["attempts"]) is not int or saved["attempts"] < 0:
        raise ValueError("invalid durable attempt count")
    _utc(saved["updated_at_utc"])
    if "deadline_utc" in saved:
        _utc(saved["deadline_utc"])
        expected_deadline_digest = hashlib.sha256(_bytes({"request_digest": saved["request_digest"], "deadline_utc": saved["deadline_utc"]})).hexdigest()
        if saved.get("deadline_digest") != expected_deadline_digest:
            raise ValueError("deadline digest mismatch")
    elif "deadline_digest" in saved:
        raise ValueError("orphan deadline digest")
    request = validate_request(saved["request"])
    if hashlib.sha256(_bytes(request)).hexdigest() != saved["request_digest"]:
        raise ValueError("request digest mismatch")
    if saved["status"] not in TRANSITIONS:
        raise ValueError("unknown stored state")
    return saved


def admit(root, request, *, allowed_consumers, max_pending_per_consumer=10, deadline_utc=None):
    root = initialize(root)
    validate_request(request)
    consumer = request["consumer_id"]
    if consumer not in allowed_consumers or request["policy_version"] != allowed_consumers[consumer]:
        raise PermissionError("consumer/policy denied")
    if type(max_pending_per_consumer) is not int or not 1 <= max_pending_per_consumer <= 1000:
        raise ValueError("invalid quota")
    if deadline_utc is not None and _utc(deadline_utc) < _utc(request["requested_at_utc"]):
        raise ValueError("deadline predates request")
    digest = hashlib.sha256(_bytes(request)).hexdigest()
    fd = _lock(root)
    try:
        target = _path(root, consumer, request["request_id"])
        if target.exists() or target.is_symlink():
            saved = _read(target)
            if saved["request_digest"] != digest:
                raise ValueError("idempotency conflict")
            if deadline_utc is not None and saved.get("deadline_utc") != deadline_utc:
                raise ValueError("immutable admission deadline conflict")
            return saved
        pending = 0
        for path in (root / "inbox").glob(consumer + "--*.json"):
            if path.name.endswith(".deadline.json"):
                continue
            record = _read(path)
            if record["request"]["consumer_id"] != consumer:
                raise ValueError("corrupt consumer namespace")
            if record["status"] in {"RECEIVED", "ACCEPTED", "PROCESSING"}:
                pending += 1
        if pending >= max_pending_per_consumer:
            raise ValueError("pending quota exceeded")
        saved = {"request": request, "request_digest": digest, "status": "RECEIVED",
                 "updated_at_utc": request["requested_at_utc"], "attempts": 0}
        if deadline_utc is not None:
            saved["deadline_utc"] = deadline_utc
            saved["deadline_digest"] = hashlib.sha256(_bytes({"request_digest": digest, "deadline_utc": deadline_utc})).hexdigest()
        _atomic(target, _bytes(saved))
        return saved
    finally:
        os.close(fd)


def advance(root, consumer, request_id, next_status, *, allowed_consumers, at_utc):
    root = initialize(root)
    if not isinstance(consumer, str) or not isinstance(request_id, str) or not _ID.fullmatch(consumer) or not _ID.fullmatch(request_id):
        raise ValueError("invalid identity")
    _utc(at_utc)
    if consumer not in allowed_consumers:
        raise PermissionError("consumer denied")
    fd = _lock(root)
    try:
        target = _path(root, consumer, request_id)
        saved = _read(target)
        req = saved["request"]
        if req["consumer_id"] != consumer or req["request_id"] != request_id or req["policy_version"] != allowed_consumers[consumer]:
            raise PermissionError("consumer policy revoked or request mismatch")
        if next_status == saved["status"]:
            return saved
        # Canonical terminal success must be coupled to a validated immutable
        # typed artifact via research_completion_v1.complete_or_reconcile.
        if next_status in {"COMPLETE", "PARTIAL"}:
            raise ValueError("typed terminal completion required")
        if next_status not in TRANSITIONS[saved["status"]]:
            raise ValueError("illegal state transition")
        if _utc(at_utc) < _utc(saved["updated_at_utc"]):
            raise ValueError("non-monotonic transition timestamp")
        saved["status"] = next_status
        saved["updated_at_utc"] = at_utc
        if next_status == "PROCESSING":
            saved["attempts"] += 1
        _atomic(target, _bytes(saved))
        return saved
    finally:
        os.close(fd)


def recovery_snapshot(root, *, allowed_consumers):
    root = initialize(root)
    fd = _lock(root)
    try:
        pending = []
        for path in sorted((root / "inbox").glob("*.json")):
            if path.name.endswith(".deadline.json"):
                continue
            saved = _read(path)
            req = saved["request"]
            if req["consumer_id"] not in allowed_consumers or req["policy_version"] != allowed_consumers[req["consumer_id"]]:
                continue
            if path.name != req["consumer_id"] + "--" + req["request_id"] + ".json":
                raise ValueError("invalid namespace")
            if saved["status"] in {"RECEIVED", "ACCEPTED", "PROCESSING"}:
                pending.append({"consumer_id": req["consumer_id"],
                                "request_id": req["request_id"],
                                "status": saved["status"],
                                "attempts": saved["attempts"]})
        return pending
    finally:
        os.close(fd)
