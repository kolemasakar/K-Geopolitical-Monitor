from __future__ import annotations

from pathlib import Path

from kgeopolitical_monitor.delivery_intent_persistence import P16_1_GATE
from kgeopolitical_monitor.delivery_operator_quality_contract import (
    DELIVERY_OPERATOR_QUALITY_ARCHITECTURE_CONTRACT,
    P16_0_GATE,
)
from kgeopolitical_monitor.delivery_policy import P16_2_GATE
from kgeopolitical_monitor.delivery_transport import P16_3_GATE
from kgeopolitical_monitor.operator_quality_feedback import P16_5_GATE
from kgeopolitical_monitor.owner_delivery_experience import P16_4_GATE
from kgeopolitical_monitor.phase_16_closure import (
    P16_7_GATE,
    PHASE_16_CLOSURE_CONTRACT,
    PHASE_16_PREREQUISITE_GATES,
)
from kgeopolitical_monitor.quality_feedback_metrics import P16_6_GATE


ROOT = Path(__file__).resolve().parents[1]


def test_p16_7_strategic_gate_and_prerequisites_are_exact():
    assert P16_7_GATE == "PHASE_16_DELIVERY_OPERATOR_QUALITY_LOOP_VALIDATED"
    assert PHASE_16_PREREQUISITE_GATES == (
        P16_0_GATE,
        P16_1_GATE,
        P16_2_GATE,
        P16_3_GATE,
        P16_4_GATE,
        P16_5_GATE,
        P16_6_GATE,
    )
    assert PHASE_16_PREREQUISITE_GATES == (
        "P16_0_DELIVERY_OPERATOR_QUALITY_ARCHITECTURE_CONTRACT_VALIDATED",
        "P16_1_DELIVERY_INTENT_AUDIT_PERSISTENCE_VALIDATED",
        "P16_2_DELIVERY_POLICY_REDACTION_VALIDATED",
        "P16_3_PROVIDER_NEUTRAL_DELIVERY_TRANSPORT_VALIDATED",
        "P16_4_OWNER_OPERATOR_EXPERIENCE_PROJECTION_VALIDATED",
        "P16_5_OPERATOR_QUALITY_FEEDBACK_PERSISTENCE_VALIDATED",
        "P16_6_ADVISORY_QUALITY_FEEDBACK_LOOP_VALIDATED",
    )


def test_p16_7_preserves_runtime_security_boundary():
    boundary = PHASE_16_CLOSURE_CONTRACT["runtime_security_boundary"]
    assert boundary == DELIVERY_OPERATOR_QUALITY_ARCHITECTURE_CONTRACT["runtime_security_boundary"]
    assert boundary["runtime_storage"] == "PROJECT_LOCAL_ONLY"
    assert boundary["mixed_shared_canonical_runtime"] == "BLOCKED"
    assert boundary["production_live"] == "NOT_OPERATIONAL"
    assert boundary["public_ingress"] == "NOT_APPROVED_NOT_DEPLOYED"
    assert boundary["paid_providers"] == "NONE_APPROVED"
    assert boundary["owner_execution"] == "DISABLED"


def test_p16_7_has_only_expected_phase_16_migration_roles_without_future_ban():
    migration_dir = ROOT / "migrations"
    expected = {
        "031_delivery_intent_audit.sql",
        "032_operator_quality_feedback.sql",
    }
    assert expected.issubset({path.name for path in migration_dir.glob("*.sql")})
    assert tuple(PHASE_16_CLOSURE_CONTRACT["phase_16_migrations"]) == tuple(sorted(expected))

    delivery_sql = (migration_dir / "031_delivery_intent_audit.sql").read_text(encoding="utf-8")
    feedback_sql = (migration_dir / "032_operator_quality_feedback.sql").read_text(encoding="utf-8")
    assert "delivery_intents" in delivery_sql
    assert "delivery_intent_audit_events" in delivery_sql
    assert "delivery_transport_attempts" in delivery_sql
    assert "delivery_receipts" in delivery_sql
    assert "operator_quality_feedback" in feedback_sql
    assert "BEFORE UPDATE" in delivery_sql and "BEFORE DELETE" in delivery_sql
    assert "BEFORE UPDATE" in feedback_sql and "BEFORE DELETE" in feedback_sql


def test_p16_7_transport_remains_local_test_only_in_phase_16_module():
    transport = (ROOT / "src" / "kgeopolitical_monitor" / "delivery_transport.py").read_text(
        encoding="utf-8"
    )
    assert "InMemoryDeliverySink" in transport
    assert "no external provider is configured or activated" in transport.lower()
    for forbidden in ("import requests", "import httpx", "import smtplib", "slack_sdk", "telegram"):
        assert forbidden not in transport.lower()


def test_p16_7_owner_and_feedback_interfaces_are_not_public_backend_routes():
    backend = (ROOT / "src" / "kgeopolitical_monitor" / "backend_action_api.py").read_text(
        encoding="utf-8"
    )
    forbidden = (
        "SQLiteOwnerDeliveryExperienceProjection",
        "owner_delivery_experience",
        "SQLiteOperatorQualityFeedbackRepository",
        "operator_quality_feedback",
        "SQLiteDeliveryDispatcher",
    )
    for name in forbidden:
        assert name not in backend


def test_p16_7_quality_and_feedback_cannot_be_truth_operators_by_contract():
    separation = tuple(PHASE_16_CLOSURE_CONTRACT["separation_invariants"])
    quality = tuple(PHASE_16_CLOSURE_CONTRACT["quality_invariants"])
    operator = tuple(PHASE_16_CLOSURE_CONTRACT["operator_invariants"])
    assert "DELIVERY_LIFECYCLE_SEPARATE_FROM_FACTUAL_VERIFICATION" in separation
    assert "OPERATOR_FEEDBACK_NOT_FACTUAL_VERIFICATION" in separation
    assert "QUALITY_METRICS_DESCRIPTIVE_ADVISORY_ONLY" in separation
    assert "FACTUAL_CORRECTION_REQUEST_REQUIRES_PROVENANCE_REVIEW" in operator
    assert "NO_AUTOMATIC_SOURCE_REPUTATION_REWRITE" in quality
    assert "NO_AUTOMATIC_VERIFICATION_POLICY_CHANGE" in quality
    assert "NO_AUTOMATIC_ALERT_THRESHOLD_CHANGE" in quality
    assert "NO_AUTOMATIC_FORECAST_CHANGE" in quality
    assert "NO_AUTOMATIC_PROVIDER_ACTIVATION" in quality
