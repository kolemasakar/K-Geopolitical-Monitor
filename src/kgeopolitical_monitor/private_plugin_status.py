"""Bounded owner-only status projection. No database, network, or RDC access."""
from collections.abc import Mapping
from typing import Any
import re

MAX_DEGRADED_SOURCES = 20
SAFE_ID = re.compile(r"^[A-Za-z0-9_.:-]{1,96}$")
SAFE_STATUS = re.compile(r"^[A-Z][A-Z0-9_]{0,39}$")
SAFE_TIME = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d{1,6})?(?:Z|[+-]\d{2}:\d{2})$")
MAX_WATCHES = 100000


def _safe_string(value: object, pattern: re.Pattern[str]) -> str | None:
    return value if isinstance(value, str) and pattern.fullmatch(value) else None


def _safe_count(value: object) -> int | None:
    return value if type(value) is int and 0 <= value <= MAX_WATCHES else None


def _safe_cycle(value: object) -> dict[str, object] | None:
    if not isinstance(value, Mapping):
        return None
    return {
        "run_id": _safe_string(value.get("run_id"), SAFE_ID),
        "status": _safe_string(value.get("status"), SAFE_STATUS),
        "started_at": _safe_string(value.get("started_at"), SAFE_TIME),
        "completed_at": _safe_string(value.get("completed_at"), SAFE_TIME),
    }


def kgm_get_status(reader: Any) -> dict[str, object]:
    """Whitelist fields and values; never infer runtime or collection continuity.

    The caller must supply an authenticated reader with bounded upstream queries.
    This projection is not itself an authorization boundary.
    """
    summary = reader.state_summary()
    if not isinstance(summary, Mapping):
        raise ValueError("invalid state summary")
    degraded = reader.degraded_sources()
    if not isinstance(degraded, list):
        raise ValueError("invalid degraded sources")
    safe_sources = []
    for item in degraded[:MAX_DEGRADED_SOURCES]:
        if not isinstance(item, Mapping):
            continue
        safe_sources.append({
            "source_id": _safe_string(item.get("source_id"), SAFE_ID),
            "availability_state": _safe_string(item.get("availability_state"), SAFE_STATUS),
            "observed_at": _safe_string(item.get("observed_at"), SAFE_TIME),
        })
    instrumentation = _safe_string(
        summary.get("unattended_cycle_instrumentation"), SAFE_STATUS
    )
    return {
        "schema_version": "0.2",
        "active_monitoring_watches": _safe_count(summary.get("active_monitoring_watches")),
        "last_monitoring_cycle": _safe_cycle(summary.get("last_monitoring_cycle")),
        "last_unattended_cycle_at": _safe_string(
            summary.get("last_unattended_cycle_at"), SAFE_TIME
        ),
        "unattended_cycle_instrumentation": instrumentation or "UNKNOWN",
        "degraded_sources": safe_sources,
        "degraded_sources_truncated": len(degraded) > MAX_DEGRADED_SOURCES,
        "service_health": "NOT_MEASURED",
        "acquisition_continuity": "NOT_VERIFIED",
    }
