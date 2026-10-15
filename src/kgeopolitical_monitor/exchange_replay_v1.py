"""Pure bounded consumer replay checks; no IO, DB, credentials or networking."""
from __future__ import annotations


class CursorExpired(ValueError):
    pass


class CursorGap(ValueError):
    pass


def select_replay(entries, *, after_sequence, minimum_available_sequence, max_records=100):
    """Select an uninterrupted bounded stream window for one consumer.

    Each entry has sequence, batch_id and sha256. The producer supplies an
    independently persisted monotonic sequence; this function cannot invent it.
    """
    if type(after_sequence) is not int or after_sequence < 0:
        raise ValueError("invalid cursor")
    if type(minimum_available_sequence) is not int or minimum_available_sequence < 1:
        raise ValueError("invalid retention floor")
    if type(max_records) is not int or not 1 <= max_records <= 100:
        raise ValueError("invalid replay bound")
    if after_sequence < minimum_available_sequence - 1:
        raise CursorExpired("CURSOR_EXPIRED")
    previous = None
    ids = set()
    for entry in entries:
        if not isinstance(entry, dict) or set(entry) != {"sequence", "batch_id", "sha256"}:
            raise ValueError("invalid ledger entry")
        sequence = entry["sequence"]
        batch_id = entry["batch_id"]
        digest = entry["sha256"]
        if type(sequence) is not int or sequence < minimum_available_sequence:
            raise ValueError("invalid sequence")
        if previous is not None and sequence != previous + 1:
            raise CursorGap("ledger contains a gap or reorder")
        if not isinstance(batch_id, str) or not batch_id or batch_id in ids:
            raise ValueError("duplicate or invalid batch")
        if not isinstance(digest, str) or len(digest) != 64 or any(c not in "0123456789abcdef" for c in digest):
            raise ValueError("invalid digest")
        previous = sequence
        ids.add(batch_id)
    if entries and entries[0]["sequence"] != minimum_available_sequence:
        raise CursorGap("retention floor mismatch")
    selected = [e for e in entries if e["sequence"] > after_sequence]
    if selected and selected[0]["sequence"] != after_sequence + 1:
        raise CursorGap("next batch missing")
    return selected[:max_records]
