"""P21.2 bounded fresh source-health measurement.

Reuses the validated P12.5 ephemeral read-only collection path. This script
never binds the deployed runtime and never activates, adds, or mutates sources.
"""
from __future__ import annotations

from datetime import datetime, timezone
import argparse
import json
import platform
from pathlib import Path
from tempfile import TemporaryDirectory

from kgeopolitical_monitor.adapter_framework import FrameworkLiveSourceCollector, ReadOnlyHttpsTransportV2
from kgeopolitical_monitor.operational_monitoring import OperationalMonitoringRuntime
from kgeopolitical_monitor.source_health_egress import (
    SourceHealthEgressService,
    build_health_probe_adapters,
    install_phase12_health_probe_governance,
    snapshot_to_jsonable,
)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--vantage", required=True)
    parser.add_argument("--host-label", required=True)
    parser.add_argument("--checkout-sha", required=True)
    args = parser.parse_args()
    now = datetime.now(timezone.utc)

    with TemporaryDirectory(prefix="kgm-p212-") as temporary:
        runtime = OperationalMonitoringRuntime(Path(temporary) / "project")
        runtime.create_watch(
            "P21.2 fresh health probe", "global", 60,
            watch_id="p212-health-live", created_at=now,
        )
        records = install_phase12_health_probe_governance(runtime, reviewed_at=now)
        if len(records) != 10:
            raise RuntimeError(f"expected 10 governed source paths, got {len(records)}")

        transport = ReadOnlyHttpsTransportV2(timeout_seconds=20.0, max_bytes=4_000_000)
        adapters = build_health_probe_adapters(transport, max_feed_entries=100, gdelt_max_records=25)
        if len(adapters) != 10:
            raise RuntimeError(f"expected 10 adapters, got {len(adapters)}")

        report = FrameworkLiveSourceCollector(runtime, adapters).collect("p212-health-live", now)
        snapshot = SourceHealthEgressService(runtime).snapshot(assessed_at=now)
        if snapshot.measured_source_count != 10:
            raise RuntimeError("measurement incomplete")

        output = snapshot_to_jsonable(snapshot)
        output["collection"] = {
            "collection_id": report.collection_id,
            "status": report.status,
            "item_count": report.item_count,
            "source_success_count": report.source_success_count,
            "source_failure_count": report.source_failure_count,
            "failures": list(report.failures),
        }
        output["phase21_measurement"] = {
            "purpose": "P21.2 fresh operational health baseline",
            "measurement_vantage": args.vantage,
            "host_label": args.host_label,
            "architecture": platform.machine(),
            "python": platform.python_version(),
            "canonical_checkout_sha": args.checkout_sha,
            "production_runtime_mutated": False,
            "service_restart": False,
            "runtime_deployment": False,
            "source_expansion": False,
            "measurement_note": (
                "Ephemeral read-only canonical-checkout probe; this measures source behavior "
                "from the named vantage and does not claim deployed runtime state."
            ),
        }
        print(json.dumps(output, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
