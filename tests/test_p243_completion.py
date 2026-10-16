import pytest
from kgeopolitical_monitor.retention_rehearsal_p243 import rehearse,TTL
from kgeopolitical_monitor.resource_observation_p243 import observe
from kgeopolitical_monitor.resource_probe_p243 import probe

NOW=100*86400
def row(key,kind,age):
    return {"id":key,"kind":kind,"created":NOW-age,"payload":b"test"}
def test_retention_policies_and_references():
    data=[row("expired","artifact",8*86400),row("protected","artifact",8*86400),
          row("ledger","ledger",99*86400),row("replay","replay_required",99*86400),
          row("evidence","evidence",99*86400),row("fresh","trace",86400)]
    before=[dict(x) for x in data]
    r=rehearse(data,now=NOW,protected_ids=["protected"])
    assert r["deleted_in_disposable_copy"]==["expired"] and r["restore"]=="PASS"
    assert set(r["retained"])=={"protected","ledger","replay","evidence","fresh"}
    assert data==before and r["production_modified"] is False
@pytest.mark.parametrize("kind",list(TTL))
def test_exact_age_policy_boundary(kind):
    data=[row("old",kind,TTL[kind]),row("new",kind,TTL[kind]-1)]
    assert rehearse(data,now=NOW)["deleted_in_disposable_copy"]==["old"]
@pytest.mark.parametrize("data",[ [row("../escape","raw",0)], [row("dup","raw",0)]*2,
    [row("unknown","missing",0)] ])
def test_retention_bad_input(data):
    with pytest.raises(ValueError): rehearse(data,now=NOW)
def test_retention_resource_and_reference_guards():
    data=[row("x","artifact",99*86400)]
    for kw in [{"max_bytes":1},{"protected_ids":["missing"]},{"max_records":0}]:
        with pytest.raises(ValueError): rehearse(data,now=NOW,**kw)
def test_retention_interruption_does_not_touch_input(monkeypatch):
    from pathlib import Path
    data=[row("x","artifact",99*86400)]
    def fail(*a,**k): raise OSError("injected")
    monkeypatch.setattr(Path,"unlink",fail)
    with pytest.raises(OSError): rehearse(data,now=NOW)
    assert data[0]["payload"]==b"test"
def healthy(**kw):
    args=dict(queue_depth=0,queue_bytes=0,disk_free_bytes=2*1024**3,
              rss_bytes=1024,retries=0,sources=["SUCCESS"]);args.update(kw)
    return observe(**args)
def test_observation_has_closed_schema_and_healthy_state():
    r=healthy();assert r["status"]=="HEALTHY" and r["admit_work"]
    assert set(r)=={"version","status","admit_work","reasons","source_counts","counters","send"}
@pytest.mark.parametrize("kw,reason",[({"queue_depth":101},"QUEUE_DEPTH"),
    ({"queue_bytes":1048577},"QUEUE_BYTES"),({"disk_free_bytes":0},"DISK_LOW"),
    ({"rss_bytes":268435457},"MEMORY"),({"retries":3},"RETRY_EXHAUSTED")])
def test_resource_admission_fails_closed(kw,reason):
    r=healthy(**kw);assert r["status"]=="BLOCKED" and not r["admit_work"] and reason in r["reasons"]
@pytest.mark.parametrize("sources",[[],["UNKNOWN"],["SUCCESS","UNAVAILABLE"]])
def test_missing_or_degraded_sources_not_healthy(sources):
    r=healthy(sources=sources);assert r["status"]=="DEGRADED" and not r["admit_work"]
@pytest.mark.parametrize("kind",["memory","file","descriptors","cpu"])
def test_real_child_limits(kind):
    r=probe(kind);assert r["status"]=="LIMIT_ENFORCED"
    assert r["max_observed_file_bytes"]<=1024
def test_child_timeout_reaped():
    assert probe("timeout")=={"kind":"timeout","status":"TIMEOUT","child_reaped":True}


def test_bytes_subclass_cannot_bypass_limit():
    class Misleading(bytes):
        def __len__(self): return 0
    data=[row("x","artifact",0)];data[0]["payload"]=Misleading(b"x"*100)
    with pytest.raises(ValueError): rehearse(data,now=NOW,max_bytes=1)
@pytest.mark.parametrize("cause",["ENOSPC","EACCES","UNKNOWN"])
def test_unrelated_failure_not_accepted_as_limit(cause):
    import json,subprocess
    from kgeopolitical_monitor.resource_probe_p243 import _classify
    result=subprocess.CompletedProcess([],42,json.dumps({"cause":cause}),"")
    assert _classify("file",result)=="FAILED"
def test_arbitrary_signal_not_accepted_as_cpu_limit():
    import subprocess
    from kgeopolitical_monitor.resource_probe_p243 import _classify
    assert _classify("cpu",subprocess.CompletedProcess([],-9,"",""))=="FAILED"
