from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def _read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_p13_3_historical_gate_survives_p13_4_and_later_progress():
    roadmap = _read("ROADMAP.md")
    readme = _read("README.md")
    plan = _read("docs/implementation/PHASE_13_SEMANTIC_VERIFICATION_PROVENANCE_PLAN.md")
    implementation = _read("docs/implementation/P13_3_EVIDENCE_RELATION_INDEPENDENCE.md")
    result = _read("docs/implementation/P13_3_EVIDENCE_RELATION_INDEPENDENCE_RESULT.md")
    checkpoint = _read("docs/checkpoints/PROJECT_CHECKPOINT_2026-09-02_P13_3_EVIDENCE_RELATION_INDEPENDENCE_VALIDATED.md")

    for document in (roadmap, readme, plan, implementation, result, checkpoint):
        assert "P13_3_EVIDENCE_RELATION_INDEPENDENCE_VALIDATED" in document

    assert "P13.3 — Evidence Relation and Independence Assessment\nState: `VALIDATED`" in roadmap
    assert "P13_4_TYPED_CONTRADICTION_MODEL_VALIDATED" in roadmap
    assert "P13_4_TYPED_CONTRADICTION_MODEL_VALIDATED" in readme
    assert "P13_4_TYPED_CONTRADICTION_MODEL_VALIDATED" in plan


def test_p13_3_implementation_and_formal_closure_evidence_remain_exact():
    implementation_records = (
        _read("docs/implementation/P13_3_EVIDENCE_RELATION_INDEPENDENCE.md"),
        _read("docs/implementation/P13_3_EVIDENCE_RELATION_INDEPENDENCE_RESULT.md"),
        _read("docs/checkpoints/PROJECT_CHECKPOINT_2026-09-02_P13_3_EVIDENCE_RELATION_INDEPENDENCE_VALIDATED.md"),
    )
    for document in implementation_records:
        assert "639d6b2e64d618edfbe742636cb2ac0f663c68ee" in document
        assert "434 passed, 1 warning / SUCCESS" in document

    closure_records = (
        _read("ROADMAP.md"),
        _read("README.md"),
        _read("DATA_MODELS.md"),
        _read("docs/implementation/PHASE_13_SEMANTIC_VERIFICATION_PROVENANCE_PLAN.md"),
    )
    for document in closure_records:
        assert "9023dc22d36525b4dc9babbf21d97d184a1c110e" in document
        assert "438 passed, 1 warning / SUCCESS" in document

    assert "33594299961" in closure_records[0] and "100134512548" in closure_records[0]
    assert "33594299979" in closure_records[0] and "100134512479" in closure_records[0]


def test_p13_3_closure_preserves_independence_truth_and_runtime_boundaries():
    roadmap = _read("ROADMAP.md")
    readme = _read("README.md")
    result = _read("docs/implementation/P13_3_EVIDENCE_RELATION_INDEPENDENCE_RESULT.md")

    for document in (roadmap, readme, result):
        assert "Production/live operational status: NOT_OPERATIONAL" in document
        assert "Runtime storage mode: PROJECT_LOCAL_ONLY" in document

    lower = result.lower()
    assert "different publisher" in lower
    assert "not sufficient" in lower or "never sufficient" in lower
    assert "independent" in lower
    assert "verification" in lower
    assert "does not" in lower
    assert "live compatibility cutover" in lower


def test_p13_3_scope_stops_before_contradiction_policy_and_cutover():
    result = _read("docs/implementation/P13_3_EVIDENCE_RELATION_INDEPENDENCE_RESULT.md")
    implementation = _read("docs/implementation/P13_3_EVIDENCE_RELATION_INDEPENDENCE.md")
    combined = (result + implementation).lower()

    for token in (
        "p13.4",
        "contradiction",
        "p13.5",
        "verification",
        "factual confidence",
        "p13.6",
        "live",
    ):
        assert token in combined

    assert "semantic_evidence_relation_versions" in combined
    assert "semantic_independence_assessment_versions" in combined
