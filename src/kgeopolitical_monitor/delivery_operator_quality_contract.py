"""Phase 16.0 delivery, operator experience and quality-feedback architecture contract.

This module is deliberately non-operational. It defines machine-readable boundaries
for delivery intent, redacted payloads, transport evidence, operator feedback and
advisory quality observations without activating a provider, deployment route or
self-modifying policy.
"""

from __future__ import annotations

from copy import deepcopy
from typing import Final


DELIVERY_OPERATOR_QUALITY_ARCHITECTURE_VERSION: Final[str] = (
    "KGM_DELIVERY_OPERATOR_QUALITY_ARCHITECTURE_V1"
)
P16_0_GATE: Final[str] = "P16_0_DELIVERY_OPERATOR_QUALITY_ARCHITECTURE_CONTRACT_VALIDATED"

DELIVERY_EVENT_INITIAL: Final[str] = "INITIAL"
DELIVERY_EVENT_UPDATE: Final[str] = "UPDATE"
DELIVERY_EVENT_RESOLUTION: Final[str] = "RESOLUTION"
DELIVERY_EVENT_TYPES: Final[tuple[str, ...]] = (
    DELIVERY_EVENT_INITIAL,
    DELIVERY_EVENT_UPDATE,
    DELIVERY_EVENT_RESOLUTION,
)

DELIVERY_INTENT_PENDING: Final[str] = "PENDING"
DELIVERY_INTENT_SUPPRESSED: Final[str] = "SUPPRESSED"
DELIVERY_INTENT_READY: Final[str] = "READY"
DELIVERY_INTENT_STATES: Final[tuple[str, ...]] = (
    DELIVERY_INTENT_PENDING,
    DELIVERY_INTENT_SUPPRESSED,
    DELIVERY_INTENT_READY,
)

TRANSPORT_ATTEMPT_ATTEMPTED: Final[str] = "ATTEMPTED"
TRANSPORT_ATTEMPT_DELIVERED: Final[str] = "DELIVERED"
TRANSPORT_ATTEMPT_FAILED: Final[str] = "FAILED"
TRANSPORT_ATTEMPT_STATES: Final[tuple[str, ...]] = (
    TRANSPORT_ATTEMPT_ATTEMPTED,
    TRANSPORT_ATTEMPT_DELIVERED,
    TRANSPORT_ATTEMPT_FAILED,
)

FEEDBACK_USEFUL: Final[str] = "USEFUL"
FEEDBACK_NOT_USEFUL: Final[str] = "NOT_USEFUL"
FEEDBACK_TIMELY: Final[str] = "TIMELY"
FEEDBACK_LATE: Final[str] = "LATE"
FEEDBACK_DUPLICATE: Final[str] = "DUPLICATE"
FEEDBACK_NOISY: Final[str] = "NOISY"
FEEDBACK_MISSING_CONTEXT: Final[str] = "MISSING_CONTEXT"
FEEDBACK_INCORRECT_PRIORITIZATION: Final[str] = "INCORRECT_PRIORITIZATION"
FEEDBACK_FACTUAL_CORRECTION_REQUESTED: Final[str] = "FACTUAL_CORRECTION_REQUESTED"
FEEDBACK_DELIVERY_FORMAT_ISSUE: Final[str] = "DELIVERY_FORMAT_ISSUE"
OPERATOR_FEEDBACK_TYPES: Final[tuple[str, ...]] = (
    FEEDBACK_USEFUL,
    FEEDBACK_NOT_USEFUL,
    FEEDBACK_TIMELY,
    FEEDBACK_LATE,
    FEEDBACK_DUPLICATE,
    FEEDBACK_NOISY,
    FEEDBACK_MISSING_CONTEXT,
    FEEDBACK_INCORRECT_PRIORITIZATION,
    FEEDBACK_FACTUAL_CORRECTION_REQUESTED,
    FEEDBACK_DELIVERY_FORMAT_ISSUE,
)

