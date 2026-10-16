"""Synthetic read-only ledger v1/v2 preflight tests."""
import pytest
from kgeopolitical_monitor.exchange_generation_v1 import publish_generation
from kgeopolitical_monitor.exchange_ledger_v1 import append_published
from kgeopolitical_monitor.exchange_ledger_atomic_v1 import append
from kgeopolitical_monitor.exchange_ledger_compatibility_s5 import compare_ledger_formats
from test_exchange_contract_v1 import base

def test_identical_formats_compatible(tmp_path):
    root=tmp_path/"export";root.mkdir()
    publish_generation(base(),root)
    append_published(root,"batch1")
    append(root,"batch1")
    assert compare_ledger_formats(root)=={"compatible":True,"reason":"IDENTICAL","v1_count":1,"v2_count":1}

def test_missing_v2_does_not_authorize_migration(tmp_path):
    root=tmp_path/"export";root.mkdir()
    publish_generation(base(),root)
    append_published(root,"batch1")
    result=compare_ledger_formats(root)
    assert not result["compatible"] and result["reason"]=="MISSING_FORMAT"
    assert not (root/"ledger-v2.jsonl").exists()

def test_divergent_v2_rejected_without_mutation(tmp_path):
    root=tmp_path/"export";root.mkdir()
    publish_generation(base(),root)
    append_published(root,"batch1")
    append(root,"batch1")
    v2=root/"ledger-v2.jsonl"
    previous=v2.read_bytes()
    v2.write_bytes(previous.replace(b"batch1",b"batch2"))
    result=compare_ledger_formats(root)
    assert result["reason"]=="DATA_DIVERGENCE" and not result["compatible"]
    assert v2.read_bytes()!=previous

def test_torn_and_symlink_formats_rejected(tmp_path):
    root=tmp_path/"export";root.mkdir()
    (root/"ledger.jsonl").write_bytes(b'{"sequence":1')
    with pytest.raises(ValueError):
        compare_ledger_formats(root)
    (root/"ledger.jsonl").unlink()
    outside=tmp_path/"outside";outside.write_text("untouched")
    (root/"ledger.jsonl").symlink_to(outside)
    with pytest.raises(ValueError):
        compare_ledger_formats(root)
    assert outside.read_text()=="untouched"
