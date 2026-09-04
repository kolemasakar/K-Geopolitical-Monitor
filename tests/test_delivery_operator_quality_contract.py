from kgeopolitical_monitor.delivery_operator_quality_contract import (
    DELIVERY_EVENT_TYPES,
    DELIVERY_INTENT_STATES,
    DELIVERY_OPERATOR_QUALITY_ARCHITECTURE_VERSION,
    OPERATOR_FEEDBACK_TYPES,
    P16_0_GATE,
    TRANSPORT_ATTEMPT_STATES,
    delivery_operator_quality_architecture_contract,
)


def test_p16_0_contract_identity_gate_and_phase_are_explicit():
    contract = delivery_operator_quality_architecture_contract()

    assert DELIVERY_OPERATOR_QUALITY_ARCHITECTURE_VERSION == (
        "KGM_DELIVERY_OPERATOR_QUALITY_ARCHITECTURE_V1"
    )
    assert P16_0_GATE == "P16_0_DELIVERY_OPERATOR_QUALITY_ARCHITECTURE_CONTRACT_VALIDATED"
    assert contract["version"] == DELIVERY_OPERATOR_QUALITY_ARCHITECTURE_VERSION
    assert contract["gate"] == P16_0_GATE
    assert contract["phase"] == "P16.0"
    assert contract["status"] == "ARCHITECTURE_BASELINE"


def test_p16_0_separation_chain_keeps_truth_delivery_feedback_and_quality_distinct():
    contract = delivery_operator_quality_architecture_contract()

    assert tuple(contract["separation_chain"]) == (
        "CANONICAL_INTELLIGENCE_STATE",
        "DELIVERY_INTENT",
        "REDACTED_PAYLOAD",
        "TRANSPORT_ATTEMPT",
        "DELIVERY_RECEIPT",
        "OPERATOR_FEEDBACK",
        "QUALITY_OBSERVATION",
        "ADVISORY_QUALITY_SUMMARY",
    )
    assert contract["entities"]["delivery_intent"]["identity"] == "delivery_intent_id"
    assert contract["entities"]["redacted_payload"]["parent"] == "delivery_intent_id"
    assert contract["entities"]["transport_attempt"]["parent"] == "delivery_intent_id"
    assert contract["entities"]["delivery_receipt"]["parent"] == "transport_attempt_id"
    assert contract["entities"]["advisory_quality_summary"]["mode"] == "ADVISORY_ONLY"


def test_p16_0_delivery_and_transport_states_are_typed_and_non_truth_states():
    contract = delivery_operator_quality_architecture_contract()

    assert DELIVERY_EVENT_TYPES == ("INITIAL", "UPDATE", "RESOLUTION")
    assert DELIVERY_INTENT_STATES == ("PENDING", "SUPPRESSED", "READY")
    assert TRANSPORT_ATTEMPT_STATES == ("ATTEMPTED", "DELIVERED", "FAILED")
    assert tuple(contract["entities"]["delivery_intent"]["event_types"]) == DELIVERY_EVENT_TYPES
    assert tuple(contract["entities"]["delivery_intent"]["states"]) == DELIVERY_INTENT_STATES
    assert tuple(contract["entities"]["transport_attempt"]["states"]) == TRANSPORT_ATTEMPT_STATES

    invariants = " ".join(contract["epistemic_invariants"])
    assert "Delivery state is not factual-verification state" in invariants
    assert "cannot promote a claim to VERIFIED" in invariants
    assert "not truth operators" in invariants


def test_p16_0_redaction_happens_before_transport_and_sensitive_payload_content_is_forbidden():
    contract = delivery_operator_quality_architecture_contract()
    rules = " ".join(contract["redaction_transport_boundary"]["rules"])

    assert "before any external transport boundary" in rules
    assert "allowlist based" in rules
    assert "Secrets, authentication material, private database paths" in rules
    assert "Provider credentials are never canonical delivery-record fields" in rules
    assert "Provider failure is isolated" in rules
    assert "No external provider is enabled" in rules


def test_p16_0_operator_feedback_is_typed_and_non_promotional_to_verification():
    contract = delivery_operator_quality_architecture_contract()

    assert "USEFUL" in OPERATOR_FEEDBACK_TYPES
    assert "NOT_USEFUL" in OPERATOR_FEEDBACK_TYPES
    assert "FACTUAL_CORRECTION_REQUESTED" in OPERATOR_FEEDBACK_TYPES
    assert "DELIVERY_FORMAT_ISSUE" in OPERATOR_FEEDBACK_TYPES
    assert tuple(contract["operator_feedback_contract"]["types"]) == OPERATOR_FEEDBACK_TYPES

    rules = " ".join(contract["operator_feedback_contract"]["rules"])
    assert "not independent event evidence by itself" in rules
    assert "does not directly change factual verification" in rules
    assert "re-enter the existing provenance and verification workflow" in rules


def test_p16_0_quality_loop_is_advisory_and_cannot_self_modify_policy():
    contract = delivery_operator_quality_architecture_contract()
    quality = contract["quality_contract"]
    rules = " ".join(quality["rules"])

    assert quality["mode"] == "DESCRIPTIVE_ADVISORY_ONLY"
    assert "cannot automatically rewrite source reputation" in rules
    assert "cannot automatically change verification policy" in rules
    assert "cannot automatically change alert thresholds" in rules
    assert "cannot automatically change forecast probability or calibration" in rules
    assert "cannot automatically activate a provider or transport" in rules
    assert "requires a separate explicit implementation or policy decision" in rules


def test_p16_0_preserves_compatibility_runtime_and_activation_boundaries_without_migration():
    contract = delivery_operator_quality_architecture_contract()
    compatibility = contract["compatibility"]
    boundary = contract["runtime_security_boundary"]

    assert compatibility["canonical_alert_store"] == "M9_STRATEGIC_ALERTS_READABLE_UNCHANGED"
    assert compatibility["owner_operational_layer"] == "PHASE_14_VALIDATED_READY_NOT_ACTIVATED"
    assert compatibility["forecast_performance_layer"] == "PHASE_15_VALIDATED_DESCRIPTIVE_ONLY"
    assert compatibility["migration_031"] == "NONE_FOR_P16_0"
    assert compatibility["phase_14_owner_activation"] == "UNCHANGED_OWNER_DECISION_REQUIRED"

    assert boundary == {
        "runtime_storage": "PROJECT_LOCAL_ONLY",
        "mixed_shared_canonical_runtime": "BLOCKED",
        "production_live": "NOT_OPERATIONAL",
        "public_ingress": "NOT_APPROVED_NOT_DEPLOYED",
        "paid_providers": "NONE_APPROVED",
        "owner_execution": "DISABLED",
        "external_provider_activation": "NOT_AUTHORIZED_BY_P16_0",
    }


def test_p16_0_contract_returns_detached_copy():
    first = delivery_operator_quality_architecture_contract()
    second = delivery_operator_quality_architecture_contract()

    first["entities"]["delivery_intent"]["states"] = ("CORRUPTED",)
    first["runtime_security_boundary"]["production_live"] = "OPERATIONAL"

    assert second["entities"]["delivery_intent"]["states"] == DELIVERY_INTENT_STATES
    assert second["runtime_security_boundary"]["production_live"] == "NOT_OPERATIONAL"
