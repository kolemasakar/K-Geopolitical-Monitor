from kgeopolitical_monitor.feedback_learning import FeedbackLearningEngine, LearningFeedback


def test_feedback_learning_positive():
    engine = FeedbackLearningEngine()
    result = engine.evaluate(LearningFeedback('source', True, 0.0))
    assert result > 0


def test_feedback_learning_negative():
    engine = FeedbackLearningEngine()
    result = engine.evaluate(LearningFeedback('source', False, 0.0))
    assert result < 0
