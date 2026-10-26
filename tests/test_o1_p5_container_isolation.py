"""P5 tests exercise network route checks using fixture filesystem only."""
from pathlib import Path
from types import SimpleNamespace

import pytest

from kgeopolitical_monitor import offline_isolation_child as child


class FakePath:
    routes = "Iface Destination Gateway Flags RefCnt Use Metric Mask MTU Window IRTT\n"
    interfaces = ["lo"]

    def __init__(self, path):
        self.path = path

    def iterdir(self):
        return [SimpleNamespace(name=x) for x in self.interfaces]

    def read_text(self, **kwargs):
        return self.routes


def test_offline_network_proof_allows_only_loopback(monkeypatch):
    monkeypatch.setattr(child, "Path", FakePath)
    assert child.verify_no_external_network_route() == ["lo"]


def test_offline_network_proof_rejects_extra_interface(monkeypatch):
    monkeypatch.setattr(child, "Path", FakePath)
    monkeypatch.setattr(FakePath, "interfaces", ["lo", "eth0"])
    with pytest.raises(RuntimeError, match="non-loopback"):
        child.verify_no_external_network_route()


def test_offline_network_proof_rejects_default_route(monkeypatch):
    monkeypatch.setattr(child, "Path", FakePath)
    monkeypatch.setattr(FakePath, "interfaces", ["lo"])
    monkeypatch.setattr(FakePath, "routes",
        "Iface Destination Gateway Flags RefCnt Use Metric Mask MTU Window IRTT\n"
        "lo 00000000 00000000 0001 0 0 0 00000000 0 0 0\n")
    with pytest.raises(RuntimeError, match="default IPv4"):
        child.verify_no_external_network_route()
