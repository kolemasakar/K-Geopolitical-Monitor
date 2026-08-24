from kgeopolitical_monitor.verification_workflow import verify_claim


def test_verify_claim_returns_status():
    result = verify_claim("test claim", [], [])
    assert result["status"] in ["VERIFIED", "PARTLY_VERIFIED"]
