"""Confidence calculation baseline and compatibility API."""


class ConfidenceEngine:
    def calculate(
        self,
        evidence_count=0,
        source_reliability=0.0,
        independence=0.0,
        contradiction_penalty=0.0,
    ):
        score = (
            (evidence_count * 0.2)
            + (source_reliability * 0.4)
            + (independence * 0.4)
            - contradiction_penalty
        )
        return max(0.0, min(1.0, score))


def _value(item, name, default=None):
    if isinstance(item, dict):
        return item.get(name, default)
    return getattr(item, name, default)


def _normalize_reliability(value) -> float:
    if isinstance(value, (int, float)):
        return max(0.0, min(1.0, float(value)))

    mapping = {
        "LOW": 0.25,
        "MEDIUM": 0.5,
        "HIGH": 0.8,
        "VERY_HIGH": 1.0,
    }
    return mapping.get(str(value).upper(), 0.5)


def calculate_confidence(evidence_items=None, contradictions=None) -> float:
    """Calculate workflow confidence from evidence objects or dictionaries."""

    evidence_items = list(evidence_items or [])
    contradictions = list(contradictions or [])

    if not evidence_items:
        return 0.0

    reliabilities = [
        _normalize_reliability(_value(item, "reliability", 0.5))
        for item in evidence_items
    ]
    source_reliability = sum(reliabilities) / len(reliabilities)

    source_ids = {
        _value(item, "source_id")
        for item in evidence_items
        if _value(item, "source_id") is not None
    }
    independence = len(source_ids) / len(evidence_items) if source_ids else 0.0
    contradiction_penalty = min(1.0, len(contradictions) * 0.2)

    return ConfidenceEngine().calculate(
        evidence_count=len(evidence_items),
        source_reliability=source_reliability,
        independence=independence,
        contradiction_penalty=contradiction_penalty,
    )
