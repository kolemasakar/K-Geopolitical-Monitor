"""Verification workflow baseline."""

VERIFICATION_STATES = [
    "DETECTED",
    "PARTLY_VERIFIED",
    "VERIFIED",
    "DISPUTED",
    "UNVERIFIABLE",
]

CONFIDENCE_LEVELS = [
    "LOW",
    "MEDIUM",
    "HIGH",
    "VERY_HIGH",
]


def evaluate_claim(evidence_count: int) -> str:
    if evidence_count >= 2:
        return "PARTLY_VERIFIED"
    return "DETECTED"
