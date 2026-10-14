"""Neutral owner-only filesystem primitives for durable research state."""
from __future__ import annotations
import fcntl
import json
import os
from pathlib import Path
import tempfile

def canonical_bytes(value):
    return (json.dumps(value, sort_keys=True, ensure_ascii=True,
                       separators=(",", ":")) + "\n").encode()

def real_directory(path):
    path = Path(path)
    if path.is_symlink() or not path.is_dir():
        raise ValueError("dedicated real directory required")
    return path

def atomic_replace(path, payload):
    if path.is_symlink():
        raise ValueError("symlink destination denied")
    with tempfile.NamedTemporaryFile(dir=path.parent, prefix=".stage-", delete=False) as f:
        stage = Path(f.name)
        try:
            os.fchmod(f.fileno(), 0o600)
            f.write(payload); f.flush(); os.fsync(f.fileno())
        except BaseException:
            stage.unlink(missing_ok=True); raise
    try:
        os.replace(stage, path)
        fd = os.open(path.parent, os.O_RDONLY | os.O_DIRECTORY)
        try: os.fsync(fd)
        finally: os.close(fd)
    finally:
        stage.unlink(missing_ok=True)

def lock(root):
    fd = os.open(root / ".research.lock", os.O_CREAT | os.O_RDWR | os.O_NOFOLLOW, 0o600)
    fcntl.flock(fd, fcntl.LOCK_EX)
    return fd

def consumer_outbox(root, consumer_id):
    directory = root / "outbox" / consumer_id
    if directory.is_symlink():
        raise ValueError("symlink outbox denied")
    directory.mkdir(mode=0o700, parents=False, exist_ok=True)
    return real_directory(directory)

def initialize(root):
    root = real_directory(root)
    for name in ("inbox", "outbox"):
        path = root / name
        if path.is_symlink():
            raise ValueError("symlink spool denied")
        path.mkdir(mode=0o700, exist_ok=True)
    return root
