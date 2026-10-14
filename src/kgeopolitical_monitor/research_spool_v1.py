"""Durable offline synthetic research inbox and isolated consumer outbox.

No network, live provider, or canonical KGM data access. A single authorized
local worker owns the dedicated private POSIX spool. Filesystem ACLs and
transport identity MUST be enforced outside this module before deployment.
"""
from __future__ import annotations
import fcntl
import hashlib
import json
import os
from pathlib import Path
import tempfile
from .research_request_v1 import validate_request
from .research_lifecycle_v1 import SyntheticResearchJob


def _bytes(value):
    return (json.dumps(value, sort_keys=True, ensure_ascii=True,
                       separators=(",", ":")) + "\n").encode()


def _directory(path):
    path = Path(path)
    if path.is_symlink() or not path.is_dir():
        raise ValueError("dedicated real directory required")
    return path


def _atomic(path, payload):
    if path.is_symlink():
        raise ValueError("symlink destination denied")
    with tempfile.NamedTemporaryFile(dir=path.parent, prefix=".stage-", delete=False) as f:
        stage = Path(f.name)
        try:
            os.fchmod(f.fileno(), 0o600)
            f.write(payload)
            f.flush()
            os.fsync(f.fileno())
        except BaseException:
            stage.unlink(missing_ok=True)
            raise
    try:
        os.replace(stage, path)
        fd = os.open(path.parent, os.O_RDONLY | os.O_DIRECTORY)
        try:
            os.fsync(fd)
        finally:
            os.close(fd)
    finally:
        stage.unlink(missing_ok=True)


def _lock(root):
    fd = os.open(root / ".research.lock", os.O_CREAT | os.O_RDWR | os.O_NOFOLLOW, 0o600)
    fcntl.flock(fd, fcntl.LOCK_EX)
    return fd


def _consumer(root, consumer_id):
    # consumer_id has already passed request validator
    directory = root / "outbox" / consumer_id
    if directory.is_symlink():
        raise ValueError("symlink outbox denied")
    directory.mkdir(mode=0o700, parents=False, exist_ok=True)
    return _directory(directory)


def initialize(root):
    root = _directory(root)
    for name in ("inbox", "outbox"):
        path = root / name
        if path.is_symlink():
            raise ValueError("symlink spool denied")
        path.mkdir(mode=0o700, exist_ok=True)
    return root


def submit(root, request, *, allowed_consumers):
    """Persist one validated request; same ID/different bytes fails closed."""
    root = initialize(root)
    validate_request(request)
    if request["consumer_id"] not in allowed_consumers:
        raise PermissionError("consumer not authorized")
    if request["policy_version"] != allowed_consumers[request["consumer_id"]]:
        raise PermissionError("policy version not authorized")
    digest = hashlib.sha256(_bytes(request)).hexdigest()
    fd = _lock(root)
    try:
        path = root / "inbox" / (request["consumer_id"] + "--" + request["request_id"] + ".json")
        if path.is_symlink():
            raise ValueError("symlink request denied")
        if path.exists():
            saved = json.loads(path.read_bytes())
            if saved["request_digest"] != digest or hashlib.sha256(_bytes(validate_request(saved["request"]))).hexdigest() != digest or saved["status"] != "RECEIVED":
                raise ValueError("idempotency conflict")
            return saved
        record = {"request_digest": digest, "request": request, "status": "RECEIVED"}
        _atomic(path, _bytes(record))
        return record
    finally:
        os.close(fd)


def process_fixture(root, consumer_id, request_id, *, allowed_consumers,
                    evidence, generated_at_utc, snapshot_id, coverage, source_health):
    """Synthetic fixture only; no source calls, one immutable correlated result."""
    root = initialize(root)
    if consumer_id not in allowed_consumers:
        raise PermissionError("consumer not authorized")
    from .research_request_v1 import _ID
    if not _ID.fullmatch(consumer_id) or not _ID.fullmatch(request_id):
        raise ValueError("invalid identifier")
    fd = _lock(root)
    try:
        request_path = root / "inbox" / (consumer_id + "--" + request_id + ".json")
        if request_path.is_symlink() or not request_path.is_file():
            raise ValueError("request unavailable")
        record = json.loads(request_path.read_bytes())
        request = validate_request(record["request"])
        if request["consumer_id"] != consumer_id or request["request_id"] != request_id:
            raise ValueError("request correlation mismatch")
        if request["policy_version"] != allowed_consumers[consumer_id]:
            raise PermissionError("policy revoked")
        if record["request_digest"] != hashlib.sha256(_bytes(request)).hexdigest():
            raise ValueError("stored request digest mismatch")
        outbox = _consumer(root, consumer_id)
        target = outbox / (request_id + ".json")
        if target.is_symlink():
            raise ValueError("symlink result denied")
        if target.exists():
            saved = json.loads(target.read_bytes())
            if saved["request_digest"] != record["request_digest"] or saved["result"]["consumer_id"] != consumer_id or saved["result"]["request_id"] != request_id or saved["sha256"] != hashlib.sha256(_bytes({"request_digest": saved["request_digest"], "result": saved["result"]})).hexdigest():
                raise ValueError("result digest conflict")
            return saved
        job = SyntheticResearchJob(request)
        job.transition("ACCEPTED")
        job.transition("PROCESSING")
        result = job.complete_fixture(evidence, generated_at_utc=generated_at_utc,
                                      snapshot_id=snapshot_id, coverage=coverage,
                                      source_health=source_health)
        artifact = {"request_digest": record["request_digest"], "result": result}
        artifact["sha256"] = hashlib.sha256(_bytes(artifact)).hexdigest()
        _atomic(target, _bytes(artifact))
        return artifact
    finally:
        os.close(fd)


def retrieve(root, consumer_id, request_id, *, allowed_consumers):
    root = initialize(root)
    from .research_request_v1 import _ID
    if consumer_id not in allowed_consumers or not _ID.fullmatch(consumer_id) or not _ID.fullmatch(request_id):
        raise PermissionError("unauthorized result")
    path = root / "outbox" / consumer_id / (request_id + ".json")
    if path.is_symlink() or not path.is_file():
        raise ValueError("result unavailable")
    artifact = json.loads(path.read_bytes())
    if artifact["result"]["consumer_id"] != consumer_id or artifact["result"]["request_id"] != request_id or artifact["result"]["policy_version"] != allowed_consumers[consumer_id]:
        raise ValueError("correlation mismatch")
    expected = hashlib.sha256(_bytes({"request_digest": artifact["request_digest"],
                                      "result": artifact["result"]})).hexdigest()
    if artifact["sha256"] != expected:
        raise ValueError("corrupt result")
    return artifact
