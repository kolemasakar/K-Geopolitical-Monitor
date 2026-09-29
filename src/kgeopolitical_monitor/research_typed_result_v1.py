"""Fail-closed typed synthetic research result validation (no provider calls)."""
from __future__ import annotations
from .research_request_v1 import validate_request, historically_available, _utc

TYPES = {"CLAIM_EVENT", "CLAIM_CORRECTION", "FORECAST_VERSION", "SOURCE_HEALTH"}
VERIFICATION = {"VERIFIED", "DISPUTED", "UNVERIFIED", "NOT_APPLICABLE"}


def validate_typed_result(request, result):
    validate_request(request)
    expected = {"schema_version", "request_id", "consumer_id", "result_id",
                "generated_at_utc", "producer_snapshot_id", "policy_version",
                "research_status", "coverage", "source_health", "records"}
    if not isinstance(result, dict) or set(result) != expected:
        raise ValueError("unapproved result fields")
    if result["schema_version"] != "kgm.research.result.v1" or (
        result["request_id"], result["consumer_id"], result["policy_version"]
    ) != (request["request_id"], request["consumer_id"], request["policy_version"]):
        raise ValueError("result correlation mismatch")
    _utc(result["generated_at_utc"])
    if not isinstance(result["result_id"], str) or not result["result_id"] or not isinstance(result["producer_snapshot_id"], str) or not result["producer_snapshot_id"]:
        raise ValueError("missing result identity")
    if result["research_status"] not in {"COMPLETE", "PARTIAL", "FAILED"}:
        raise ValueError("invalid result status")
    if result["coverage"] not in {"COMPLETE", "PARTIAL", "UNMEASURED"} or result["source_health"] not in {"HEALTHY", "DEGRADED", "STALE", "UNAVAILABLE", "UNMEASURED"}:
        raise ValueError("invalid coverage/health")
    if result["research_status"] == "COMPLETE" and (result["coverage"] != "COMPLETE" or result["source_health"] != "HEALTHY"):
        raise ValueError("false completeness")
    records = result["records"]
    if not isinstance(records, list) or len(records) > request["max_results"]:
        raise ValueError("unbounded records")
    record_fields = {"record_id", "kind", "summary", "verification", "evidence",
                     "contradictions", "revision_of", "forecast"}
    seen = set()
    for record in records:
        if not isinstance(record, dict) or set(record) != record_fields:
            raise ValueError("unapproved record fields")
        rid = record["record_id"]
        if not isinstance(rid, str) or not 1 <= len(rid) <= 128 or rid in seen:
            raise ValueError("invalid/duplicate record ID")
        seen.add(rid)
        if record["kind"] not in TYPES or record["verification"] not in VERIFICATION:
            raise ValueError("invalid typed record")
        if not isinstance(record["summary"], str) or not 1 <= len(record["summary"]) <= 1000:
            raise ValueError("invalid summary")
        evidence = record["evidence"]
        if not isinstance(evidence, list) or not 1 <= len(evidence) <= 20:
            raise ValueError("evidence required; no unsupported claims")
        for item in evidence:
            if not isinstance(item, dict) or set(item) != {"source_id", "public_url", "published_at_utc", "available_at_utc"}:
                raise ValueError("invalid evidence provenance")
            if not isinstance(item["source_id"], str) or not item["source_id"] or not isinstance(item["public_url"], str) or not item["public_url"].startswith("https://") or len(item["public_url"]) > 2048:
                raise ValueError("invalid public evidence reference")
            _utc(item["published_at_utc"])
            _utc(item["available_at_utc"])
            if request["mode"] == "HISTORICAL_AS_OF" and not historically_available(item, request["as_of_utc"]):
                raise ValueError("historical evidence lookahead")
        if not isinstance(record["contradictions"], list) or len(record["contradictions"]) > 20 or any(not isinstance(x, str) or len(x) > 128 for x in record["contradictions"]):
            raise ValueError("invalid contradictions")
        if record["revision_of"] is not None and (not isinstance(record["revision_of"], str) or len(record["revision_of"]) > 128):
            raise ValueError("invalid revision lineage")
        forecast = record["forecast"]
        if record["kind"] == "FORECAST_VERSION":
            if not isinstance(forecast, dict) or set(forecast) != {"assumptions", "scenario", "uncertainty"} or any(not isinstance(forecast[x], str) or not 1 <= len(forecast[x]) <= 1000 for x in forecast):
                raise ValueError("untyped forecast")
        elif forecast is not None:
            raise ValueError("forecast attached to factual claim")
    return result
