import json
from pathlib import Path

from kgeopolitical_monitor.p23_4_candidate_selection import (
    classify_candidate,
    select_preparation_cohort,
)

ROOT = Path(__file__).resolve().parents[1]
QUAL = ROOT / "docs/evidence/P22_2_WAVE_B_CANDIDATE_QUALIFICATION_2026-09-19.json"


def _candidates():
    return json.loads(QUAL.read_text(encoding="utf-8"))["candidates"]


def _classified():
    remediation = {
        "uk-sanctions-list-en": "READY_FOR_OWNER_GATED_ACTIVATION_REVALIDATION",
        "russian-government-news-ru": "BLOCKED_HTTPS_TRANSPORT_TIMEOUT",
    }
    active = {"ofac-recent-actions-en", "white-house-briefings-en"}
    return [
        classify_candidate(
            c,
            repository_active_source_ids=active,
            remediation_readiness=remediation,
        )
        for c in _candidates()
    ]


def test_p23_4_preselection_preserves_no_activation_and_no_independence_credit():
    rows = _classified()
    assert len(rows) == 13
    assert all(row.activation_authorized is False for row in rows)
    assert all(row.independence_credit_granted is False for row in rows)


def test_p23_4_preselection_class_distribution_is_deterministic():
    rows = _classified()
    counts = {}
    for row in rows:
        counts[row.readiness_class] = counts.get(row.readiness_class, 0) + 1
    assert counts == {
        "ALREADY_REPOSITORY_ACTIVE": 2,
        "READY_FOR_OWNER_GATED_ACTIVATION_REVALIDATION": 1,
        "BLOCKED_TRANSPORT": 1,
        "RIGHTS_REVIEW_REQUIRED_BEFORE_FIXTURE": 3,
        "TAXONOMY_AND_RIGHTS_REVIEW_REQUIRED": 2,
        "RIGHTS_REVIEW_REQUIRED": 4,
    }


def test_p23_4_owner_gate_candidate_is_only_uksl():
    rows = _classified()
    ready = [r for r in rows if r.readiness_class == "READY_FOR_OWNER_GATED_ACTIVATION_REVALIDATION"]
    assert [r.source_id for r in ready] == ["uk-sanctions-list-en"]
    assert ready[0].expected_dimensions == ("REQUIRED_COVERAGE", "PROVENANCE_ORIGIN_DEPTH")


def test_p23_4_preparation_cohort_has_lowest_unresolved_governance_shape():
    assert select_preparation_cohort(_classified()) == (
        "anadolu-en",
        "cctv-news-zh",
        "trt-haber-tr",
    )


def test_p23_4_russian_government_remains_transport_blocked():
    rows = {r.source_id: r for r in _classified()}
    assert rows["russian-government-news-ru"].readiness_class == "BLOCKED_TRANSPORT"
    assert "NO_HTTP_FALLBACK" in rows["russian-government-news-ru"].reason_codes
