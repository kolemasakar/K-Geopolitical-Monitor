"""Isolated request-correlated synthetic research lifecycle; no provider calls."""
from __future__ import annotations
import hashlib
import json
from .research_request_v1 import validate_request, historically_available, _utc

TRANSITIONS = {"RECEIVED": {"ACCEPTED", "FAILED", "EXPIRED"},
               "ACCEPTED": {"PROCESSING", "FAILED", "EXPIRED"},
               "PROCESSING": {"COMPLETE", "PARTIAL", "FAILED", "EXPIRED"},
               "COMPLETE": set(), "PARTIAL": set(), "FAILED": set(), "EXPIRED": set()}


def request_digest(request):
    validate_request(request)
    return hashlib.sha256(json.dumps(request, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


class SyntheticResearchJob:
    """One in-memory deterministic fixture job; not a durable production queue."""

    def __init__(self, request):
        self.request = dict(validate_request(request))
        self.digest = request_digest(request)
        self.status = "RECEIVED"
        self.result = None

    def retry(self, request):
        if request["request_id"] != self.request["request_id"] or request_digest(request) != self.digest:
            raise ValueError("idempotency conflict")
        return self

    def transition(self, next_status):
        if next_status not in TRANSITIONS[self.status]:
            raise ValueError("illegal lifecycle transition")
        self.status = next_status

    def complete_fixture(self, evidence, *, generated_at_utc, snapshot_id,
                         coverage, source_health):
        if self.status != "PROCESSING":
            raise ValueError("job not processing")
        _utc(generated_at_utc)
        if coverage not in {"COMPLETE", "PARTIAL", "UNMEASURED"}:
            raise ValueError("invalid coverage")
        if source_health not in {"HEALTHY", "DEGRADED", "STALE", "UNAVAILABLE", "UNMEASURED"}:
            raise ValueError("invalid source health")
        if not isinstance(snapshot_id, str) or not snapshot_id:
            raise ValueError("snapshot id required")
        if not isinstance(evidence, list) or len(evidence) > self.request["max_results"]:
            raise ValueError("unbounded result")
        selected = []
        for item in evidence:
            if not isinstance(item, dict) or set(item) != {"record_id", "kind", "published_at_utc", "available_at_utc", "summary"}:
                raise ValueError("unapproved fixture fields")
            if item["kind"] not in {"CLAIM_EVENT", "CLAIM_CORRECTION", "FORECAST_VERSION"}:
                raise ValueError("unapproved kind")
            if not isinstance(item["summary"], str) or len(item["summary"]) > 1000:
                raise ValueError("invalid summary")
            if self.request["mode"] == "HISTORICAL_AS_OF" and not historically_available(item, self.request["as_of_utc"]):
                raise ValueError("historical lookahead or missing availability")
            _utc(item["published_at_utc"])
            _utc(item["available_at_utc"])
            selected.append(dict(item))
        status = "COMPLETE" if coverage == "COMPLETE" and source_health == "HEALTHY" else "PARTIAL"
        result = {"schema_version": "kgm.research.result.v1",
                  "request_id": self.request["request_id"],
                  "consumer_id": self.request["consumer_id"],
                  "result_id": self.request["request_id"] + "-result-1",
                  "generated_at_utc": generated_at_utc,
                  "producer_snapshot_id": snapshot_id,
                  "policy_version": self.request["policy_version"],
                  "research_status": status, "coverage": coverage,
                  "source_health": source_health, "records": selected}
        self.transition(status)
        self.result = result
        return result
