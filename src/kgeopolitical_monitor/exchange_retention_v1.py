"""Fail-closed retention planning for KGM exchange, offline only.

This module never deletes batches. A retention decision must be applied only
after an approved checkpoint snapshot and explicit consumer expiry handling.
"""
from __future__ import annotations

from datetime import datetime, timezone, timedelta


class SnapshotRequired(ValueError):
    pass


def plan_retention(entries, *, now_utc, retention_days, acknowledged_sequences):
    """Return a non-destructive plan; never prune a required consumer cursor."""
    if not isinstance(now_utc, datetime) or now_utc.tzinfo is None:
        raise ValueError("timezone-aware now required")
    if type(retention_days) is not int or not 1 <= retention_days <= 365:
        raise ValueError("retention days outside approved planning bounds")
    if not isinstance(acknowledged_sequences, dict) or not acknowledged_sequences:
        raise ValueError("explicit independent consumer checkpoints required")
    for consumer, cursor in acknowledged_sequences.items():
        if not isinstance(consumer, str) or not consumer or type(cursor) is not int or cursor < 0:
            raise ValueError("invalid consumer checkpoint")
    cutoff = now_utc.astimezone(timezone.utc) - timedelta(days=retention_days)
    previous = 0
    expired = []
    for entry in entries:
        if not isinstance(entry, dict) or set(entry) != {"sequence", "created_utc"}:
            raise ValueError("invalid retention entry")
        seq = entry["sequence"]
        if type(seq) is not int or seq != previous + 1:
            raise ValueError("ledger sequence must start at one and be contiguous")
        previous = seq
        stamp = datetime.fromisoformat(entry["created_utc"].replace("Z", "+00:00"))
        if stamp.tzinfo is None:
            raise ValueError("UTC timestamp required")
        if stamp.astimezone(timezone.utc) < cutoff:
            expired.append(seq)
    eligible_through = expired[-1] if expired else 0
    if any(seq > previous for seq in acknowledged_sequences.values()):
        raise ValueError("consumer checkpoint exceeds producer head")
    blocked = sorted(name for name, seq in acknowledged_sequences.items()
                     if seq < eligible_through)
    return {"eligible_through": eligible_through,
            "next_minimum_sequence": eligible_through + 1,
            "blocked_consumers": blocked,
            "requires_approved_snapshot": bool(blocked),
            "deletion_authorized": False}


def require_safe_retention(plan, *, snapshot_approved=False):
    """No implicit snapshot, no automatic deletion."""
    if plan["requires_approved_snapshot"] or not snapshot_approved:
        raise SnapshotRequired("approved checkpoint snapshot and consumer expiry handling required")
    return {"next_minimum_sequence": plan["next_minimum_sequence"],
            "deletion_authorized": False}
