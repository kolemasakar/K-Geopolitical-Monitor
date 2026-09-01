from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MATRIX = ROOT / "docs" / "implementation" / "P12_6_PHASE_12_VALIDATION_MATRIX.md"
RESULT = ROOT / "docs" / "implementation" / "P12_6_PHASE_12_VALIDATION_MATRIX_RESULT.md"
CHECKPOINT = ROOT / "docs" / "checkpoints" / "PROJECT_CHECKPOINT_2026-09-01_P12_6_PHASE_12_VALIDATED.md"


def _read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_p12_6_closure_links_complete_phase12_chain():
    matrix = MATRIX.read_text(encoding="utf-8")
    result = RESULT.read_text(encoding="utf-8")
    for gate in (
        "P12_0_CANONICAL_CONVERGENCE_VALIDATED",
        "P12_1_SOURCE_PORTFOLIO_CONTRACT_VALIDATED",
        "P12_2_ADAPTER_FRAMEWORK_V2_VALIDATED",
        "P12_3_AUTHORITATIVE_SOURCE_PACK_VALIDATED",
        "P12_4_LOCAL_LANGUAGE_DISCOVERY_VALIDATED",
        "P12_5_SOURCE_HEALTH_EGRESS_INVENTORY_VALIDATED",
        "PHASE_12_INTELLIGENCE_SOURCE_NETWORK_FOUNDATION_VALIDATED",
    ):
        assert gate in matrix
        assert gate in result


def test_p12_6_closure_evidence_is_exact_and_saved():
    matrix = MATRIX.read_text(encoding="utf-8")
    result = RESULT.read_text(encoding="utf-8")
    checkpoint = CHECKPOINT.read_text(encoding="utf-8")

    for exact_id in (
        "c6aca6a2fe3c0dc991b267efa82c5748bd6460e2",
        "33546794411",
        "99986187419",
        "33546794273",
        "99986186748",
    ):
        assert exact_id in matrix
        assert exact_id in result
        assert exact_id in checkpoint

    for document in (result, checkpoint):
        assert "391 passed, 1 warning / SUCCESS" in document


def test_p12_6_known_limitations_remain_visible():
    text = (MATRIX.read_text(encoding="utf-8") + RESULT.read_text(encoding="utf-8")).lower()
    assert "pass_with_known_limitations" in text
    assert "european parliament" in text and "unavailable/parser" in text
    assert "haberturk" in text and "unavailable/unknown" in text
    assert "original_url must be http or https" in text
    assert "osce" in text and "content `stale`" in text
    assert "uk/ru/pl/tr" in text
    assert "not global language coverage" in text
    assert "not deployed enforcement" in text or "no firewall allowlist" in text


def test_p12_6_preserves_truth_runtime_security_boundaries():
    matrix = MATRIX.read_text(encoding="utf-8")
    lower = matrix.lower()
    readme = _read("README.md")
    roadmap = _read("ROADMAP.md")
    assert "publisher/publication is not automatically the underlying origin" in lower
    assert "do not create independent corroboration" in lower
    assert "not automatically underlying-event truth" in lower
    assert "are not truth operators" in lower
    assert "`global` is scope, not proof of exhaustive world coverage" in lower
    assert "a failed source does not prove an event did not occur" in lower
    assert "a successful probe does not prove exhaustive coverage" in lower
    for doc in (matrix, readme, roadmap):
        assert "Production/live operational status: NOT_OPERATIONAL" in doc
        assert "Runtime storage mode: PROJECT_LOCAL_ONLY" in doc
    assert "NONE_APPROVED" in matrix
    assert "0.0.0.0/0" in matrix
    assert "broad outbound egress" in matrix


def test_p12_6_closes_phase12_and_allows_validated_sequential_phase13_progress():
    roadmap = _read("ROADMAP.md")
    readme = _read("README.md")
    assert "Phase 12 — Intelligence Quality and Source Network Foundation\nState: `VALIDATED_WITH_KNOWN_LIMITATIONS`" in roadmap
    assert "P12.6 — Phase 12 Validation Matrix\nState: `VALIDATED`" in roadmap
    assert "PHASE_12_INTELLIGENCE_SOURCE_NETWORK_FOUNDATION_VALIDATED" in roadmap
    assert "Phase 13 — Semantic Verification and Provenance Intelligence\nState: `APPROVED / ACTIVE_ENGINEERING_PHASE`" in roadmap
    assert "P13.0 — Semantic Verification Architecture Contract\nState: `CURRENT / IMPLEMENTED_PENDING_VALIDATION`" in roadmap
    assert "P13.1 — Structured Semantic Claim Model\nState: `PLANNED / NOT_STARTED`" in roadmap
    assert "Phase 14 — Owner Operational Intelligence Activation\nState: `APPROVED_SEQUENTIAL / NOT_STARTED`" in roadmap
    assert "P12.6" in readme and "VALIDATED" in readme
    assert "P13.0_SEMANTIC_VERIFICATION_ARCHITECTURE_CONTRACT" in readme
