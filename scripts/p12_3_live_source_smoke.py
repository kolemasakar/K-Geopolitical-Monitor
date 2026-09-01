"""P12.3 controlled-live read-only smoke for the authoritative source pack.

This is operational acquisition evidence only. It does not establish factual
verification, independent-origin credit, coverage completeness or production state.
Individual source failures are reported and isolated rather than hidden.
"""

from __future__ import annotations

from datetime import datetime, timezone
import json

from kgeopolitical_monitor.adapter_framework import ReadOnlyHttpsTransportV2
from kgeopolitical_monitor.authoritative_source_pack import build_source_pack_adapters
from kgeopolitical_monitor.operational_monitoring import MonitoringWatch


def main() -> None:
    now = datetime.now(timezone.utc)
    transport = ReadOnlyHttpsTransportV2(timeout_seconds=20.0, max_bytes=4_000_000)
    adapters = build_source_pack_adapters(transport, max_entries=50)

    results: list[dict[str, object]] = []
    success_count = 0
    failure_count = 0

    for adapter in adapters:
        watch = MonitoringWatch(
            watch_id=f"p123-live-{adapter.source_id}",
            name=f"P12.3 live {adapter.source_name}",
            query="Ukraine",
            cadence_minutes=60,
            created_at=now,
        )
        try:
            items = adapter.fetch(watch, now)
            success_count += 1
            results.append(
                {
                    "source_id": adapter.source_id,
                    "source_name": adapter.source_name,
                    "adapter_identity": adapter.adapter_identity,
                    "request_locator": adapter.last_request_locator,
                    "status": "SUCCESS",
                    "parsed_items": len(items),
                }
            )
        except Exception as exc:
            failure_count += 1
            results.append(
                {
                    "source_id": adapter.source_id,
                    "source_name": adapter.source_name,
                    "adapter_identity": adapter.adapter_identity,
                    "request_locator": adapter.last_request_locator,
                    "status": "FAILED",
                    "parsed_items": 0,
                    "error_type": exc.__class__.__name__,
                    "error": str(exc).strip() or exc.__class__.__name__,
                }
            )

    if success_count == 0:
        overall = "FAILED"
    elif failure_count:
        overall = "PARTIAL"
    else:
        overall = "COMPLETED"

    print(
        json.dumps(
            {
                "status": overall,
                "checked_at": now.isoformat(),
                "source_success_count": success_count,
                "source_failure_count": failure_count,
                "sources": results,
                "epistemic_note": (
                    "Acquisition success/failure is operational evidence only; source count "
                    "is not independent-origin count and does not promote verification."
                ),
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
