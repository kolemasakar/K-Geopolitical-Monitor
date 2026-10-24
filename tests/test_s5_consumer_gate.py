"""S5.3: pure local scope checks, zero transport or external consumer activation."""
import pytest
from kgeopolitical_monitor.research_consumer_gate_s5 import authorize_offline_view, ConsumerNotAuthorized


def test_known_scope_is_local_only():
    authorize_offline_view(consumer_id="fixture-a",scope="offline-read",grants={"fixture-a":("offline-read",)})


@pytest.mark.parametrize("consumer,scope,mode,grants", [
    ("fixture-b","offline-read","NO_SEND",{"fixture-a":("offline-read",)}),
    ("fixture-a","offline-write","NO_SEND",{"fixture-a":("offline-read",)}),
    ("fixture-a","offline-read","SEND",{"fixture-a":("offline-read",)}),
    ("fixture-a","offline-read","NO_SEND",{}),
    ("","offline-read","NO_SEND",{"":("offline-read",)}),
    ("fixture-a","","NO_SEND",{"fixture-a":("",)}),
])
def test_unknown_consumer_scope_and_send_fail_closed(consumer,scope,mode,grants):
    with pytest.raises(ConsumerNotAuthorized):
        authorize_offline_view(consumer_id=consumer,scope=scope,mode=mode,grants=grants)
