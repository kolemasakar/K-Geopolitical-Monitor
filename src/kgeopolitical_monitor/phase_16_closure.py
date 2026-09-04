"""P16.7 machine-readable strategic closure contract.

The closure contract is declarative and non-operational. It composes the already
validated P16.0-P16.6 gates and preserves the P16.0 runtime/security boundaries.
"""

from __future__ import annotations

from copy import deepcopy
from typing import Final

from .delivery_operator_quality_contract import (
    DELIVERY_OPERATOR_QUALITY_ARCHITECTURE_CONTRACT,
    P16_0_GATE,
)
from .delivery_intent_persistence import P16_1_GATE
from .delivery_policy import P16_2_GATE
from .delivery_transport import P16_3_GATE
from .owner_delivery_experience import P16_4_GATE
from .operator_quality_feedback import P16_5_GATE
from .quality_feedback_metrics import P16_6_GATE


P16_7_GATE: Final[str] = "PHASE_16_DELIVERY_OPERATOR_QUALITY_LOOP_VALIDATED"
PHASE_16_CLOSURE_VERSION: Final[str] = "KGM_PHASE_16_CLOSURE_V1"

PHASE_16_PREREQUISITE_GATES: Final[tuple[str, ...]] = (
    P16_0_GATE,
    P16_1_GATE,
    P16_2_GATE,
    P16_3_GATE,
    P16_4_GATE,
    P16_5_GATE,
    P16_6_GATE,
)

PHASE_16_CLOSURE_CONTRACT: Final[dict[str, object]] = {
    "version": PHASE_16_CLOSURE_VERSION,
    "phase": "PHASE_16",
    "gate": P16_7_GATE,
    "prerequisite_gates": PHASE_16_PREREQUISITE_GATES,
    "separation_invariants": (
        "DELIVERY_LIFECYCLE_SEPARATE_FROM_ALERT_LIFECYCLE",
        "DELIVERY_LIFECYCLE_SEPARATE_FROM_FACTUAL_VERIFICATION",
        "OPERATOR_FEEDBACK_NOT_FACTUAL_VERIFICATION",
        "QUALITY_METRICS_DESCRIPTIVE_ADVISORY_ONLY",
    ),
    "transport_invariants": (
        "REDACTION_BEFORE_TRANSPORT",
        "ALLOWLIST_PAYLOAD_ONLY",
        "PERSISTED_IDEMPOTENCY",
        "BOUNDED_RETRY",
        "FAILURE_ISOLATION",
        "NO_EXTERNAL_PROVIDER_ENABLED_BY_DEFAULT",
    ),
    "operator_invariants": (
        "OWNER_PROJECTION_READ_ONLY",
        "NO_PUBLIC_OWNER_DELIVERY_ROUTE",
        "FEEDBACK_APPEND_ONLY",
        "FACTUAL_CORRECTION_REQUEST_REQUIRES_PROVENANCE_REVIEW",
    ),
    "quality_invariants": (
        "COHORT_AND_SAMPLE_SIZE_EXPLICIT",
        "NO_AUTOMATIC_SOURCE_REPUTATION_REWRITE",
        "NO_AUTOMATIC_VERIFICATION_POLICY_CHANGE",
        "NO_AUTOMATIC_ALERT_THRESHOLD_CHANGE",
        "NO_AUTOMATIC_FORECAST_CHANGE",
        "NO_AUTOMATIC_PROVIDER_ACTIVATION",
    ),
    "phase_16_migrations": (
        "031_delivery_intent_audit.sql",
        "032_operator_quality_feedback.sql",
    ),
    "runtime_security_boundary": deepcopy(
        DELIVERY_OPERATOR_QUALITY_ARCHITECTURE_CONTRACT["runtime_security_boundary"]
    ),
}


def phase_16_closure_contract() -> dict[str, object]:
    return deepcopy(PHASE_16_CLOSURE_CONTRACT)


__all__ = [
    "P16_7_GATE",
    "PHASE_16_CLOSURE_VERSION",
    "PHASE_16_PREREQUISITE_GATES",
    "PHASE_16_CLOSURE_CONTRACT",
    "phase_16_closure_contract",
]
