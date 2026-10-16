import json
import os
import pytest
from kgeopolitical_monitor.retention_plan_p243 import plan
from kgeopolitical_monitor.startup_attestation_p243 import startup_record
from kgeopolitical_monitor.live_sources import ConsiliumRssAdapter, GdeltDoc2Adapter, UrllibHttpTransport
from kgeopolitical_monitor import unattended_runner as runner

def test_attestation_real_adapters_no_network(tmp_path):
    adapters=[ConsiliumRssAdapter(UrllibHttpTransport()),GdeltDoc2Adapter(UrllibHttpTransport())]
    r=startup_record(tmp_path,adapters)
    assert r["checkout_sha_at_startup"] is None
    assert [s["source_id"] for s in r["sources"]]==["consilium-press-releases","gdelt-doc-2"]
    assert all(len(s["loaded_fetch_code_sha256"])==64 for s in r["sources"])
    assert r["secrets_included"] is False

def test_opt_in_parser_default():
    assert runner._parser().parse_args([]).startup_attestation is False
    assert runner._parser().parse_args(["--startup-attestation"]).startup_attestation is True

def test_hook_receives_constructed_adapter_ids(tmp_path,monkeypatch):
    class Runtime:
        database_path=tmp_path/"db"
        def __init__(self,*a): pass
    monkeypatch.setattr(runner,"OperationalMonitoringRuntime",Runtime)
    for n in ["ReproducibilityInstrumentedCollector","LiveEndToEndProcessor",
              "RuntimeHealthStore"]:
        monkeypatch.setattr(runner,n,lambda *a,**k: object())
    monkeypatch.setattr(runner,"LiveOperationalCycle",lambda *a: object())
    monkeypatch.setattr(runner,"UnattendedMonitoringService",lambda *a,**k: object())
    # Collector itself only validates adapters; no network is invoked.
    records=[]
    runner.build_unattended_service(tmp_path,attestation_sink=records.append)
    assert [s["source_id"] for s in records[0]["sources"]]==["consilium-press-releases","gdelt-doc-2"]

def test_retention_dry_run_preserves_newest_and_all_bytes(tmp_path):
    for n in range(3):
        p=tmp_path/f"artifact-{n}.json";p.write_text("{}");os.utime(p,(n,n))
    (tmp_path/"ledger-v2.jsonl").write_text("protected")
    before={p.name:p.read_bytes() for p in tmp_path.iterdir()}
    r=plan(tmp_path,now=100,min_age_seconds=10,keep_last=1)
    assert r["eligible"]==["artifact-1.json","artifact-0.json"]
    assert r["artifact_bytes"]==6 and r["eligible_bytes"]==4 and r["deleted"]==0
    assert {p.name:p.read_bytes() for p in tmp_path.iterdir()}==before

def test_retention_resource_bound_fails_without_partial_plan(tmp_path):
    for n in range(2): (tmp_path/str(n)).write_text("x")
    with pytest.raises(ValueError):
        plan(tmp_path,now=100,min_age_seconds=0,keep_last=1,max_files=1)

def test_retention_alias_denied(tmp_path):
    (tmp_path/"artifact-x.json").symlink_to(tmp_path/"missing")
    with pytest.raises(ValueError):
        plan(tmp_path,now=100,min_age_seconds=0,keep_last=1)

@pytest.mark.parametrize("kw",[{"now":float("nan")},{"min_age_seconds":-1},{"keep_last":0},{"max_files":10001}])
def test_retention_invalid_bounds(tmp_path,kw):
    args=dict(now=100,min_age_seconds=10,keep_last=1);args.update(kw)
    with pytest.raises(ValueError): plan(tmp_path,**args)
