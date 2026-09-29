"""Synthetic-only offline immutable artifact tests."""
import json
from hashlib import sha256
import pytest

from kgeopolitical_monitor.exchange_artifact_v1 import write_immutable_batch
from test_exchange_contract_v1 import base, claim


def test_atomic_immutable_synthetic_batch(tmp_path):
    out = tmp_path / "kgm-export"
    out.mkdir()
    batch = base()
    batch["records"] = [claim("DISPUTED")]
    result = write_immutable_batch(batch, out)
    artifact = out / result["artifact"]
    manifest = json.loads((out / result["manifest"]).read_text())
    raw = artifact.read_bytes()
    assert sha256(raw).hexdigest() == manifest["sha256"] == result["sha256"]
    assert json.loads(raw)["records"][0]["verification"]["canonical_verification_state"] == "DISPUTED"
    assert manifest["record_count"] == 1
    assert len(list(out.iterdir())) == 2


def test_duplicate_batch_never_overwrites(tmp_path):
    out = tmp_path / "kgm-export"
    out.mkdir()
    batch = base()
    first = write_immutable_batch(batch, out)
    before = (out / first["artifact"]).read_bytes()
    with pytest.raises(FileExistsError):
        write_immutable_batch(batch, out)
    assert (out / first["artifact"]).read_bytes() == before
    assert len(list(out.iterdir())) == 2


def test_reject_unapproved_payload_before_write(tmp_path):
    out = tmp_path / "kgm-export"
    out.mkdir()
    batch = base()
    batch["private_token"] = "synthetic"
    with pytest.raises(ValueError):
        write_immutable_batch(batch, out)
    assert list(out.iterdir()) == []


def test_reject_missing_or_symlink_output_dir(tmp_path):
    batch = base()
    with pytest.raises(ValueError):
        write_immutable_batch(batch, tmp_path / "missing")
    out = tmp_path / "kgm-export"
    out.mkdir()
    link = tmp_path / "link"
    link.symlink_to(out, target_is_directory=True)
    with pytest.raises(ValueError):
        write_immutable_batch(batch, link)
    assert list(out.iterdir()) == []


def test_heartbeat_empty_batch_preserves_status(tmp_path):
    out = tmp_path / "kgm-export"
    out.mkdir()
    batch = base()
    batch["heartbeat"]["state"] = "UNKNOWN"
    result = write_immutable_batch(batch, out)
    assert json.loads((out / result["artifact"]).read_text())["heartbeat"]["state"] == "UNKNOWN"
    assert result["record_count"] == 0
