"""P12.4 controlled-live native-language media discovery smoke.

This probe is read-only operational acquisition/parser evidence. Each source is
queried with an explicit native-language term to avoid treating one English query
as semantically equivalent across languages. It does not establish factual truth,
independent-origin credit, coverage completeness or production/live readiness.
"""

from __future__ import annotations

from datetime import datetime, timezone
import json

from kgeopolitical_monitor.adapter_framework import ReadOnlyHttpsTransportV2
from kgeopolitical_monitor.local_language_discovery_pack import (
    LANGUAGE_SLICE_GAP_STATEMENT,
    build_local_language_adapter,
    local_language_specs,
)
from kgeopolitical_monitor.operational_monitoring import MonitoringWatch


def main() -> None:
    now = datetime.now(timezone.utc)
    transport = ReadOnlyHttpsTransportV2(timeout_seconds=20.0, max_bytes=4_000_000)
    results: list[dict[str, object]] = []
    success_count = 0
    failure_count = 0

    for spec in local_language_specs():
        adapter = build_local_language_adapter(
            transport,
            spec,
            max_entries=60,
            query_filter=True,
        )
        watch = MonitoringWatch(
            watch_id=f"p124-live-{spec.source_id}",
            name=f"P12.4 live {spec.source_name}",
            query=spec.native_query_term,
            cadence_minutes=60,
            created_at=now,
        )
        try:
            items = adapter.fetch(watch, now)
            success_count += 1
            results.append(
                {
                    "source_id": spec.source_id,
                    "source_name": spec.source_name,
                    "content_language": spec.content_language,
                    "native_query_term": spec.native_query_term,
                    "region_scope": list(spec.region_scope),
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
                    "source_id": spec.source_id,
                    "source_name": spec.source_name,
                    "content_language": spec.content_language,
                    "native_query_term": spec.native_query_term,
                    "region_scope": list(spec.region_scope),
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
                "language_gap_statement": LANGUAGE_SLICE_GAP_STATEMENT,
                "epistemic_note": (
                    "Media/source/language count is not independent-origin count; original-language "
                    "acquisition does not promote verification or prove language/region completeness."
                ),
            },
            ensure_ascii=False,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
