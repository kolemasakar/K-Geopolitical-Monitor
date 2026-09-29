"""Standalone offline KGM-only acceptance matrix.

Run with: PYTHONPATH=src python -m kgeopolitical_monitor.research_offline_acceptance_v1
No provider calls, cross-host transport or production writes.
"""
from __future__ import annotations
import json
import tempfile
from .research_durable_lifecycle_v1 import admit, advance, recovery_snapshot
from .research_spool_v1 import retrieve
from .research_typed_spool_v1 import publish_typed_fixture


def run_fixture(request, typed_result):
    policy = {request["consumer_id"]: request["policy_version"]}
    with tempfile.TemporaryDirectory(prefix="kgm-synthetic-") as directory:
        admitted = admit(directory, request, allowed_consumers=policy, max_pending_per_consumer=1)
        advance(directory, request["consumer_id"], request["request_id"], "ACCEPTED",
                allowed_consumers=policy, at_utc=request["requested_at_utc"])
        pending = recovery_snapshot(directory, allowed_consumers=policy)
        published = publish_typed_fixture(directory, request["consumer_id"],
                                          request["request_id"], typed_result,
                                          allowed_consumers=policy)
        received = retrieve(directory, request["consumer_id"], request["request_id"],
                            allowed_consumers=policy)
        if published != received or admitted["request_digest"] != received["request_digest"]:
            raise ValueError("synthetic acceptance mismatch")
        return {"mode": "KGM_OFFLINE_SYNTHETIC_ONLY", "request_id": request["request_id"],
                "consumer_id": request["consumer_id"],
                "accepted": True, "pending_after_restart_snapshot": len(pending),
                "typed_result_verified": True,
                "artifact_sha256": received["sha256"],
                "cross_host_exchange_tested": False, "real_corpus_tested": False}


if __name__ == "__main__":
    raise SystemExit("Supply explicit synthetic fixtures through run_fixture; no default real-data mode")
