"""Bounded offline synthetic recovery pass; no daemon, network or providers.

Reconcile published typed artifacts before considering explicit deadlines.
Unpublished work remains pending unless its caller-supplied deadline passed.
"""
from __future__ import annotations
from .research_durable_lifecycle_v1 import recovery_snapshot
from .research_completion_v1 import complete_or_reconcile
from .research_expiry_v1 import expire_stale
from .research_request_v1 import _utc


def recovery_pass(root, *, allowed_consumers, observed_at_utc,
                  deadlines=None, max_items=10, after_key=None):
    _utc(observed_at_utc)
    if type(max_items) is not int or not 1 <= max_items <= 100:
        raise ValueError("invalid recovery bound")
    if deadlines is None:
        deadlines = {}
    if not isinstance(deadlines, dict):
        raise ValueError("invalid deadlines")
    # Fail closed on unknown deadline shapes, even when there is no pending work.
    for key, value in deadlines.items():
        if not isinstance(key, tuple) or len(key) != 2 or not all(isinstance(x, str) for x in key):
            raise ValueError("invalid deadline key")
        _utc(value)
    if after_key is not None and (not isinstance(after_key, tuple) or len(after_key) != 2 or not all(isinstance(x, str) for x in after_key)):
        raise ValueError("invalid recovery cursor")
    pending = recovery_snapshot(root, allowed_consumers=allowed_consumers)
    # A caller may persist the returned cursor to avoid starving later keys.
    # Snapshot scanning remains O(total inbox); only processing is bounded.
    if after_key is not None:
        later = [item for item in pending if (item["consumer_id"], item["request_id"]) > after_key]
        earlier = [item for item in pending if (item["consumer_id"], item["request_id"]) <= after_key]
        pending = later + earlier
    report = {"reconciled": [], "expired": [], "pending": [], "errors": [],
              "remaining": max(0, len(pending) - max_items),
              "next_cursor": after_key}
    for item in pending[:max_items]:
        consumer, request_id = item["consumer_id"], item["request_id"]
        key = (consumer, request_id)
        report["next_cursor"] = key
        try:
            # Attempt verified artifact reconciliation first, including after a crash.
            if item["status"] == "PROCESSING":
                try:
                    complete_or_reconcile(root, consumer, request_id,
                                          allowed_consumers=allowed_consumers,
                                          at_utc=observed_at_utc)
                    report["reconciled"].append(key)
                    continue
                except ValueError as error:
                    if str(error) != "result not yet published":
                        raise
            deadline = deadlines.get(key)
            if deadline is not None and _utc(observed_at_utc) >= _utc(deadline):
                expire_stale(root, consumer, request_id,
                             allowed_consumers=allowed_consumers,
                             deadline_utc=deadline,
                             observed_at_utc=observed_at_utc)
                report["expired"].append(key)
            else:
                report["pending"].append(key)
        except (ValueError, PermissionError, OSError, KeyError, TypeError) as error:
            report["errors"].append({"key": key, "error": type(error).__name__})
    return report
