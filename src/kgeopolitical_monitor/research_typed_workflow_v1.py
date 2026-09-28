"""Owner-only offline entry point for the durable typed synthetic workflow.

This is the supported fixture-facing API. Older minimal fixture modules are
retained for compatibility and must not be used by this workflow.
"""
from __future__ import annotations
from .research_durable_lifecycle_v1 import admit, advance
from .research_completion_v1 import complete_or_reconcile
from .research_recovery_pass_v1 import recovery_pass
from .research_typed_result_v1 import validate_typed_result


def accept_request(root, request, *, allowed_consumers, max_pending_per_consumer=10,
                   accepted_at_utc, deadline_utc=None):
    saved = admit(root, request, allowed_consumers=allowed_consumers,
                  max_pending_per_consumer=max_pending_per_consumer,
                  deadline_utc=deadline_utc)
    if saved["status"] == "RECEIVED":
        return advance(root, request["consumer_id"], request["request_id"], "ACCEPTED",
                       allowed_consumers=allowed_consumers, at_utc=accepted_at_utc)
    return saved


def begin_processing(root, consumer, request_id, *, allowed_consumers, at_utc):
    return advance(root, consumer, request_id, "PROCESSING",
                   allowed_consumers=allowed_consumers, at_utc=at_utc)


def publish_and_complete(root, consumer, request_id, result, *,
                         allowed_consumers, at_utc):
    # The strict validator also runs inside the locked completion operation.
    return complete_or_reconcile(root, consumer, request_id,
                                 allowed_consumers=allowed_consumers,
                                 result=result, at_utc=at_utc)


def recover_pending(root, *, allowed_consumers, observed_at_utc,
                    deadlines=None, max_items=10, after_key=None):
    return recovery_pass(root, allowed_consumers=allowed_consumers,
                         observed_at_utc=observed_at_utc,
                         deadlines=deadlines, max_items=max_items,
                         after_key=after_key)


def register_request_deadline(root, consumer, request_id, *, allowed_consumers,
                              deadline_utc):
    from .research_deadline_registry_v1 import register_deadline
    return register_deadline(root, consumer, request_id,
                             allowed_consumers=allowed_consumers,
                             deadline_utc=deadline_utc)


def recover_registered(root, *, allowed_consumers, observed_at_utc, max_items=10,
                       after_key=None):
    from .research_deadline_registry_v1 import registered_deadlines
    deadlines = registered_deadlines(root, allowed_consumers=allowed_consumers)
    return recover_pending(root, allowed_consumers=allowed_consumers,
                           observed_at_utc=observed_at_utc,
                           deadlines=deadlines, max_items=max_items,
                           after_key=after_key)
