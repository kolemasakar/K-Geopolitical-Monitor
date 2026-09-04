from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def _read(name: str) -> str:
    return (ROOT / name).read_text(encoding="utf-8")


def test_p12_3_gate_remains_canonical_after_later_phase_progress():
    roadmap = _read("ROADMAP.md")
    plan = _read("docs/implementation/PHASE_12_INTELLIGENCE_QUALITY_SOURCE_NETWORK_PLAN.md")
    result = _read("docs/implementation/P12_3_PRIORITY_AUTHORITATIVE_SOURCE_PACK_RESULT.md")

    for document in (roadmap, plan, result):
        assert "P12_3_AUTHORITATIVE_SOURCE_PACK_VALIDATED" in document
    assert "PHASE_12_INTELLIGENCE_SOURCE_NETWORK_FOUNDATION_VALIDATED" in roadmap
    assert "Phase 13 — Semantic Verification and Provenance Intelligence" in roadmap


def test_p12_3_preserves_production_and_storage_contracts():
    readme = _read("README.md")
    roadmap = _read("ROADMAP.md")

    for document in (readme, roadmap):
        assert "Production/live operational status: NOT_OPERATIONAL" in document
        assert "Runtime storage mode: PROJECT_LOCAL_ONLY" in document


def test_p12_3_explicitly_preserves_degraded_european_parliament_state():
    documents = "\n".join(
        [
            _read("ARCHITECTURE.md"),
            _read("EXTERNAL_INTEGRATIONS.md"),
            _read("SOURCE_POLICY.md"),
            _read("SECURITY_AND_DATA_POLICY.md"),
            _read("docs/implementation/P12_3_PRIORITY_AUTHORITATIVE_SOURCE_PACK_RESULT.md"),
            _read("docs/implementation/P12_3_CONTROLLED_LIVE_SOURCE_MATRIX.md"),
        ]
    )

    assert "European Parliament" in documents
    assert "DEGRADED" in documents
    assert "anti-bot" in documents
    assert "third-party" in documents


def test_p12_3_epistemic_and_paid_provider_boundaries_remain_explicit():
    roadmap = _read("ROADMAP.md")
    source_policy = _read("SOURCE_POLICY.md")
    result = _read("docs/implementation/P12_3_PRIORITY_AUTHORITATIVE_SOURCE_PACK_RESULT.md")

    assert "adapter/source/domain/item count is not independent-origin count" in roadmap
    assert "official sources are authoritative for their own statements, not automatically for the underlying event" in source_policy
    assert "paid providers: `NONE_APPROVED`" in result
