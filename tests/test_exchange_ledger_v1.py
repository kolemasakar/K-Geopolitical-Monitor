"""Synthetic producer ledger tests. No runtime data or network."""
import pytest
from kgeopolitical_monitor.exchange_generation_v1 import publish_generation
from kgeopolitical_monitor.exchange_ledger_v1 import append_published, replay_published
from kgeopolitical_monitor.exchange_replay_v1 import CursorExpired
from test_exchange_contract_v1 import base


def test_append_replay_and_idempotency(tmp_path):
    out = tmp_path / "export"
    out.mkdir()
    batch = base()
    publish_generation(batch, out)
    first = append_published(out, batch["batch_id"])
    assert first["sequence"] == 1
    assert append_published(out, batch["batch_id"]) == first
    assert replay_published(out, 0) == [first]


def test_ordered_append_and_expiry(tmp_path):
    out = tmp_path / "export"
    out.mkdir()
    for name in ("batch1", "batch2"):
        batch = base()
        batch["batch_id"] = name
        publish_generation(batch, out)
        append_published(out, name)
    assert [e["sequence"] for e in replay_published(out, 1)] == [2]
    with pytest.raises(CursorExpired):
        replay_published(out, 0, minimum_available_sequence=2)


def test_refuse_unpublished(tmp_path):
    out = tmp_path / "export"
    out.mkdir()
    with pytest.raises(ValueError):
        append_published(out, "missing")
    assert not (out / "ledger.jsonl").exists()
