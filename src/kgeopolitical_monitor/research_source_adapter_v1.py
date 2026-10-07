"""Typed source-adapter contract for owner-pilot research execution.

Pure validation/normalization only. No network or provider calls.
"""
from __future__ import annotations
import hashlib
from .research_request_v1 import validate_request, historically_available, _utc, _ID

SOURCE_STATUSES = {"SUCCESS", "PARTIAL", "UNAVAILABLE", "INVALID"}
OBSERVATION_VERSION = "kgm.source.observation.v1"

def validate_source_observation(request, observation):
    validate_request(request)
    fields = {"schema_version","request_id","source_id","observation_id","status",
              "observed_at_utc","published_at_utc","available_at_utc","public_url",
              "summary","error_code"}
    if not isinstance(observation, dict) or set(observation) != fields:
        raise ValueError("unapproved source observation fields")
    if observation["schema_version"] != OBSERVATION_VERSION or observation["request_id"] != request["request_id"]:
        raise ValueError("source observation correlation mismatch")
    for field in ("source_id","observation_id"):
        if not isinstance(observation[field], str) or not _ID.fullmatch(observation[field]):
            raise ValueError("invalid source identity")
    if observation["status"] not in SOURCE_STATUSES:
        raise ValueError("invalid source status")
    _utc(observation["observed_at_utc"])
    if observation["status"] in {"SUCCESS","PARTIAL"}:
        if not isinstance(observation["public_url"], str) or not observation["public_url"].startswith("https://"):
            raise ValueError("invalid source provenance")
        if not isinstance(observation["summary"], str) or not 1 <= len(observation["summary"]) <= 1000:
            raise ValueError("invalid observation summary")
        if observation["error_code"] is not None:
            raise ValueError("successful observation cannot carry error")
        _utc(observation["published_at_utc"]); _utc(observation["available_at_utc"])
        evidence = {k: observation[k] for k in ("source_id","public_url","published_at_utc","available_at_utc")}
        if request["mode"] == "HISTORICAL_AS_OF" and not historically_available(evidence, request["as_of_utc"]):
            raise ValueError("historical source lookahead")
    else:
        if any(observation[x] is not None for x in ("published_at_utc","available_at_utc","public_url","summary")):
            raise ValueError("failed source cannot masquerade as evidence")
        if not isinstance(observation["error_code"], str) or not _ID.fullmatch(observation["error_code"]):
            raise ValueError("explicit source error required")
    return observation

def normalize_observations(request, observations):
    validate_request(request)
    if not isinstance(observations, list) or not 1 <= len(observations) <= 100:
        raise ValueError("invalid observation batch")
    seen = set(); normalized = []
    for item in observations:
        validate_source_observation(request, item)
        key = (item["source_id"], item["observation_id"])
        if key in seen:
            raise ValueError("duplicate source observation")
        seen.add(key)
        normalized.append(dict(item))
    normalized.sort(key=lambda x: (x["source_id"], x["observation_id"]))
    return normalized

def observation_digest(observation):
    from .research_storage_v1 import canonical_bytes
    return hashlib.sha256(canonical_bytes(observation)).hexdigest()
