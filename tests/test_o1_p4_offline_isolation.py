import json
import pytest

from kgeopolitical_monitor import offline_isolation as isolate


def test_isolation_command_fails_closed_without_unshare(monkeypatch):
    monkeypatch.setattr(isolate.shutil, "which", lambda name: None)
    with pytest.raises(RuntimeError, match="unavailable"):
        isolate.isolated_command()


def test_isolation_command_uses_network_namespace(monkeypatch):
    monkeypatch.setattr(isolate.shutil, "which", lambda name: "/usr/bin/unshare")
    monkeypatch.setattr(isolate.sys, "platform", "linux")
    args = isolate.isolated_command()
    assert args[:5] == ["/usr/bin/unshare", "--user", "--map-root-user", "--net", "--"]
    assert "offline_isolation_child" in args[-1]


def test_isolation_fail_closed_on_unshare_error(monkeypatch):
    monkeypatch.setattr(isolate, "isolated_command", lambda: ["unshare", "--net", "--", "python3"])
    class Failed:
        returncode = 1
        stdout = ""
    monkeypatch.setattr(isolate.subprocess, "run", lambda *args, **kwargs: Failed())
    with pytest.raises(RuntimeError, match="failed closed"):
        isolate.run_isolated_synthetic_test()


def test_isolation_checks_report(monkeypatch):
    monkeypatch.setattr(isolate, "isolated_command", lambda: ["unshare", "--net", "--", "python3"])
    class Result:
        returncode = 0
        stdout = json.dumps({"format": "KGM_O1_NETNS_SYNTHETIC_V1", "only_synthetic_data": True, "status": "COMPLETED"})
    monkeypatch.setattr(isolate.subprocess, "run", lambda *args, **kwargs: Result())
    assert isolate.run_isolated_synthetic_test()["status"] == "COMPLETED"
