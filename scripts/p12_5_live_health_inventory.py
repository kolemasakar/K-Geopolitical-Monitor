"""P12.5 controlled-live health/freshness/egress inventory probe.

The probe creates an ephemeral project-local runtime, installs explicit P12.1
portfolio governance for the ten measured public/free paths, executes P12.2
read-only adapters once, and emits a source-by-source operational snapshot.
Failures are measured data and do not make the workflow fail by themselves.
"""

from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
from tempfile import TemporaryDirectory

from kgeopolitical_monitor.adapter_framework import (
    FrameworkLiveSourceCollector,
    ReadOnlyHttpsTransportV2,
)
from kgeopolitical_monitor.operational_monitoring import OperationalMonitoringRuntime
from kgeopolitical_monitor.source_health_egress import (
    SourceHealthEgressService,
    build_health_probe_adapters,
    install_phase12_health_probe_governance,
    snapshot_to_jsonable,
)


def main() -> None:
    now = datetime.now(timezone.utc)
    with TemporaryDirectory(prefix="kgm-p125-") as temporary:
        runtime = OperationalMonitoringRuntime(Path(temporary) / "project")
        runtime.create_watch(
            "P12.5 controlled health probe",
            "Ukraine",
            60,
            watch_id="p125-health-live",
            created_at=now,
        )
        records = install_phase12_health_probe_governance(runtime, reviewed_at=now)
        if len(records) != 10:
            raise RuntimeError(f"P12.5 expected 10 governed source paths, got {len(records)}")

        transport = ReadOnlyHttpsTransportV2(
            timeout_seconds=20.0,
            max_bytes=4_000_000,
        )
        adapters = build_health_probe_adapters(
            transport,
            max_feed_entries=100,
            gdelt_max_records=25,
        )
        if len(adapters) != 10:
            raise RuntimeError(f"P12.5 expected 10 adapter paths, got {len(adapters)}")

        collector = FrameworkLiveSourceCollector(runtime, adapters)
        report = collector.collect("p125-health-live", now)
        snapshot = SourceHealthEgressService(runtime).snapshot(assessed_at=now)
        if snapshot.measured_source_count != 10:
            raise RuntimeError(
                "P12.5 measurement did not persist one current attempt for every governed source"
            )

        output = snapshot_to_jsonable(snapshot)
        output["collection"] = {
            "collection_id": report.collection_id,
            "status": report.status,
            "item_count": report.item_count,
            "source_success_count": report.source_success_count,
            "source_failure_count": report.source_failure_count,
            "failures": list(report.failures),
        }
        output["measurement_scope"] = {
            "source_count": 10,
            "includes": [
                "Consilium RSS",
                "GDELT DOC 2.0",
                "P12.3 authoritative pack",
                "P12.4 local-language/media pack",
            ],
            "production_runtime_mutated": False,
            "egress_restriction_applied": False,
        }
        print(json.dumps(output, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
