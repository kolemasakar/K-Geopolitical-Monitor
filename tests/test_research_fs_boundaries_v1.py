"""KGM-only negative filesystem boundary tests using disposable directories."""
import json
import pytest
from kgeopolitical_monitor.research_durable_lifecycle_v1 import admit, recovery_snapshot
from kgeopolitical_monitor.research_completion_v1 import complete_or_reconcile
from test_research_request_v1 import sample
from test_research_completion_v1 import processing, POLICY, STAMP


def test_root_alias_rejected(tmp_path):
    root = tmp_path / "root"
    root.mkdir()
    alias = tmp_path / "alias"
    alias.symlink_to(root, target_is_directory=True)
    with pytest.raises(ValueError):
        admit(alias, sample(), allowed_consumers=POLICY)


def test_request_alias_rejected(tmp_path):
    inbox = tmp_path / "inbox"
    inbox.mkdir()
    target = tmp_path / "target.json"
    target.write_text("unchanged")
    (inbox / "ktrader--req-01.json").symlink_to(target)
    with pytest.raises(ValueError):
        admit(tmp_path, sample(), allowed_consumers=POLICY)
    assert target.read_text() == "unchanged"


def test_corrupt_request_recovery_denied(tmp_path):
    admit(tmp_path, sample(), allowed_consumers=POLICY)
    target = tmp_path / "inbox" / "ktrader--req-01.json"
    saved = json.loads(target.read_text())
    saved["request"]["symbols"] = ["ALTERED"]
    target.write_text(json.dumps(saved))
    with pytest.raises(ValueError):
        recovery_snapshot(tmp_path, allowed_consumers=POLICY)


def test_corrupt_result_reconciliation_denied(tmp_path):
    result = processing(tmp_path)
    complete_or_reconcile(tmp_path, "ktrader", "req-01",
                          allowed_consumers=POLICY, result=result, at_utc=STAMP)
    target = tmp_path / "outbox" / "ktrader" / "req-01.json"
    saved = json.loads(target.read_text())
    saved["result"]["records"][0]["summary"] = "altered"
    target.write_text(json.dumps(saved))
    with pytest.raises(ValueError):
        complete_or_reconcile(tmp_path, "ktrader", "req-01",
                              allowed_consumers=POLICY)
