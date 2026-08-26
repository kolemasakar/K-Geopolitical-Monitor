from datetime import datetime

from kgeopolitical_monitor.confidence_engine import calculate_confidence
from kgeopolitical_monitor.contradictions import Contradiction
from kgeopolitical_monitor.evidence import Evidence
from kgeopolitical_monitor.verification_workflow import verify_claim


def _evidence(evidence_id, source_id, reliability):
    return Evidence(
        id=evidence_id,
        source_id=source_id,
        claim="test claim",
        reliability=reliability,
        created_at=datetime(2026, 8, 26, 0, 0, 0),
    )


def test_verified_multi_source_evidence():
    evidence_items = [
        _evidence("e1", "source-a", "HIGH"),
        _evidence("e2", "source-b", "HIGH"),
    ]

    result = verify_claim("test claim", evidence_items)

    assert result["status"] == "VERIFIED"
    assert result["confidence"] >= 0.75


def test_conflicting_claims_reduce_confidence():
    evidence_items = [
        _evidence("e1", "source-a", "HIGH"),
        _evidence("e2", "source-b", "HIGH"),
    ]
    contradiction = Contradiction("claim-a", "claim-b")

    clean = calculate_confidence(evidence_items, [])
    conflicted = calculate_confidence(evidence_items, [contradiction])

    assert conflicted < clean


def test_low_reliability_source_does_not_force_verified_status():
    evidence_items = [_evidence("e1", "source-a", "LOW")]

    result = verify_claim("test claim", evidence_items)

    assert result["status"] == "PARTLY_VERIFIED"
    assert result["confidence"] < 0.75


def test_insufficient_evidence_has_zero_confidence():
    result = verify_claim("test claim", [])

    assert result["status"] == "PARTLY_VERIFIED"
    assert result["confidence"] == 0.0
