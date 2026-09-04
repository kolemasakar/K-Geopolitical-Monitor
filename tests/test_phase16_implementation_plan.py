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
    assert "Plan status: `COMPLETE / VALIDATED`" in text
    assert "ROADMAP basis: `v4.20`" in text
    assert "Strategic phase state: `VALIDATED`" in text
    assert "Strategic phase gate: `PHASE_16_DELIVERY_OPERATOR_QUALITY_LOOP_VALIDATED`" in text
    assert "Closure validation anchor: `18c2d5eed4145500bf72bbeeb0b6bbc92e8c7553`" in text


def test_phase16_p16_0_validated_gate_and_evidence_are_recorded():
    text = _plan_text()

    assert "### P16.0 — Delivery / Operator / Quality Architecture Contract" in text
    assert "State: `VALIDATED`" in text
    assert "Gate: `P16_0_DELIVERY_OPERATOR_QUALITY_ARCHITECTURE_CONTRACT_VALIDATED`" in text
    assert "Validation anchor: `bab44c76abdcf5da198b007aeda90e3e30ab4796`" in text
    assert "x64 run `33915893936`, job `101162849016`: `594 passed, 2 warnings / SUCCESS`" in text
    assert "native ARM64 run `33915893917`, job `101162848853`: `594 passed, 2 warnings / SUCCESS`, native `aarch64`, bootstrap/unattended/systemd PASS" in text


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
    for heading in headings:
        section = text[text.index(heading) :]
        assert "State: `VALIDATED`" in section


def test_phase16_plan_preserves_runtime_security_and_activation_boundaries():
    text = _plan_text()

    required = (
        "runtime storage remains `PROJECT_LOCAL_ONLY`",
        "mixed/shared canonical runtime remains `BLOCKED`",
        "`PRODUCTION_LIVE = NOT_OPERATIONAL`",
        "paid providers remain `NONE_APPROVED`",
        "owner execution remains disabled/separately gated",
        "public ingress remains not deployed",
        "no public route, shared runtime or paid provider is introduced by Phase 16",
    )
    for phrase in required:
        assert phrase in text


def test_phase16_plan_keeps_delivery_and_feedback_non_promotional_to_truth():
    text = _plan_text()

    required = (
        "delivery state is not factual-verification state",
        "operator feedback is workflow/quality evidence, not independent event evidence by itself",
        "feedback cannot directly mutate factual verification",
        "quality analysis is descriptive/advisory until a separate policy-change decision",
        "no self-modifying verification, alert, source, forecast or delivery policy is authorized in Phase 16",
        "replacement of P13.5/P13.6 factual verification",
    )
    for phrase in required:
        assert phrase in text


def test_phase16_plan_requires_redaction_dedup_and_failure_isolation_before_real_delivery():
    text = _plan_text()

    required = (
        "redaction and data minimization occur before the transport boundary",
        "deduplication and retry are deterministic and auditable",
        "provider failure is isolated from monitoring and canonical analytical persistence",
        "canonical deterministic validation sink is `InMemoryDeliverySink`",
        "no real external provider enabled by default",
    )
    for phrase in required:
        assert phrase in text


def test_phase16_plan_records_schema_and_provider_activation_boundaries_after_validation():
    text = _plan_text()

    assert "No migration. No provider, public ingress, owner execution or production/live activation." in text
    assert "Migration: `031_delivery_intent_audit.sql`." in text
    assert "Migration: `032_operator_quality_feedback.sql`." in text
    assert "Telegram, email, Slack, SMS, push, webhook and other external channels remain outside the validated Phase-16 activation scope." in text
    assert "private GPT Action activation" in text
    assert "paid/external provider use" in text


def test_phase16_closure_records_dual_architecture_validation():
    text = _plan_text()

    assert "Closure validation anchor: `18c2d5eed4145500bf72bbeeb0b6bbc92e8c7553`" in text
    assert "x64 run `33920882676`, job `101178676207`: `638 passed, 2 warnings / SUCCESS`" in text
    assert "native ARM64 run `33920882682`, job `101178676586`: `638 passed, 2 warnings / SUCCESS`, native `aarch64`, bootstrap/unattended/systemd PASS" in text
    assert "Every implementation gate was validated on an exact repository anchor with full x64 and native ARM64 regression" in text
    assert "Strategic decision: `PHASE_16_DELIVERY_OPERATOR_QUALITY_LOOP_VALIDATED`" in text
