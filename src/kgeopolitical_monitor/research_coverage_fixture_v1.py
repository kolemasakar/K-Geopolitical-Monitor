"""Read-only synthetic coverage assessment for historical research fixtures.

Coverage is UNKNOWN unless a declared corpus window and explicit evidence
availability are provided. This does not inspect the live KGM corpus.
"""
from __future__ import annotations
from .research_request_v1 import validate_request, historically_available, _utc


def assess_fixture_coverage(request, *, corpus_windows, evidence):
    validate_request(request)
    if not isinstance(corpus_windows, list) or not isinstance(evidence, list):
        raise ValueError("explicit corpus windows and evidence required")
    start, end = _utc(request["period_start_utc"]), _utc(request["period_end_utc"])
    windows = []
    for window in corpus_windows:
        if not isinstance(window, dict) or set(window) != {"start_utc", "end_utc", "coverage_verified"} or type(window["coverage_verified"]) is not bool:
            raise ValueError("unapproved corpus window")
        a, b = _utc(window["start_utc"]), _utc(window["end_utc"])
        if a > b:
            raise ValueError("reversed window")
        if request["mode"] == "HISTORICAL_AS_OF" and b > _utc(request["as_of_utc"]):
            b = _utc(request["as_of_utc"])
        if window["coverage_verified"] and a < b:
            windows.append((a, b))
    cursor = start
    for a, b in sorted(windows):
        if a <= cursor:
            cursor = max(cursor, b)
    complete = cursor >= end
    available = 0
    for item in evidence:
        if request["mode"] == "HISTORICAL_AS_OF":
            if historically_available(item, request["as_of_utc"]):
                available += 1
        elif isinstance(item, dict) and "available_at_utc" in item:
            _utc(item["available_at_utc"])
            available += 1
    return {"coverage": "COMPLETE" if complete else "UNMEASURED",
            "eligible_evidence_count": available,
            "gap_detected": not complete,
            "no_news_conclusion_authorized": complete and available == 0}
