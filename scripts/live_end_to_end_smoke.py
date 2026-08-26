"""Read-only live-source acquisition plus project-local M8 processing smoke."""

from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path

from kgeopolitical_monitor.live_end_to_end import LiveEndToEndProcessor
from kgeopolitical_monitor.live_sources import (
    ConsiliumRssAdapter,
    GdeltDoc2Adapter,
    LiveSourceCollector,
    UrllibHttpTransport,
)
from kgeopolitical_monitor.operational_monitoring import OperationalMonitoringRuntime


def main() -> None:
    now = datetime.now(timezone.utc)
    project_root = Path.cwd()
    runtime = OperationalMonitoringRuntime(project_root)
    watch = runtime.create_watch(
        "Live Ukraine pilot",
        "Ukraine",
        60,
        watch_id="m8-live-smoke",
        created_at=now,
    )

    transport = UrllibHttpTransport(timeout_seconds=20.0, max_bytes=4_000_000)
    collector = LiveSourceCollector(
        runtime,
        [
            ConsiliumRssAdapter(transport),
            GdeltDoc2Adapter(transport, max_records=5, timespan="24h"),
        ],
    )
    collection = collector.collect(watch.watch_id, now)
    if collection.status != "COMPLETED":
        raise RuntimeError(
            f"live collection must complete with both sources; status={collection.status}; "
            f"failures={collection.failures}"
        )
    if collection.source_success_count != 2:
        raise RuntimeError("live collection did not validate both approved sources")
    if collection.item_count <= 0:
        raise RuntimeError("live collection returned no items")

    result = LiveEndToEndProcessor(runtime).process_collection(
        collection.collection_id,
        processed_at=now,
    )
    if not result.claims:
        raise RuntimeError("M8 analysis produced no claims")
    if len(result.findings) != len(result.claims):
        raise RuntimeError("M8 operational finding projection is incomplete")
    for finding in result.findings:
        if not any(ref.startswith("claim:") for ref in finding.evidence_refs):
            raise RuntimeError("finding is missing claim traceability")
        if not any(ref.startswith("raw_item:") for ref in finding.evidence_refs):
            raise RuntimeError("finding is missing raw-item traceability")
        if not any(ref.startswith("origin:") for ref in finding.evidence_refs):
            raise RuntimeError("finding is missing origin traceability")

    statuses: dict[str, int] = {}
    for claim in result.claims:
        statuses[claim.verification_status] = statuses.get(claim.verification_status, 0) + 1

    print(
        json.dumps(
            {
                "status": "success",
                "collection_status": collection.status,
                "source_success_count": collection.source_success_count,
                "collected_items": collection.item_count,
                "claims": len(result.claims),
                "findings": len(result.findings),
                "verification_statuses": statuses,
                "runtime_storage": "PROJECT_LOCAL_ONLY",
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
