"""Owner-controlled one-time public source probe: aggregate statuses, no report send.

NOT a hardened network-sandbox or production user research interface.
Only run in approved ephemeral environment with no secrets or production mounts.
"""
from __future__ import annotations

from datetime import datetime, timezone
from hashlib import sha256
import json
import os
import sqlite3
from tempfile import TemporaryDirectory

from .live_sources import GdeltDoc2Adapter, ConsiliumRssAdapter, LiveSourceCollector
from .on_demand_gdacs import GdacsRssAdapter
from .on_demand_request_gate import authorize_public_probe
from .on_demand_source_policy import RestrictedSourcePolicy, RestrictedSourceTransport
from .operational_monitoring import OperationalMonitoringRuntime
from .p5_probe_diagnostics import classify_attempt


def probe_public_once(*, topic: str, transport=None) -> dict[str, object]:
    """Exactly one bounded collection; no background schedule, sends, or raw output."""
    if transport is None:
        transport = RestrictedSourceTransport(RestrictedSourcePolicy(
            max_requests=3, timeout_seconds=7, max_bytes_per_response=512_000
        ))
    now = datetime.now(timezone.utc)
    with TemporaryDirectory(prefix="kgm-p5-live-probe-") as temp_root:
        runtime = OperationalMonitoringRuntime(temp_root)
        watch = runtime.create_watch(
            name="Ephemeral public source probe", query=topic,
            cadence_minutes=1440, enabled=True, created_at=now,
        )
        adapters = [
            GdacsRssAdapter(transport, max_records=10),
            ConsiliumRssAdapter(transport),
            GdeltDoc2Adapter(transport, max_records=10, timespan="24h"),
        ]
        report = LiveSourceCollector(runtime, adapters).collect(watch.watch_id, now)
        # Collection, not claim verification. A PARTIAL outcome must remain PARTIAL.
        with sqlite3.connect(runtime.database_path) as db:
            rows = db.execute(
                "SELECT source_id, status, item_count, error FROM source_collection_attempts "
                "WHERE collection_id=? ORDER BY source_id",
                (report.collection_id,),
            ).fetchall()
        result = {
            "format": "KGM_P5_4_PUBLIC_SOURCE_PROBE_V1",
            "observed_at": now.isoformat(),
            "topic_sha256": sha256(topic.encode("utf-8")).hexdigest(),
            "network_policy": "IN_PROCESS_ALLOWLIST_ONLY_NOT_OS_EGRESS_ATTESTATION",
            "send": "NONE",
            "watch_persistence": "EPHEMERAL_ONLY",
            "collection_status": report.status,
            "item_count": report.item_count,
            "source_success_count": report.source_success_count,
            "source_failure_count": report.source_failure_count,
            "sources": [dict({"source_id": sid, "status": status, "item_count": count},
                             **classify_attempt(status=status, item_count=count, error=error))
                        for sid, status, count, error in rows],
            "analysis": "NOT_EXECUTED",
            "independent_claim_verification": "NOT_ATTESTED",
        }
    return result


def main() -> None:
    gate = authorize_public_probe(
        repository=os.environ["KGM_REPOSITORY"],
        actor=os.environ["KGM_ACTOR"],
        ref=os.environ["KGM_REF"],
        event_name=os.environ["KGM_EVENT"],
        mode=os.environ["KGM_PROBE_MODE"],
        topic=os.environ["KGM_TOPIC"],
        request_id=os.environ["KGM_REQUEST_ID"],
    )
    if os.environ.get("KGM_PROBE_MODE") != "PUBLIC_SOURCE_READONLY":
        raise PermissionError("live public probe requires explicit approved mode")
    if gate.topic_sha256 != sha256(os.environ["KGM_TOPIC"].encode()).hexdigest():
        raise RuntimeError("topic digest mismatch")
    print(json.dumps(probe_public_once(topic=os.environ["KGM_TOPIC"]), sort_keys=True))


if __name__ == "__main__":
    main()
