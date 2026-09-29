"""No-lookahead historical corpus window fixture checks."""
from kgeopolitical_monitor.research_coverage_fixture_v1 import assess_fixture_coverage
from test_research_request_v1 import sample


def test_missing_corpus_is_unmeasured():
    report = assess_fixture_coverage(sample(), corpus_windows=[], evidence=[])
    assert report["coverage"] == "UNMEASURED"
    assert not report["no_news_conclusion_authorized"]


def test_verified_synthetic_window_not_proof_of_no_news():
    report = assess_fixture_coverage(sample(), corpus_windows=[
        {"start_utc": "2026-09-01T00:00:00Z",
         "end_utc": "2026-09-02T00:00:00Z", "coverage_verified": True}], evidence=[])
    assert report["coverage"] == "COMPLETE"
    assert not report["no_news_conclusion_authorized"]


def test_unverified_window_rejected_as_complete():
    report = assess_fixture_coverage(sample(), corpus_windows=[
        {"start_utc": "2026-09-01T00:00:00Z",
         "end_utc": "2026-09-02T00:00:00Z", "coverage_verified": False}], evidence=[])
    assert report["gap_detected"]


def test_late_evidence_not_eligible():
    report = assess_fixture_coverage(sample(), corpus_windows=[], evidence=[
        {"published_at_utc": "2026-09-01T00:00:00Z",
         "available_at_utc": "2026-09-04T00:00:00Z"}])
    assert report["eligible_evidence_count"] == 0
