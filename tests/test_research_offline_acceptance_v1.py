"""KGM-only acceptance bundle using explicit synthetic request and typed response."""
from kgeopolitical_monitor.research_offline_acceptance_v1 import run_fixture
from test_research_typed_result_v1 import typed


def test_offline_acceptance_without_ktrader_or_network():
    request, result = typed()
    report = run_fixture(request, result)
    assert report["accepted"] and report["typed_result_verified"]
    assert report["pending_after_restart_snapshot"] == 1
    assert not report["cross_host_exchange_tested"]
    assert not report["real_corpus_tested"]
