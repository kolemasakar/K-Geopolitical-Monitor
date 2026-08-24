from kgeopolitical_monitor.verification import evaluate_claim


def test_claim_verification_baseline():
    assert evaluate_claim(0) == "DETECTED"
    assert evaluate_claim(2) == "PARTLY_VERIFIED"
