"""Deny-by-default S5.3 source and scope contract tests."""
import pytest
from kgeopolitical_monitor.exchange_consumer_policy_s5 import ConsumerGrant,authorize_export

G=ConsumerGrant("k-sentinel","kgm-exchange-v1","news-research",enabled=True)
def request(**kw):
    defaults=dict(consumer="k-sentinel",contract="kgm-exchange-v1",scope="news-research",grants=[G],source_state="COMPLETE",verification="VERIFIED")
    defaults.update(kw)
    return authorize_export(**defaults)

def test_exact_grant_returns_no_send_contract():
    x=request()
    assert x["offline_approved"] is True and x["sent"] is False

@pytest.mark.parametrize("override",[
    {"grants":[]},{"consumer":"k-trader"},{"contract":"kgm-exchange-v2"},
    {"scope":"trading-signals"},{"source_state":"PARTIAL"},
    {"source_state":"UNKNOWN"},{"verification":"UNVERIFIED"},
    {"verification":"REJECTED"},{"dry_run":False},
])
def test_no_implicit_consumer_or_source_authority(override):
    with pytest.raises(PermissionError):
        request(**override)

def test_disputed_can_only_pass_approved_explicit_scope():
    assert request(verification="DISPUTED")["sent"] is False
    with pytest.raises(PermissionError):
        request(verification="DISPUTED",scope="trading-signals")
