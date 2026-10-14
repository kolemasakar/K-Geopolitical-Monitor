"""Typed KGM-only synthetic inbox/outbox acceptance."""
import copy
import pytest
from kgeopolitical_monitor.research_spool_v1 import submit, retrieve
from kgeopolitical_monitor.research_typed_spool_v1 import publish_typed_fixture
from test_research_typed_result_v1 import typed


def test_typed_fixture_roundtrip_and_restart(tmp_path):
    request, result = typed()
    policy = {"ktrader": "review-v1"}
    submit(tmp_path, request, allowed_consumers=policy)
    first = publish_typed_fixture(tmp_path, "ktrader", "req-01", result, allowed_consumers=policy)
    assert retrieve(tmp_path, "ktrader", "req-01", allowed_consumers=policy) == first
    assert publish_typed_fixture(tmp_path, "ktrader", "req-01", result, allowed_consumers=policy) == first


def test_immutable_typed_result_conflict(tmp_path):
    request, result = typed()
    policy = {"ktrader": "review-v1"}
    submit(tmp_path, request, allowed_consumers=policy)
    publish_typed_fixture(tmp_path, "ktrader", "req-01", result, allowed_consumers=policy)
    changed = copy.deepcopy(result)
    changed["records"][0]["summary"] = "Different synthetic fact"
    with pytest.raises(ValueError):
        publish_typed_fixture(tmp_path, "ktrader", "req-01", changed, allowed_consumers=policy)


def test_typed_historical_lookahead_never_published(tmp_path):
    request, result = typed()
    policy = {"ktrader": "review-v1"}
    submit(tmp_path, request, allowed_consumers=policy)
    result["records"][0]["evidence"][0]["available_at_utc"] = "2026-09-04T00:00:00Z"
    with pytest.raises(ValueError):
        publish_typed_fixture(tmp_path, "ktrader", "req-01", result, allowed_consumers=policy)
    assert not (tmp_path / "outbox" / "ktrader" / "req-01.json").exists()


def test_revoked_policy_blocks_typed_publication(tmp_path):
    request, result = typed()
    submit(tmp_path, request, allowed_consumers={"ktrader": "review-v1"})
    with pytest.raises(ValueError):
        publish_typed_fixture(tmp_path, "ktrader", "req-01", result,
                              allowed_consumers={"ktrader": "review-v2"})
