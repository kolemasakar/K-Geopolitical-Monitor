"""Read-only live smoke for approved M7 public-source adapters."""

from __future__ import annotations

from datetime import datetime, timezone
import json

from kgeopolitical_monitor.live_sources import (
    ConsiliumRssAdapter,
    GdeltDoc2Adapter,
    UrllibHttpTransport,
)
from kgeopolitical_monitor.operational_monitoring import MonitoringWatch


def main() -> None:
    now = datetime.now(timezone.utc)
    transport = UrllibHttpTransport(timeout_seconds=20.0, max_bytes=4_000_000)

    checks = [
        (
            "consilium-press-releases",
            ConsiliumRssAdapter(transport),
            MonitoringWatch(
                watch_id="smoke-consilium",
                name="Consilium Ukraine",
                query="Ukraine",
                cadence_minutes=60,
                created_at=now,
            ),
        ),
        (
            "gdelt-doc-2",
            GdeltDoc2Adapter(transport, max_records=5, timespan="24h"),
            MonitoringWatch(
                watch_id="smoke-gdelt",
                name="GDELT Ukraine",
                query="Ukraine",
                cadence_minutes=60,
                created_at=now,
            ),
        ),
    ]

    results = []
    for source_id, adapter, watch in checks:
        items = adapter.fetch(watch, now)
        results.append(
            {
                "source_id": source_id,
                "status": "success",
                "parsed_items": len(items),
            }
        )

    print(json.dumps({"status": "success", "sources": results}, sort_keys=True))


if __name__ == "__main__":
    main()
