"""S5.1b valid external ledger must never be read through an alias."""
import pytest
from kgeopolitical_monitor import exchange_ledger_atomic_v1 as a
from kgeopolitical_monitor.exchange_generation_v1 import publish_generation
from test_exchange_contract_v1 import base

def test_valid_external_symlink_rejected_even_if_payload_well_formed(tmp_path):
    root=tmp_path/"export";root.mkdir()
    publish_generation(base(),root)
    a.append(root,"batch1")
    target=tmp_path/"valid-outside.jsonl"
    target.write_bytes((root/"ledger-v2.jsonl").read_bytes())
    (root/"ledger-v2.jsonl").unlink()
    (root/"ledger-v2.jsonl").symlink_to(target)
    with pytest.raises((ValueError,OSError)):
        a.replay(root,0)
    with pytest.raises((ValueError,OSError)):
        a.append(root,"batch1")
    assert target.read_bytes().endswith(b"\n")

def test_hardlinked_external_ledger_rejected(tmp_path):
    import os
    root=tmp_path/"export";root.mkdir()
    publish_generation(base(),root)
    a.append(root,"batch1")
    link=tmp_path/"outside-link"
    os.link(root/"ledger-v2.jsonl",link)
    with pytest.raises(ValueError):
        a.replay(root,0)
    assert link.read_bytes().endswith(b"\n")
