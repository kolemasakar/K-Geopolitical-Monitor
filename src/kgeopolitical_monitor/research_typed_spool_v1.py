"""Standalone KGM-side typed synthetic research result fixture.

No provider calls, no K-Trader dependency, no network transport. Uses the
existing offline spool's cooperative lock and immutable per-consumer result.
"""
from __future__ import annotations
import hashlib
import json
from .research_storage_v1 import initialize, lock as _lock, consumer_outbox as _consumer, atomic_replace as _atomic, canonical_bytes as _bytes
from .research_request_v1 import validate_request, _ID
from .research_typed_result_v1 import validate_typed_result
import os


def publish_typed_fixture(root, consumer_id, request_id, result, *, allowed_consumers):
    root = initialize(root)
    if not isinstance(consumer_id, str) or not isinstance(request_id, str) or not _ID.fullmatch(consumer_id) or not _ID.fullmatch(request_id):
        raise ValueError("invalid request identity")
    if consumer_id not in allowed_consumers:
        raise PermissionError("consumer denied")
    fd = _lock(root)
    try:
        path = root / "inbox" / (consumer_id + "--" + request_id + ".json")
        if path.is_symlink() or not path.is_file():
            raise ValueError("request unavailable")
        saved = json.loads(path.read_bytes())
        req = validate_request(saved["request"])
        digest = hashlib.sha256(_bytes(req)).hexdigest()
        if (req["consumer_id"], req["request_id"], req["policy_version"]) != (
            consumer_id, request_id, allowed_consumers[consumer_id]
        ) or saved["request_digest"] != digest:
            raise ValueError("request mismatch or policy revoked")
        validate_typed_result(req, result)
        target = _consumer(root, consumer_id) / (request_id + ".json")
        if target.is_symlink():
            raise ValueError("result symlink denied")
        artifact = {"request_digest": digest, "result": result}
        artifact["sha256"] = hashlib.sha256(_bytes(artifact)).hexdigest()
        if target.exists():
            if target.read_bytes() != _bytes(artifact):
                raise ValueError("immutable result conflict")
            return artifact
        _atomic(target, _bytes(artifact))
        return artifact
    finally:
        os.close(fd)
