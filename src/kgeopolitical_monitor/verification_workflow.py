"""M1 verification workflow orchestration baseline."""

from .confidence_engine import calculate_confidence


def verify_claim(claim, evidence_items, contradictions=None):
    score = calculate_confidence(
        evidence_items=evidence_items,
        contradictions=contradictions or [],
    )
    return {
        "claim": claim,
        "confidence": score,
        "status": "VERIFIED" if score >= 0.75 else "PARTLY_VERIFIED",
    }
