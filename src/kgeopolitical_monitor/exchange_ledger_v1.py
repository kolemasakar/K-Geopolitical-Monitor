"""Offline single-writer durable producer ledger prototype.

No DB, network, credentials or live exporter. Use only on a dedicated private
POSIX filesystem with one producer and already validated complete generations.
"""
import fcntl
import json
import os
from pathlib import Path

from .exchange_generation_v1 import read_generation
from .exchange_replay_v1 import select_replay


def append_published(root, batch_id):
    root = Path(root)
    if root.is_symlink() or not root.is_dir():
        raise ValueError("invalid ledger directory")
    batch = read_generation(root, batch_id)
    import hashlib
    raw = (root / batch_id / "batch.json").read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    lock = root / ".ledger.lock"
    with open(lock, "a+b") as handle:
        fcntl.flock(handle, fcntl.LOCK_EX)
        ledger = root / "ledger.jsonl"
        entries = []
        if ledger.exists():
            for line in ledger.read_text().splitlines():
                entries.append(json.loads(line))
        for entry in entries:
            if entry["batch_id"] == batch_id:
                if entry["sha256"] == digest:
                    return entry
                raise ValueError("batch ID digest conflict")
        sequence = entries[-1]["sequence"] + 1 if entries else 1
        entry = {"sequence": sequence, "batch_id": batch_id, "sha256": digest}
        fd = os.open(ledger, os.O_CREAT | os.O_WRONLY | os.O_APPEND | getattr(os, "O_NOFOLLOW", 0), 0o600)
        with os.fdopen(fd, "ab") as out:
            out.write((json.dumps(entry, sort_keys=True, separators=(",", ":")) + "\n").encode())
            out.flush()
            os.fsync(out.fileno())
        parent = os.open(root, os.O_RDONLY | getattr(os, "O_DIRECTORY", 0))
        try:
            os.fsync(parent)
        finally:
            os.close(parent)
        return entry


def replay_published(root, after_sequence, minimum_available_sequence=1, max_records=100):
    root = Path(root)
    if root.is_symlink() or not root.is_dir():
        raise ValueError("invalid ledger directory")
    ledger = root / "ledger.jsonl"
    entries = [json.loads(line) for line in ledger.read_text().splitlines()] if ledger.exists() else []
    return select_replay(entries, after_sequence=after_sequence,
                         minimum_available_sequence=minimum_available_sequence,
                         max_records=max_records)
