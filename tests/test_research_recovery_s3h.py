"""Bounded offline recovery pass: no unattended scheduler or provider calls."""
import pytest
from kgeopolitical_monitor.research_durable_lifecycle_v1 import admit,recovery_snapshot,advance
from kgeopolitical_monitor.research_recovery_pass_v1 import recovery_pass
from kgeopolitical_monitor.research_completion_v1 import complete_or_reconcile
from test_research_request_v1 import sample
from test_research_typed_result_v1 import typed

POLICY={"ktrader":"review-v1"}
NOW="2026-09-28T12:06:00Z"
DEADLINE="2026-09-28T12:05:00Z"
KEY=("ktrader","req-01")

def test_explicit_deadline_expires_unpublished(tmp_path):
    admit(tmp_path,sample(),allowed_consumers=POLICY)
    result=recovery_pass(tmp_path,allowed_consumers=POLICY,observed_at_utc=NOW,
                         deadlines={KEY:DEADLINE})
    assert result["expired"]==[KEY]
    assert recovery_snapshot(tmp_path,allowed_consumers=POLICY)==[]

def test_no_deadline_keeps_pending(tmp_path):
    admit(tmp_path,sample(),allowed_consumers=POLICY)
    result=recovery_pass(tmp_path,allowed_consumers=POLICY,observed_at_utc=NOW)
    assert result["pending"]==[KEY]

def test_reconciles_published_result_before_expiry(tmp_path):
    request,result=typed()
    admit(tmp_path,request,allowed_consumers=POLICY)
    advance(tmp_path,"ktrader","req-01","ACCEPTED",allowed_consumers=POLICY,
            at_utc="2026-09-28T12:01:00Z")
    advance(tmp_path,"ktrader","req-01","PROCESSING",allowed_consumers=POLICY,
            at_utc="2026-09-28T12:02:00Z")
    # Mimic crash after atomic result publication but before state reconciliation
    from kgeopolitical_monitor.research_storage_v1 import atomic_replace,canonical_bytes
    import hashlib
    artifact={"request_digest":__import__("json").loads((tmp_path/"inbox"/"ktrader--req-01.json").read_text())["request_digest"],"result":result}
    artifact["sha256"]=hashlib.sha256(canonical_bytes(artifact)).hexdigest()
    (tmp_path/"outbox"/"ktrader").mkdir()
    atomic_replace(tmp_path/"outbox"/"ktrader"/"req-01.json",canonical_bytes(artifact))
    report=recovery_pass(tmp_path,allowed_consumers=POLICY,observed_at_utc=NOW,
                         deadlines={KEY:DEADLINE})
    assert report["reconciled"]==[KEY] and report["expired"]==[]
    assert recovery_snapshot(tmp_path,allowed_consumers=POLICY)==[]

def test_bounded_and_cursor_input(tmp_path):
    for n in range(3):
        req=sample();req["request_id"]=f"req-{n:02d}"
        admit(tmp_path,req,allowed_consumers=POLICY)
    one=recovery_pass(tmp_path,allowed_consumers=POLICY,observed_at_utc=NOW,max_items=1)
    assert len(one["pending"])==1 and one["remaining"]==2
    two=recovery_pass(tmp_path,allowed_consumers=POLICY,observed_at_utc=NOW,
                      max_items=1,after_key=one["next_cursor"])
    assert two["pending"]!=one["pending"]

def test_invalid_bound_denied(tmp_path):
    with pytest.raises(ValueError):
        recovery_pass(tmp_path,allowed_consumers=POLICY,observed_at_utc=NOW,max_items=0)
