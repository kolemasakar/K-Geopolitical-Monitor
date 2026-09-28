"""Synthetic-only v1 KGM exchange tests. No live data, no cross-project network."""
from copy import deepcopy
import pytest

from kgeopolitical_monitor.exchange_contract_v1 import validate_batch

T0 = "2026-09-28T12:00:00Z"
T1 = "2026-09-28T12:01:00Z"
T2 = "2026-09-28T12:02:00Z"

def base():
    return {
        "schema_version": "kgm.exchange.v1", "batch_id": "batch1",
        "producer_snapshot_id": "snapshot1", "producer_code_sha": "sha1",
        "policy_version": "synthetic-v1", "generated_at_utc": T2,
        "minimum_available_cursor": "cursor0", "high_watermark_cursor": "cursor1",
        "heartbeat": {"state": "HEALTHY", "observed_at_utc": T2}, "records": [],
    }

def claim(state="VERIFIED"):
    return {
        "record_id": "rec1", "kind": "CLAIM_EVENT", "change_type": "NEW",
        "entity_id": "claim1", "entity_version_id": "claimv1",
        "recorded_at_utc": T1, "published_at_utc": T0,
        "ingested_at_utc": T1, "exported_at_utc": T2,
        "verification": {"canonical_verification_state": state,
                         "confidence_dimensions": {"evidence_sufficiency": "HIGH"}},
        "provenance": {"publisher": "synthetic", "underlying_origin": "synthetic-origin"},
        "content": {"summary": "synthetic claim only"},
    }

def test_healthy_empty_heartbeat_is_valid():
    assert len(validate_batch(base())) == 64

def test_healthy_verified():
    b = base()
    b["records"] = [claim()]
    assert len(validate_batch(b)) == 64

def test_disputed_unresolved_is_valid():
    b = base()
    v = claim("DISPUTED")
    v["contradiction"] = {"lifecycle_state": "UNRESOLVED"}
    b["records"] = [v]
    validate_batch(b)

def test_unresolved_verified_fails():
    b = base()
    v = claim()
    v["contradiction"] = {"lifecycle_state": "UNRESOLVED"}
    b["records"] = [v]
    with pytest.raises(ValueError):
        validate_batch(b)

def test_revision_correction_requires_lineage():
    b = base()
    v = claim()
    v.update({"record_id": "rec2", "entity_version_id": "claimv2",
              "kind": "CLAIM_CORRECTION", "change_type": "CORRECTION",
              "supersedes_record_id": "rec1"})
    b["records"] = [v]
    validate_batch(b)
    del v["supersedes_record_id"]
    with pytest.raises(ValueError):
        validate_batch(b)

def test_forecast_not_fact():
    b = base()
    v = {k: val for k, val in claim().items() if k != "verification"}
    v["kind"] = "FORECAST_VERSION"
    v["forecast"] = {"raw_probability": .4, "calibrated_probability": .3,
                     "scenario_confidence": "MEDIUM"}
    b["records"] = [v]
    validate_batch(b)
    v["forecast"]["canonical_verification_state"] = "VERIFIED"
    with pytest.raises(ValueError):
        validate_batch(b)

def test_unknown_source_health():
    b = base()
    v = {k: val for k, val in claim().items() if k != "verification"}
    v["kind"] = "SOURCE_HEALTH"
    v["source_health"] = {"operational_state": "UNMEASURED"}
    b["heartbeat"] = {"state": "UNKNOWN", "observed_at_utc": T2}
    b["records"] = [v]
    validate_batch(b)

def test_reject_consumer_numeric_confidence():
    b = base()
    v = claim()
    v["confidence"] = .9
    b["records"] = [v]
    with pytest.raises(ValueError):
        validate_batch(b)

def test_reject_non_utc():
    b = base()
    b["generated_at_utc"] = "2026-09-28T15:02:00+03:00"
    with pytest.raises(ValueError):
        validate_batch(b)

def test_reject_oversized_batch():
    b = base()
    v = claim()
    v["content"]["summary"] = "x" * (1024 * 1024)
    b["records"] = [v]
    with pytest.raises(ValueError):
        validate_batch(b)

def test_wrong_schema_rejected():
    b = base()
    b["schema_version"] = "kgm.exchange.v2"
    with pytest.raises(ValueError):
        validate_batch(b)

def test_revision_future_ingest_rejected():
    b = base()
    v = claim()
    v["ingested_at_utc"] = "2026-09-28T12:03:00Z"
    b["records"] = [v]
    with pytest.raises(ValueError):
        validate_batch(b)

def test_no_mutation_and_deterministic_digest():
    b = base()
    original = deepcopy(b)
    assert validate_batch(b) == validate_batch(b)
    assert b == original
