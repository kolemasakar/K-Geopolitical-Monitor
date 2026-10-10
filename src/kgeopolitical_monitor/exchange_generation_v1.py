"""Offline v1 complete-generation artifact protocol; no DB, network or secrets."""
import hashlib
import json
import os
from pathlib import Path
import stat
import tempfile

from .exchange_contract_v1 import validate_batch


def _json(value):
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False) + "\n").encode()


def _directory(path):
    path = Path(path)
    if path.is_symlink() or not path.is_dir() or path.resolve() in (Path("/"), Path("/tmp")):
        raise ValueError("dedicated real export directory required")
    return path


def _id(value):
    if not isinstance(value, str) or not value or len(value) > 128 or not value.isascii() or not value.replace("-", "").replace("_", "").isalnum():
        raise ValueError("invalid batch id")
    return value


def _sync(path):
    fd = os.open(path, os.O_RDONLY | getattr(os, "O_DIRECTORY", 0))
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def _write(path, payload):
    with open(path, "xb") as f:
        f.write(payload)
        f.flush()
        os.fsync(f.fileno())


def _manifest(batch, raw):
    return {"schema_version": "kgm.exchange.manifest.v1", "batch_id": batch["batch_id"],
            "artifact": "batch.json", "sha256": hashlib.sha256(raw).hexdigest(),
            "size_bytes": len(raw), "record_count": len(batch["records"]),
            "high_watermark_cursor": batch["high_watermark_cursor"]}


def publish_generation(batch, root):
    """Single-writer POSIX prototype. Publish only after files and marker fsync."""
    validate_batch(batch)
    root = _directory(root)
    name = _id(batch["batch_id"])
    dest = root / name
    if dest.exists() or dest.is_symlink():
        raise FileExistsError(name)
    raw = _json(batch)
    manifest = _manifest(batch, raw)
    with tempfile.TemporaryDirectory(prefix=".kgm-stage-", dir=root) as temp:
        stage = Path(temp)
        _write(stage / "batch.json", raw)
        _write(stage / "manifest.json", _json(manifest))
        _write(stage / "COMPLETE", b"kgm.exchange.complete.v1\n")
        _sync(stage)
        if dest.exists() or dest.is_symlink():
            raise FileExistsError(name)
        os.rename(stage, dest)
        _sync(root)
    return manifest


def read_generation(root, name):
    root = _directory(root)
    path = root / _id(name)
    if path.is_symlink() or not path.is_dir():
        raise ValueError("missing complete generation")
    if {p.name for p in path.iterdir()} != {"batch.json", "manifest.json", "COMPLETE"}:
        raise ValueError("partial generation")
    for p in path.iterdir():
        s = p.lstat()
        if not stat.S_ISREG(s.st_mode) or s.st_nlink != 1:
            raise ValueError("linked or nonregular file")
    if (path / "COMPLETE").read_bytes() != b"kgm.exchange.complete.v1\n":
        raise ValueError("invalid completion marker")
    if (path / "batch.json").stat().st_size > 1048577 or (path / "manifest.json").stat().st_size > 4096:
        raise ValueError("oversized artifact")
    raw = (path / "batch.json").read_bytes()
    batch = json.loads(raw)
    manifest = json.loads((path / "manifest.json").read_bytes())
    validate_batch(batch)
    if batch["batch_id"] != name or manifest != _manifest(batch, raw):
        raise ValueError("manifest or batch mismatch")
    return batch
