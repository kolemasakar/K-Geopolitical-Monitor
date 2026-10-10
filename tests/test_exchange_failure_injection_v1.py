"""Offline fault-injection acceptance tests for publication and ledger."""
import pytest
from kgeopolitical_monitor import exchange_generation_v1 as generation
from kgeopolitical_monitor import exchange_ledger_v1 as ledger
from test_exchange_contract_v1 import base


def test_failed_generation_rename_not_visible(tmp_path, monkeypatch):
    out = tmp_path / "export"
    out.mkdir()
    def fail_rename(*args):
        raise OSError("synthetic interrupted publication")
    monkeypatch.setattr(generation.os, "rename", fail_rename)
    with pytest.raises(OSError):
        generation.publish_generation(base(), out)
    assert not (out / "batch1").exists()
    with pytest.raises(ValueError):
        generation.read_generation(out, "batch1")


def test_ledger_rejects_missing_generation(tmp_path):
    out = tmp_path / "export"
    out.mkdir()
    with pytest.raises(ValueError):
        ledger.append_published(out, "batch1")
    assert not (out / "ledger.jsonl").exists()


def test_published_generation_survives_duplicate_attempt(tmp_path):
    out = tmp_path / "export"
    out.mkdir()
    generation.publish_generation(base(), out)
    with pytest.raises(FileExistsError):
        generation.publish_generation(base(), out)
    assert generation.read_generation(out, "batch1") == base()
