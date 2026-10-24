"""S5.2 read-only migration inventory, with no actual conversion."""
import pytest
from kgeopolitical_monitor.exchange_generation_v1 import publish_generation
from kgeopolitical_monitor.exchange_ledger_v1 import append_published
from kgeopolitical_monitor.exchange_ledger_atomic_v1 import append
from kgeopolitical_monitor.ledger_migration_preview_s5 import preview_ledger_migration
from test_exchange_contract_v1 import base


def test_preview_requires_explicit_migration_and_preserves_v1(tmp_path):
    root=tmp_path/"exchange"
    root.mkdir()
    for name in ("batch1","batch2"):
        payload=base()
        payload["batch_id"]=name
        publish_generation(payload,root)
        append_published(root,name)
    before=(root/"ledger.jsonl").read_bytes()
    p=preview_ledger_migration(root)
    assert p["missing_in_v2"]==("batch1","batch2")
    assert p["migration_applied"] is False and p["production_authorized"] is False
    assert (root/"ledger.jsonl").read_bytes()==before
    assert not (root/"ledger-v2.jsonl").exists()
    append(root,"batch1")
    assert preview_ledger_migration(root)["missing_in_v2"]==("batch2",)


def test_preview_rejects_torn_legacy(tmp_path):
    root=tmp_path/"exchange"
    root.mkdir()
    (root/"ledger.jsonl").write_bytes(b'{"sequence":1')
    with pytest.raises(ValueError):
        preview_ledger_migration(root)


def test_preview_rejects_legacy_symlink(tmp_path):
    root=tmp_path/"exchange"
    root.mkdir()
    outside=tmp_path/"outside.jsonl"
    outside.write_bytes(b"")
    (root/"ledger.jsonl").symlink_to(outside)
    with pytest.raises(ValueError):
        preview_ledger_migration(root)
