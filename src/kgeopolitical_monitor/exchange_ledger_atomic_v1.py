"""Crash-consistent offline producer ledger candidate.

A private POSIX directory, cooperative writer/reader flock, atomic whole-ledger
replacement and directory fsync. No live KGM reader or network.
"""
import fcntl
import hashlib
import json
import os
from pathlib import Path
import tempfile

from .exchange_generation_v1 import read_generation
from .exchange_replay_v1 import select_replay


def _read(path):
    if not path.exists():
        return []
    data = path.read_bytes()
    if data and not data.endswith(b"\n"):
        raise ValueError("torn ledger")
    rows = [json.loads(line) for line in data.splitlines()]
    select_replay(rows, after_sequence=0, minimum_available_sequence=1,
                  max_records=100) if rows else None
    return rows


def _root(path):
    path = Path(path)
    if path.is_symlink() or not path.is_dir():
        raise ValueError("dedicated directory required")
    return path


def _sync_directory(path):
    fd = os.open(path, os.O_RDONLY | getattr(os, "O_DIRECTORY", 0))
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def _lock(root, exclusive):
    fd = os.open(root / ".ledger-v2.lock", os.O_CREAT | os.O_RDWR | getattr(os, "O_NOFOLLOW", 0), 0o600)
    fcntl.flock(fd, fcntl.LOCK_EX if exclusive else fcntl.LOCK_SH)
    return fd


def append(root, batch_id):
    root = _root(root)
    batch = read_generation(root, batch_id)
    digest = hashlib.sha256((root / batch_id / "batch.json").read_bytes()).hexdigest()
    fd = _lock(root, True)
    try:
        ledger = root / "ledger-v2.jsonl"
        rows = _read(ledger)
        for row in rows:
            if row["batch_id"] == batch["batch_id"]:
                if row["sha256"] != digest:
                    raise ValueError("batch digest conflict")
                return row
        row = {"sequence": rows[-1]["sequence"] + 1 if rows else 1,
               "batch_id": batch_id, "sha256": digest}
        rows.append(row)
        with tempfile.NamedTemporaryFile(dir=root, prefix=".ledger-v2-stage-", delete=False) as f:
            temp = Path(f.name)
            try:
                os.fchmod(f.fileno(), 0o600)
                for item in rows:
                    f.write((json.dumps(item, sort_keys=True, separators=(",", ":")) + "\n").encode())
                f.flush()
                os.fsync(f.fileno())
            except BaseException:
                temp.unlink(missing_ok=True)
                raise
        try:
            os.replace(temp, ledger)
            _sync_directory(root)
        finally:
            temp.unlink(missing_ok=True)
        return row
    finally:
        os.close(fd)


def replay(root, after_sequence, max_records=100):
    root = _root(root)
    fd = _lock(root, False)
    try:
        rows = _read(root / "ledger-v2.jsonl")
        return select_replay(rows, after_sequence=after_sequence,
                             minimum_available_sequence=1, max_records=max_records)
    finally:
        os.close(fd)
