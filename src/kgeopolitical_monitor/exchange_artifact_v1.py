"""Opt-in offline-only immutable exchange artifact writer.

No DB access, scheduler, network or consumer credentials. Caller supplies a
previously approved, fully projected v1 batch and a dedicated empty directory.
"""
from __future__ import annotations

from hashlib import sha256
import json
import os
from pathlib import Path
import tempfile
from typing import Any, Mapping

from .exchange_contract_v1 import validate_batch


def write_immutable_batch(batch: Mapping[str, Any], output_dir: str | Path) -> dict[str, str | int]:
    """Write one validated immutable JSON artifact and sidecar manifest atomically.

    Never overwrite any existing artifact; no shared DB or cross-project mount.
    Manifest is an integrity digest, NOT an authentication signature.
    """
    validate_batch(batch)
    directory = Path(output_dir)
    if directory.is_symlink() or not directory.is_dir():
        raise ValueError("pre-existing real output directory required")
    if directory.resolve() in (Path("/"), Path("/tmp")):
        raise ValueError("dedicated subdirectory required")
    name = batch["batch_id"]
    if not isinstance(name, str) or not name.isascii() or not name.replace("-", "").replace("_", "").isalnum():
        raise ValueError("batch_id must be filesystem-safe ASCII")
    payload = (json.dumps(batch, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False) + "\n").encode()
    digest = sha256(payload).hexdigest()
    artifact = directory / f"{name}.json"
    manifest = directory / f"{name}.manifest.json"
    manifest_bytes = (json.dumps({
        "schema_version": "kgm.exchange.manifest.v1",
        "batch_id": name, "artifact": artifact.name,
        "sha256": digest, "size_bytes": len(payload),
        "record_count": len(batch["records"]),
        "high_watermark_cursor": batch["high_watermark_cursor"],
    }, sort_keys=True, separators=(",", ":")) + "\n").encode()
    # No overwrite. Exclusive reservations prevent accidental duplicate publication.
    reserved: list[Path] = []
    temps: list[Path] = []
    try:
        for target in (artifact, manifest):
            fd = os.open(target, os.O_CREAT | os.O_EXCL | os.O_WRONLY | getattr(os, "O_NOFOLLOW", 0), 0o600)
            os.close(fd)
            reserved.append(target)
        for data in (payload, manifest_bytes):
            with tempfile.NamedTemporaryFile(dir=directory, prefix=".kgm-exchange-", delete=False) as f:
                temps.append(Path(f.name))
                f.write(data)
                f.flush()
                os.fsync(f.fileno())
        os.replace(temps[0], artifact)
        os.replace(temps[1], manifest)
    except BaseException:
        for path in temps + reserved:
            path.unlink(missing_ok=True)
        raise
    return {"batch_id": name, "sha256": digest, "record_count": len(batch["records"]),
            "artifact": artifact.name, "manifest": manifest.name}
