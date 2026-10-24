"""S5.2: ledger v1/v2 compatibility inventory, no migration or production writes."""
from kgeopolitical_monitor.exchange_generation_v1 import publish_generation
from kgeopolitical_monitor.exchange_ledger_v1 import append_published, replay_published
from kgeopolitical_monitor.exchange_ledger_atomic_v1 import append, replay
from test_exchange_contract_v1 import base


def test_v1_and_v2_ledgers_are_independent_not_implicitly_migrated(tmp_path):
    out = tmp_path / "synthetic"
    out.mkdir()
    publish_generation(base(), out)
    old = append_published(out, "batch1")
    assert old["sequence"] == 1
    assert not (out / "ledger-v2.jsonl").exists()
    new = append(out, "batch1")
    assert new["sequence"] == 1
    assert (out / "ledger.jsonl").is_file()
    assert (out / "ledger-v2.jsonl").is_file()
    assert replay_published(out, after_sequence=0) == [old]
    assert replay(out, after_sequence=0) == [new]
    assert append(out, "batch1") == new
    assert append_published(out, "batch1") == old


def test_v2_never_backfills_v1_history_automatically(tmp_path):
    out = tmp_path / "synthetic"
    out.mkdir()
    for index in (1, 2):
        payload = base()
        payload["batch_id"] = f"batch{index}"
        publish_generation(payload, out)
        append_published(out, payload["batch_id"])
    assert [row["sequence"] for row in replay_published(out, after_sequence=0)] == [1, 2]
    assert replay(out, after_sequence=0) == []
    append(out, "batch2")
    assert [r["batch_id"] for r in replay(out, after_sequence=0)] == ["batch2"]
    assert [r["batch_id"] for r in replay_published(out, after_sequence=0)] == ["batch1", "batch2"]
