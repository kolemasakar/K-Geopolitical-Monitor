from pathlib import Path


PLAN_PATH = (
    Path(__file__).resolve().parents[1]
    / "docs"
    / "implementation"
    / "PHASE_16_DELIVERY_OPERATOR_QUALITY_FEEDBACK_PLAN.md"
)


def _plan_text() -> str:
    return PLAN_PATH.read_text(encoding="utf-8")


def test_phase16_plan_identity_and_strategic_gate_are_explicit():
    text = _plan_text()

    assert "# Phase 16 — Delivery, Operator Experience and Quality Feedback" in text
    assert "Plan status: `IN_PROGRESS`" in text
    assert "ROADMAP basis: `v4.19`" in text
    assert "Strategic phase state: `APPROVED_SEQUENTIAL / NOT_STARTED`" in text
    assert "Strategic phase gate: `PHASE_16_DELIVERY_OPERATOR_QUALITY_LOOP_VALIDATED`" in text


def test_phase16_p16_0_validated_gate_and_evidence_are_recorded():
    text = _plan_text()

    assert "### P16.0 — Delivery / Operator / Quality Architecture Contract" in text
    assert "State: `VALIDATED`" in text
    assert "Gate: `P16_0_DELIVERY_OPERATOR_QUALITY_ARCHITECTURE_CONTRACT_VALIDATED`" in text
    assert "Validation anchor: `bab44c76abdcf5da198b007aeda90e3e30ab4796`" in text
    assert "x64 CI run `33915893936`, job `101162849016`: `594 passed, 2 warnings / SUCCESS`" in text
    assert "native ARM64 run `33915893917`, job `101162848853`: native `aarch64`, `594 passed, 2 warnings / SUCCESS`" in text
    assert "ARM64 host bootstrap: PASS" in text
    assert "ARM64 unattended one-tick: PASS" in text
    assert "ARM64 systemd contract: PASS" in text


def test_phase16_plan_sequence_is_complete_and_ordered():
    text = _plan_text()
    headings = [
        "### P16.0 — Delivery / Operator / Quality Architecture Contract",
        "### P16.1 — Canonical Delivery Intent and Audit Persistence",
        "### P16.2 — Delivery Policy, Redaction and Data-Minimized Payload Projection",
        "### P16.3 — Provider-Neutral Delivery Transport and Retry Isolation",
        "### P16.4 — Owner Delivery and Operator-Experience Read Model",
        "### P16.5 — Operator Quality Feedback Persistence",
        "### P16.6 — Deterministic Quality Metrics and Advisory Feedback Loop",
        "### P16.7 — Phase 16 Validation Matrix / Strategic Closure",
    ]

    positions = [text.index(heading) for heading in headings]
    assert positions == sorted(positions)


def test_phase16_plan_preserves_runtime_security_and_activation_boundaries():
    text = _plan_text()

    required = (
        "runtime storage remains `PROJECT_LOCAL_ONLY`",
        "mixed/shared canonical runtime remains `BLOCKED`",
        "`PRODUCTION_LIVE = NOT_OPERATIONAL`",
        "paid providers remain `NONE_APPROVED`",
        "owner execution remains disabled",
        "public ingress remains not deployed",
        "no public route, shared runtime or paid provider is introduced by Phase 16",
    )
    for phrase in required:
        assert phrase in text


def test_phase16_plan_keeps_delivery_and_feedback_non_promotional_to_truth():
    text = _plan_text()

    required = (
        "delivery state is not factual-verification state",
        "operator feedback measures usefulness, correctness perception, workflow quality or required correction; it is not independent event evidence by itself",
        "feedback cannot directly mutate factual verification",
        "quality metrics remain descriptive/advisory",
        "no self-modifying verification, alert, source, forecast or delivery policy is authorized in Phase 16",
        "replacement of P13.5/P13.6 factual verification",
    )
    for phrase in required:
        assert phrase in text


def test_phase16_plan_requires_redaction_dedup_and_failure_isolation_before_real_delivery():
    text = _plan_text()

    required = (
        "redaction and data minimization occur before any external-transport boundary",
        "deduplication and retry must be deterministic and auditable",
        "provider failure is isolated from monitoring and canonical analytical persistence",
        "local/in-memory/test sink for canonical automated tests",
        "no real external provider enabled by default",
    )
    for phrase in required:
        assert phrase in text


def test_phase16_plan_does_not_pre_authorize_new_schema_or_provider_activation():
    text = _plan_text()

    assert "migration `031`: `NONE_FOR_P16_0`" in text
    assert "Its exact schema is not pre-authorized by this plan" in text
    assert "exact schema remains subject to P16.5 review" in text
    assert "Paid providers remain forbidden unless separately approved" in text
    assert "private GPT Action activation" in text


def test_phase16_closure_requires_dual_architecture_validation():
    text = _plan_text()

    assert "full x64 repository regression passes on the exact closure anchor" in text
    assert "full native ARM64 regression passes on the same exact closure anchor" in text
    assert "ARM64 host bootstrap, unattended one-tick smoke and systemd contract remain PASS" in text
    assert "No P16 subphase is promoted from implemented to validated solely because code exists" in text
