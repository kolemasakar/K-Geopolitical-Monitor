"""Crash-reconcilable offline synthetic typed research completion.

The immutable result is published first; the durable terminal state is then
recorded. Recovery may safely finalize a previously published verified result.
This is not an atomic multi-file transaction or a production worker.
"""
from __future__ import annotations
import hashlib
import json
import os
from .research_spool_v1 import initialize, _lock, _bytes, _atomic, _consumer
from .research_durable_lifecycle_v1 import _read, _path
from .research_request_v1 import _ID
from .research_typed_result_v1 import validate_typed_result


def _verify(root, consumer, request_id, allowed_consumers):
    if not isinstance(consumer, str) or not isinstance(request_id, str) or not _ID.fullmatch(consumer) or not _ID.fullmatch(request_id):
        raise ValueError("invalid identity")
    if consumer not in allowed_consumers:
        raise PermissionError("consumer denied")
    path = _path(root, consumer, request_id)
    saved = _read(path)
    req = saved["request"]
    if (req["consumer_id"], req["request_id"], req["policy_version"]) != (
        consumer, request_id, allowed_consumers[consumer]):
        raise PermissionError("policy revoked or request mismatch")
    return path, saved


def _result(root, consumer, request_id, saved):
    path = root / "outbox" / consumer / (request_id + ".json")
    if path.is_symlink() or not path.is_file():
        raise ValueError("result not yet published")
    artifact = json.loads(path.read_bytes())
    if set(artifact) != {"request_digest", "result", "sha256"} or artifact["request_digest"] != saved["request_digest"]:
        raise ValueError("artifact/request mismatch")
    expected = hashlib.sha256(_bytes({"request_digest": artifact["request_digest"],
                                      "result": artifact["result"]})).hexdigest()
    if artifact["sha256"] != expected:
        raise ValueError("artifact integrity mismatch")
    validate_typed_result(saved["request"], artifact["result"])
    if artifact["result"]["research_status"] not in {"COMPLETE", "PARTIAL"}:
        raise ValueError("unsupported fixture terminal state")
    return artifact


def complete_or_reconcile(root, consumer, request_id, *, allowed_consumers,
                          result=None, at_utc=None):
    """Publish immutable typed result then reconcile persisted terminal state.

    result=None performs recovery only, and NEVER invents an absent result.
    Must only be invoked by a trusted local KGM worker.
    """
    from .research_request_v1 import _utc
    root = initialize(root)
    fd = _lock(root)
    try:
        path, saved = _verify(root, consumer, request_id, allowed_consumers)
        if saved["status"] not in {"PROCESSING", "COMPLETE", "PARTIAL"}:
            raise ValueError("request not processing/terminal")
        target = _consumer(root, consumer) / (request_id + ".json")
        if target.is_symlink():
            raise ValueError("symlink result denied")
        if result is not None:
            validate_typed_result(saved["request"], result)
            if result["research_status"] not in {"COMPLETE", "PARTIAL"}:
                raise ValueError("invalid completion status")
            candidate = {"request_digest": saved["request_digest"], "result": result}
            candidate["sha256"] = hashlib.sha256(_bytes(candidate)).hexdigest()
            if target.exists():
                if target.read_bytes() != _bytes(candidate):
                    raise ValueError("immutable result conflict")
            else:
                if saved["status"] != "PROCESSING":
                    raise ValueError("terminal state without artifact")
                _atomic(target, _bytes(candidate))
        artifact = _result(root, consumer, request_id, saved)
        terminal = artifact["result"]["research_status"]
        if saved["status"] in {"COMPLETE", "PARTIAL"}:
            if saved["status"] != terminal:
                raise ValueError("terminal/result mismatch")
            return artifact
        if at_utc is None:
            raise ValueError("explicit reconciliation timestamp required")
        if _utc(at_utc) < _utc(saved["updated_at_utc"]):
            raise ValueError("non-monotonic reconciliation")
        saved["status"] = terminal
        saved["updated_at_utc"] = at_utc
        _atomic(path, _bytes(saved))
        return artifact
    finally:
        os.close(fd)
