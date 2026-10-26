from hashlib import sha256

import pytest
from kgeopolitical_monitor.on_demand_request_gate import authorize_manual_request


BASE = dict(
    repository="kolemasakar/K-Geopolitical-Monitor",
    actor="kolemasakar",
    ref="refs/heads/main",
    event_name="workflow_dispatch",
    mode="OFFLINE_SYNTHETIC",
    topic="Geopolitical test",
    request_id="sample-01",
)


def test_manual_owner_request_allows_only_offline():
    r = authorize_manual_request(**BASE)
    assert r.topic_sha256 == sha256(BASE["topic"].encode("utf-8")).hexdigest()
    assert r.mode == "OFFLINE_SYNTHETIC"
    assert r.request_id == "sample-01"


@pytest.mark.parametrize("key,value", [
    ("actor", "not-owner"),
    ("repository", "attacker/fork"),
    ("ref", "refs/heads/feature"),
    ("event_name", "pull_request"),
    ("mode", "LIVE_SOURCES"),
])
def test_manual_gate_denies_unapproved_context(key, value):
    with pytest.raises(PermissionError):
        authorize_manual_request(**dict(BASE, **{key: value}))


@pytest.mark.parametrize("key,value", [
    ("topic", ""),
    ("topic", "x" * 257),
    ("topic", "test\nnewline"),
    ("request_id", "../escape"),
])
def test_owner_input_rejected_when_invalid(key, value):
    with pytest.raises(ValueError):
        authorize_manual_request(**dict(BASE, **{key: value}))


def test_no_live_workflow_or_push_trigger():
    from pathlib import Path
    workflow = (Path(__file__).resolve().parents[1] /
                ".github/workflows/p5-owner-on-demand-offline.yml").read_text()
    assert "workflow_dispatch:" in workflow
    assert "OFFLINE_SYNTHETIC" in workflow
    assert "--network none" in workflow
    assert "--cap-drop ALL" in workflow
    assert "persist-credentials: false" in workflow
    assert "pull_request:" not in workflow
    assert "push:" not in workflow
    assert "LIVE_SOURCES" not in workflow
