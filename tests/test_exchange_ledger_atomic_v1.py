"""Synthetic atomic ledger failure and replay tests."""
import pytest
from kgeopolitical_monitor import exchange_ledger_atomic_v1 as atomic
from kgeopolitical_monitor.exchange_generation_v1 import publish_generation
from test_exchange_contract_v1 import base


def _root(tmp_path):
    out = tmp_path / "export"
    out.mkdir()
    return out


def test_atomic_append_replay_idempotent(tmp_path):
    out = _root(tmp_path)
    publish_generation(base(), out)
    first = atomic.append(out, "batch1")
    assert first["sequence"] == 1
    assert atomic.append(out, "batch1") == first
    assert atomic.replay(out, 0) == [first]


def test_atomic_two_batches(tmp_path):
    out = _root(tmp_path)
    for name in ("batch1", "batch2"):
        batch = base()
        batch["batch_id"] = name
        publish_generation(batch, out)
        atomic.append(out, name)
    assert [row["sequence"] for row in atomic.replay(out, 1)] == [2]


def test_reject_torn_ledger(tmp_path):
    out = _root(tmp_path)
    (out / "ledger-v2.jsonl").write_bytes(b'{"sequence":1')
    with pytest.raises(ValueError):
        atomic.replay(out, 0)


def test_replace_failure_preserves_previous(tmp_path, monkeypatch):
    out = _root(tmp_path)
    publish_generation(base(), out)
    first = atomic.append(out, "batch1")
    batch = base()
    batch["batch_id"] = "batch2"
    publish_generation(batch, out)
    def interrupt(*args):
        raise OSError("synthetic failure before atomic replacement")
    monkeypatch.setattr(atomic.os, "replace", interrupt)
    with pytest.raises(OSError):
        atomic.append(out, "batch2")
    assert atomic.replay(out, 0) == [first]


def test_reject_unpublished_generation(tmp_path):
    out = _root(tmp_path)
    with pytest.raises(ValueError):
        atomic.append(out, "missing")
    assert atomic.replay(out, 0) == []