DELIVERY_OPERATOR_QUALITY_ARCHITECTURE_CONTRACT: Final[dict[str, object]] = {
    "version": DELIVERY_OPERATOR_QUALITY_ARCHITECTURE_VERSION,
    "gate": P16_0_GATE,
    "phase": "P16.0",
    "status": "ARCHITECTURE_BASELINE",
    "entities": {
        "canonical_intelligence_state": {
            "ownership": "EXISTING_CANONICAL_STORES",
            "examples": ("strategic_alert", "owner_brief", "finding", "semantic_claim"),
            "meaning": "Existing persisted intelligence objects referenced by delivery; not duplicated as a Phase 16 truth store.",
        },
        "delivery_intent": {
            "identity": "delivery_intent_id",
            "event_types": DELIVERY_EVENT_TYPES,
            "states": DELIVERY_INTENT_STATES,
            "meaning": "Auditable intent to deliver a canonical intelligence object under a deterministic policy.",
        },
        "redacted_payload": {
            "identity": "delivery_payload_id",
            "parent": "delivery_intent_id",
            "meaning": "Data-minimized allowlist projection produced before any external transport boundary.",
        },
        "transport_attempt": {
            "identity": "transport_attempt_id",
            "parent": "delivery_intent_id",
            "states": TRANSPORT_ATTEMPT_STATES,
            "meaning": "A transport execution record whose result is delivery evidence only.",
        },
        "delivery_receipt": {
            "identity": "delivery_receipt_id",
            "parent": "transport_attempt_id",
            "meaning": "Provider-neutral receipt/acknowledgement metadata that cannot establish factual correctness.",
        },
        "operator_feedback": {
            "identity": "operator_feedback_id",
            "types": OPERATOR_FEEDBACK_TYPES,
            "meaning": "Operator assessment of usefulness, timeliness, noise, prioritization, context, correction need or format.",
        },
        "quality_observation": {
            "identity": "quality_observation_id",
            "meaning": "Deterministic descriptive metric derived from persisted delivery/feedback/performance evidence.",
        },
        "advisory_quality_summary": {
            "identity": "advisory_quality_summary_id",
            "mode": "ADVISORY_ONLY",
            "meaning": "Explicit recommendations or summaries that cannot self-modify canonical policy.",
        },
    },
    "separation_chain": (
        "CANONICAL_INTELLIGENCE_STATE",
        "DELIVERY_INTENT",
        "REDACTED_PAYLOAD",
        "TRANSPORT_ATTEMPT",
        "DELIVERY_RECEIPT",
        "OPERATOR_FEEDBACK",
        "QUALITY_OBSERVATION",
        "ADVISORY_QUALITY_SUMMARY",
    ),
    "delivery_contract": {
        "rules": (
            "Delivery lifecycle remains separate from alert and factual-verification lifecycles.",
            "Delivery intent references canonical intelligence state rather than creating a shadow truth store.",
            "Initial, update and resolution delivery events are explicit and auditable.",
            "Deduplication and idempotency must be deterministic before provider transport.",
            "Suppression or delivery failure cannot mutate the underlying alert, claim or forecast truth state.",
        ),
    },
    "redaction_transport_boundary": {
        "rules": (
            "Redaction and data minimization occur before any external transport boundary.",
            "Payload fields are allowlist based and fail closed when required canonical references are unavailable, stale or ambiguous.",
            "Secrets, authentication material, private database paths and unnecessary owner/runtime metadata are forbidden delivery payload content.",
            "Provider credentials are never canonical delivery-record fields.",
            "Provider failure is isolated from monitoring and canonical analytical persistence.",
            "No external provider is enabled by this architecture contract.",
        ),
    },
    "operator_feedback_contract": {
        "types": OPERATOR_FEEDBACK_TYPES,
        "rules": (
            "Operator feedback is workflow/quality evidence, not independent event evidence by itself.",
            "A factual correction request does not directly change factual verification.",
            "Potential factual corrections must re-enter the existing provenance and verification workflow.",
            "Feedback history must be append-only and auditable when persistence is introduced.",
        ),
    },
    "quality_contract": {
        "mode": "DESCRIPTIVE_ADVISORY_ONLY",
        "rules": (
            "Quality metrics expose cohort definition and sample size when aggregated.",
            "Quality metrics cannot automatically rewrite source reputation.",
            "Quality metrics cannot automatically change verification policy.",
            "Quality metrics cannot automatically change alert thresholds.",
            "Quality metrics cannot automatically change forecast probability or calibration.",
            "Quality metrics cannot automatically activate a provider or transport.",
            "Any recommendation requires a separate explicit implementation or policy decision.",
        ),
    },
    "epistemic_invariants": (
        "Delivery state is not factual-verification state.",
        "Delivery receipt, acknowledgement, click, rating or operator action cannot promote a claim to VERIFIED.",
        "Operator feedback is not independent event evidence by itself.",
        "Delivery counts, acknowledgement rates, quality scores and feedback counts are not truth operators.",
        "Forecast calibration and performance metrics remain non-promotional to factual verification.",
        "Canonical factual verification remains owned by the current P13.5 decision through the P13.6 bridge.",
        "No self-modifying verification, alert, source, forecast or delivery policy is authorized in Phase 16.",
    ),
    "compatibility": {
        "canonical_alert_store": "M9_STRATEGIC_ALERTS_READABLE_UNCHANGED",
        "owner_operational_layer": "PHASE_14_VALIDATED_READY_NOT_ACTIVATED",
        "forecast_performance_layer": "PHASE_15_VALIDATED_DESCRIPTIVE_ONLY",
        "migration_031": "NONE_FOR_P16_0",
        "phase_14_owner_activation": "UNCHANGED_OWNER_DECISION_REQUIRED",
    },
    "runtime_security_boundary": {
        "runtime_storage": "PROJECT_LOCAL_ONLY",
        "mixed_shared_canonical_runtime": "BLOCKED",
        "production_live": "NOT_OPERATIONAL",
        "public_ingress": "NOT_APPROVED_NOT_DEPLOYED",
        "paid_providers": "NONE_APPROVED",
        "owner_execution": "DISABLED",
        "external_provider_activation": "NOT_AUTHORIZED_BY_P16_0",
    },
}


def delivery_operator_quality_architecture_contract() -> dict[str, object]:
    """Return a detached copy of the P16.0 architecture contract."""

    return deepcopy(DELIVERY_OPERATOR_QUALITY_ARCHITECTURE_CONTRACT)


__all__ = [
    "DELIVERY_OPERATOR_QUALITY_ARCHITECTURE_VERSION",
    "P16_0_GATE",
    "DELIVERY_EVENT_INITIAL",
    "DELIVERY_EVENT_UPDATE",
    "DELIVERY_EVENT_RESOLUTION",
    "DELIVERY_EVENT_TYPES",
    "DELIVERY_INTENT_PENDING",
    "DELIVERY_INTENT_SUPPRESSED",
    "DELIVERY_INTENT_READY",
    "DELIVERY_INTENT_STATES",
    "TRANSPORT_ATTEMPT_ATTEMPTED",
    "TRANSPORT_ATTEMPT_DELIVERED",
    "TRANSPORT_ATTEMPT_FAILED",
    "TRANSPORT_ATTEMPT_STATES",
    "OPERATOR_FEEDBACK_TYPES",
    "DELIVERY_OPERATOR_QUALITY_ARCHITECTURE_CONTRACT",
    "delivery_operator_quality_architecture_contract",
]
