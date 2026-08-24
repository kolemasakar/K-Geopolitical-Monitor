"""Feedback learning baseline.

Tracks verification outcomes and produces adaptation signals.
"""

from dataclasses import dataclass


@dataclass
class LearningFeedback:
    source_id: str
    prediction_correct: bool
    confidence_error: float


class FeedbackLearningEngine:
    def evaluate(self, feedback: LearningFeedback) -> float:
        score = 0.1 if feedback.prediction_correct else -0.1
        score -= feedback.confidence_error * 0.05
        return max(-1.0, min(1.0, score))
