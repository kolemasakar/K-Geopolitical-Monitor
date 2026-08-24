# Confidence Engine baseline

class ConfidenceEngine:
    def calculate(self, evidence_count=0, source_reliability=0.0, independence=0.0, contradiction_penalty=0.0):
        score = (evidence_count * 0.2) + (source_reliability * 0.4) + (independence * 0.4) - contradiction_penalty
        return max(0.0, min(1.0, score))
