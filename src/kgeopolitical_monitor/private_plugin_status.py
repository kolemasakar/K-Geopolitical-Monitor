"""Sanitized, bounded, side-effect-free owner Plugin status projection.

Consumes an existing BackendStateReader-compatible object. This module does not
open databases, start network listeners, or require RDC.
"""
from collections.abc import Mapping
from typing import Any

MAX_DEGRADED_SOURCES = 20


def kgm_get_status(reader: Any) -> dict[str, object]:
    """Return a narrow read projection; never infer collection continuity."""
    summary = reader.state_summary()
    if not isinstance(summary, Mapping):
        raise ValueError("invalid state summary")
    raw_cycle = summary.get("last_monitoring_cycle")
    cycle = None
    if isinstance(raw_cycle, Mapping):
        cycle = {
            key: raw_cycle.get(key)
            for key in ("run_id", "status", "started_at", "completed_at")
        }
    degraded = reader.degraded_sources()
    if not isinstance(degraded, list):
        raise ValueError("invalid degraded sources")
    safe_sources = [
        {
            "source_id": item.get("source_id"),
            "availability_state": item.get("availability_state"),
            "observed_at": item.get("observed_at"),
        }
        for item in degraded[:MAX_DEGRADED_SOURCES]
        if isinstance(item, Mapping)
    ]
    return {
        "schema_version": "0.1",
        "active_monitoring_watches": summary.get("active_monitoring_watches"),
        "last_monitoring_cycle": cycle,
        "last_unattended_cycle_at": summary.get("last_unattended_cycle_at"),
        "unattended_cycle_instrumentation": summary.get(
            "unattended_cycle_instrumentation", "UNKNOWN"
        ),
        "degraded_sources": safe_sources,
        "degraded_sources_truncated": len(degraded) > MAX_DEGRADED_SOURCES,
        "service_health": "NOT_MEASURED",
        "acquisition_continuity": "NOT_VERIFIED",
    }
