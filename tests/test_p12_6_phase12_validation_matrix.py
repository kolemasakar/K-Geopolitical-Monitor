from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MATRIX = ROOT / "docs" / "implementation" / "P12_6_PHASE_12_VALIDATION_MATRIX.md"


def _read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_p12_6_matrix_links_all_validated_phase12_gates():
    matrix = MATRIX.read_text(encoding="utf-8")
    result_paths = {
        "P12_0_CANONICAL_CONVERGENCE_VALIDATED": "docs/implementation/P12_0_CANONICAL_CONVERGENCE_RESULT.md",
        "P12_1_SOURCE_PORTFOLIO_CONTRACT_VALIDATED": "docs/implementation/P12_1_SOURCE_PORTFOLIO_CONTRACT_RESULT.md",
        "P12_2_ADAPTER_FRAMEWORK_V2_VALIDATED": "docs/implementation/P12_2_LIVE_ADAPTER_FRAMEWORK_V2_RESULT.md",
        "P12_3_AUTHORITATIVE_SOURCE_PACK_VALIDATED": "docs/implementation/P12_3_PRIORITY_AUTHORITATIVE_SOURCE_PACK_RESULT.md",
        "P12_4_LOCAL_LANGUAGE_DISCOVERY_VALIDATED": "docs/implementation/P12_4_LOCAL_LANGUAGE_MEDIA_DISCOVERY_PACK_RESULT.md",
        "P12_5_SOURCE_HEALTH_EGRESS_INVENTORY_VALIDATED": "docs/implementation/P12_5_SOURCE_HEALTH_EGRESS_INVENTORY_RESULT.md",
    }

    for gate, path in result_paths.items():
        source_result = _read(path)
        assert gate in source_result
        assert gate in matrix
        assert path in matrix


def test_p12_6_keeps_known_external_limitations_visible():
    matrix = MATRIX.read_text(encoding="utf-8")

    assert "PASS_WITH_KNOWN_LIMITATIONS" in matrix
    assert "European Parliament" in matrix
    assert "DEGRADED" in matrix
    assert "UNAVAILABLE/PARSER" in matrix
    assert "Haberturk" in matrix
    assert "UNAVAILABLE/UNKNOWN" in matrix
    assert "original_url must be HTTP or HTTPS" in matrix
    assert "OSCE" in matrix
    assert "content `STALE`" in matrix
    assert "uk/ru/pl/tr" in matrix
    assert "not global language coverage" in matrix.lower()


def test_p12_6_preserves_truth_and_coverage_boundaries():
    matrix = MATRIX.read_text(encoding="utf-8").lower()

    for statement in (
        "publisher/publication is not automatically the underlying origin",
        "do not create independent corroboration",
        "not automatically underlying-event truth",
        "is not independent-origin count",
        "are not truth operators",
        "`global` is scope, not proof of exhaustive world coverage",
        "a failed source does not prove an event did not occur",
        "a successful probe does not prove exhaustive coverage",
    ):
        assert statement in matrix


def test_p12_6_preserves_runtime_security_and_paid_provider_boundaries():
    matrix = MATRIX.read_text(encoding="utf-8")
    readme = _read("README.md")
    roadmap = _read("ROADMAP.md")

    assert "Runtime storage mode: PROJECT_LOCAL_ONLY" in matrix
    assert "Production/live operational status: NOT_OPERATIONAL" in matrix
    assert "Runtime storage mode: PROJECT_LOCAL_ONLY" in readme
    assert "Production/live operational status: NOT_OPERATIONAL" in readme
    assert "Runtime storage mode: PROJECT_LOCAL_ONLY" in roadmap
    assert "Production/live operational status: NOT_OPERATIONAL" in roadmap
    assert "NONE_APPROVED" in matrix
    assert "0.0.0.0/0" in matrix
    assert "broad outbound egress" in matrix
    assert "not a firewall allowlist" in matrix.lower()


def test_p12_6_candidate_does_not_predeclare_phase_gate_or_start_phase13():
    matrix = MATRIX.read_text(encoding="utf-8")
    roadmap = _read("ROADMAP.md")

    assert "Target phase gate: `PHASE_12_INTELLIGENCE_SOURCE_NETWORK_FOUNDATION_VALIDATED`" in matrix
    assert "remains `REGRESSION_PENDING`" in matrix
    assert "Phase 13 remains `NOT_STARTED`" in matrix
    assert "P12.6_PHASE_12_VALIDATION_MATRIX / NEXT_NOT_STARTED" in roadmap
    assert "Phase 13" in roadmap
    assert "NOT_STARTED" in roadmap
