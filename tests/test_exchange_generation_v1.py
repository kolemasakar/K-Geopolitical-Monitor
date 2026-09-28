"""Synthetic complete-generation acceptance tests."""
import pytest
from kgeopolitical_monitor.exchange_generation_v1 import publish_generation, read_generation
from test_exchange_contract_v1 import base, claim


def root(tmp_path):
    path = tmp_path / "export"
    path.mkdir()
    return path


def test_round_trip(tmp_path):
    out = root(tmp_path)
    batch = base()
    batch["records"] = [claim("DISPUTED")]
    manifest = publish_generation(batch, out)
    assert manifest["record_count"] == 1
    assert read_generation(out, "batch1") == batch


def test_duplicate(tmp_path):
    out = root(tmp_path)
    publish_generation(base(), out)
    with pytest.raises(FileExistsError):
        publish_generation(base(), out)


def test_digest_failure(tmp_path):
    out = root(tmp_path)
    publish_generation(base(), out)
    (out / "batch1" / "batch.json").write_text("{}")
    with pytest.raises(ValueError):
        read_generation(out, "batch1")


def test_missing_marker(tmp_path):
    out = root(tmp_path)
    publish_generation(base(), out)
    (out / "batch1" / "COMPLETE").unlink()
    with pytest.raises(ValueError):
        read_generation(out, "batch1")


def test_incomplete_staging_not_published(tmp_path):
    out = root(tmp_path)
    (out / ".kgm-stage-incomplete").mkdir()
    with pytest.raises(ValueError):
        read_generation(out, "batch1")


def test_bad_schema_rejected(tmp_path):
    out = root(tmp_path)
    batch = base()
    batch["schema_version"] = "invalid"
    with pytest.raises(ValueError):
        publish_generation(batch, out)
    assert list(out.iterdir()) == []
