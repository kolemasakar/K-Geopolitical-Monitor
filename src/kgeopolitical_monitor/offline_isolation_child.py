"""Fixed synthetic offline research probe used only inside a network namespace."""
from datetime import datetime, timezone
from pathlib import Path
import json

from .live_sources import LiveSourceItem
from .on_demand_dispatcher import OnDemandRequest, dispatch_offline_once


class SyntheticAdapter:
    offline_fixture_only = True
    source_class = "Official sources"
    def __init__(self, source_id):
        self.source_id = source_id
        self.source_name = source_id
    def fetch(self, watch, collected_at):
        return [LiveSourceItem(
            item_id="isolated-" + self.source_id,
            source_id=self.source_id, source_name=self.source_name,
            source_class=self.source_class,
            title="Synthetic event in offline namespace",
            summary="This is synthetic test data, not a real event.",
            original_url="https://" + self.source_id + ".example/fixture",
            collected_at=collected_at,
            reliability="official",
        )]


def verify_no_external_network_route():
    interfaces = sorted(p.name for p in Path('/sys/class/net').iterdir())
    if interfaces != ['lo']:
        raise RuntimeError('isolated process has a non-loopback network interface')
    routing = Path('/proc/net/route').read_text(encoding='utf-8').splitlines()[1:]
    if any(line.split()[1] == '00000000' for line in routing if len(line.split()) >= 2):
        raise RuntimeError('isolated process has a default IPv4 route')
    return interfaces


def main():
    interfaces = verify_no_external_network_route()
    result = dispatch_offline_once(
        OnDemandRequest(
            topic="synthetic", requested_at=datetime(2026, 10, 25, tzinfo=timezone.utc),
            request_id="network-isolated-fixture",
        ),
        adapters=[SyntheticAdapter("agency-a"), SyntheticAdapter("agency-b")],
    )
    print(json.dumps({
        "format": "KGM_O1_NETNS_SYNTHETIC_V1",
        "status": result.status,
        "collection_status": result.collection_status,
        "source_count": result.source_success_count,
        "evidence_count": result.evidence_count,
        "finding_count": result.finding_count,
        "only_synthetic_data": True,
        "network_interfaces": interfaces,
        "network_route_check": "NO_EXTERNAL_INTERFACE_OR_DEFAULT_IPV4_ROUTE",
    }, sort_keys=True))


if __name__ == "__main__":
    main()
