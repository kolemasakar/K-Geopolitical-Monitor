from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def _read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_phase13_canonical_closure_candidate_is_synchronized_and_fail_closed():
    roadmap = _read("ROADMAP.md")
    readme = _read("README.md")
    data_models = _read("DATA_MODELS.md")
    plan = _read("docs/implementation/PHASE_13_SEMANTIC_VERIFICATION_PROVENANCE_PLAN.md")
    history = _read("PROJECT_HISTORY.md")
    matrix = _read("docs/implementation/P13_6_LIVE_COMPATIBILITY_CUTOVER_VALIDATION_MATRIX.md")
    result = _read("docs/implementation/P13_6_LIVE_COMPATIBILITY_CUTOVER_RESULT.md")
    checkpoint = _read("docs/checkpoints/PROJECT_CHECKPOINT_2026-09-04_P13_6_IMPLEMENTATION_VALIDATED.md")

    canonical = (roadmap, readme, data_models, plan, history, matrix, result, checkpoint)
    for document in canonical:
        assert "3b8d75d05168561898ba3fa592d0d7bdad5a5dd4" in document
        assert "PENDING_EXACT_HEAD_CLOSURE_REGRESSION" in document
        assert "Production/live operational status: NOT_OPERATIONAL" in document
        assert "Runtime storage mode: PROJECT_LOCAL_ONLY" in document

    assert "State: `CLOSURE_CANDIDATE / AWAITING_EXACT_HEAD_REGRESSION`" in roadmap
    assert "P13.6 — Live Compatibility Cutover and Phase 13 Validation Matrix\nState: `IMPLEMENTATION_VALIDATED / CLOSURE_CANDIDATE`" in roadmap
    assert "NOT_YET_GRANTED" in checkpoint


def test_phase13_candidate_preserves_exact_p13_6_and_p13_5_closure_evidence():
    combined = "\n".join(
        _read(path)
        for path in (
            "ROADMAP.md",
            "README.md",
            "DATA_MODELS.md",
            "docs/implementation/PHASE_13_SEMANTIC_VERIFICATION_PROVENANCE_PLAN.md",
            "PROJECT_HISTORY.md",
            "docs/implementation/P13_6_LIVE_COMPATIBILITY_CUTOVER_VALIDATION_MATRIX.md",
        )
    )
    for token in (
        "d2e80fe8a1bd998ca422be1e1001744be0e9e6e3",
        "33856550956",
        "100971101911",
        "33856550913",
        "100971101835",
        "480 passed, 2 warnings / SUCCESS",
        "33857212159",
        "100973174656",
        "33857212157",
        "100973174256",
        "489 passed, 2 warnings / SUCCESS",
        "2a482eb85b118fa5ea46396fa92707733dad5159",
        "33857629735",
        "100974493101",
        "33857629714",
        "100974493074",
        "493 passed, 2 warnings / SUCCESS",
    ):
        assert token in combined


def test_phase13_candidate_keeps_legacy_truth_and_reproducibility_boundaries():
    combined = "\n".join(
        _read(path)
        for path in (
            "ROADMAP.md",
            "README.md",
            "DATA_MODELS.md",
            "docs/implementation/PHASE_13_SEMANTIC_VERIFICATION_PROVENANCE_PLAN.md",
            "docs/implementation/P13_6_LIVE_COMPATIBILITY_CUTOVER_VALIDATION_MATRIX.md",
        )
    ).lower()
    assert "migration 028" in combined and "none" in combined
    assert "origin_host" in combined
    assert "independent_origin_count" in combined
    assert "scalar confidence" in combined
    assert "not_instrumented" in combined
    assert "not reconstructed" in combined or "never reconstructed" in combined
    assert "count-only" in combined
    assert "coverage confidence cannot promote factual verification confidence" in combined
    assert "publisher/publication is not automatically the underlying origin" in combined


def test_phase14_remains_sequential_and_requires_owner_activation_after_phase13_candidate():
    roadmap = _read("ROADMAP.md")
    readme = _read("README.md")
    plan = _read("docs/implementation/PHASE_13_SEMANTIC_VERIFICATION_PROVENANCE_PLAN.md")
    for document in (roadmap, readme, plan):
        assert "OWNER_ONLY_OPERATIONAL_ACTIVATION = OWNER_DECISION_REQUIRED" in document
    assert "Phase 14 — Owner Operational Intelligence Activation\nState: `APPROVED_SEQUENTIAL / NOT_STARTED`" in roadmap
    assert "PRODUCTION_LIVE = NOT_OPERATIONAL" in roadmap
