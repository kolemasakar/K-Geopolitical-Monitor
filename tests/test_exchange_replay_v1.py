"""Offline synthetic replay contract tests."""
import pytest
from kgeopolitical_monitor.exchange_replay_v1 import select_replay, CursorExpired, CursorGap


def entries():
    return [{"sequence": n, "batch_id": "batch" + str(n), "sha256": "a" * 64}
            for n in range(5, 9)]


def test_replay_from_retention_floor():
    assert [x["sequence"] for x in select_replay(entries(), after_sequence=4, minimum_available_sequence=5)] == [5, 6, 7, 8]


def test_replay_from_checkpoint():
    assert [x["sequence"] for x in select_replay(entries(), after_sequence=6, minimum_available_sequence=5)] == [7, 8]


def test_bounded_replay():
    assert len(select_replay(entries(), after_sequence=4, minimum_available_sequence=5, max_records=2)) == 2


def test_expired_cursor():
    with pytest.raises(CursorExpired):
        select_replay(entries(), after_sequence=3, minimum_available_sequence=5)


def test_gap():
    ledger = entries()
    del ledger[1]
    with pytest.raises(CursorGap):
        select_replay(ledger, after_sequence=4, minimum_available_sequence=5)


def test_reordered():
    ledger = entries()
    ledger[0], ledger[1] = ledger[1], ledger[0]
    with pytest.raises(CursorGap):
        select_replay(ledger, after_sequence=4, minimum_available_sequence=5)


def test_duplicate_batch():
    ledger = entries()
    ledger[1]["batch_id"] = ledger[0]["batch_id"]
    with pytest.raises(ValueError):
        select_replay(ledger, after_sequence=4, minimum_available_sequence=5)


def test_empty_ledger_is_not_proof_of_healthy_feed():
    assert select_replay([], after_sequence=4, minimum_available_sequence=5) == []


def test_reject_invalid_digest():
    ledger = entries()
    ledger[0]["sha256"] = "not-a-digest"
    with pytest.raises(ValueError):
        select_replay(ledger, after_sequence=4, minimum_available_sequence=5)
