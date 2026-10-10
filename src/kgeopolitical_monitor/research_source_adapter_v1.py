"""Typed source-adapter contract for owner-pilot research execution.

Pure validation/normalization only. No network or provider calls.
"""
from __future__ import annotations
import hashlib
from urllib.parse import urlsplit, urlunsplit
from .research_request_v1 import validate_request, historically_available, _utc, _ID
from .research_generic_identity_v1 import (
    validate_generic_event_descriptor, generic_event_identity,
    validate_generic_claim_descriptor, generic_claim_signature)

SOURCE_STATUSES={"SUCCESS","PARTIAL","UNAVAILABLE","INVALID"}
OBSERVATION_VERSION="kgm.source.observation.v1"
PARTIAL_REASONS={"SOURCE_TRUNCATED","UPSTREAM_PARTIAL","RATE_LIMITED_PARTIAL",
                 "FILTER_LIMIT","PARSE_PARTIAL","COVERAGE_GAP","OTHER"}

def _validated_https_url(value):
    if not isinstance(value,str) or not 1<=len(value)<=2048:
        raise ValueError("invalid source provenance")
    parsed=urlsplit(value)
    if (parsed.scheme!="https" or not parsed.hostname or
        parsed.username is not None or parsed.password is not None or parsed.fragment):
        raise ValueError("invalid source provenance")
    try:
        _=parsed.port
    except ValueError as exc:
        raise ValueError("invalid source provenance") from exc
    return parsed

def validate_source_observation(request,observation):
    validate_request(request)
    base_fields={"schema_version","request_id","source_id","observation_id","status",
                 "observed_at_utc","published_at_utc","available_at_utc","public_url",
                 "summary","error_code"}
    optional_fields={"event_identity","claim_signature","origin_group","event_parameters",
                     "event_descriptor","claim_descriptor","partial_reason"}
    if (not isinstance(observation,dict) or not base_fields<=set(observation) or
        set(observation)-base_fields-optional_fields):
        raise ValueError("unapproved source observation fields")

    identity=observation.get("event_identity")
    signature=observation.get("claim_signature")
    if identity is not None and (not isinstance(identity,str) or not _ID.fullmatch(identity)):
        raise ValueError("invalid event identity")
    if signature is not None and (not isinstance(signature,str) or not _ID.fullmatch(signature)):
        raise ValueError("invalid claim signature")
    if signature is not None and identity is None:
        raise ValueError("claim signature requires event identity")

    event_descriptor=observation.get("event_descriptor")
    claim_descriptor=observation.get("claim_descriptor")
    if event_descriptor is not None:
        validate_generic_event_descriptor(event_descriptor)
        if identity!=generic_event_identity(event_descriptor):
            raise ValueError("generic event identity mismatch")
    if claim_descriptor is not None:
        validate_generic_claim_descriptor(claim_descriptor)
        if signature!=generic_claim_signature(claim_descriptor):
            raise ValueError("generic claim signature mismatch")
    if claim_descriptor is not None and event_descriptor is None:
        raise ValueError("generic claim descriptor requires event descriptor")

    origin_group=observation.get("origin_group")
    if origin_group is not None and (not isinstance(origin_group,str) or not _ID.fullmatch(origin_group)):
        raise ValueError("invalid origin group")

    params=observation.get("event_parameters")
    if params is not None:
        if not isinstance(params,dict) or set(params)!={"kind","origin_utc","latitude","longitude","magnitude"}:
            raise ValueError("invalid event parameters")
        if params["kind"]!="EARTHQUAKE":
            raise ValueError("unsupported event parameter kind")
        _utc(params["origin_utc"])
        for field in ("latitude","longitude","magnitude"):
            if not isinstance(params[field],(int,float)) or isinstance(params[field],bool):
                raise ValueError("invalid event parameter value")
        if not -90<=params["latitude"]<=90 or not -180<=params["longitude"]<=180 or not 0<=params["magnitude"]<=10:
            raise ValueError("event parameter out of range")

    if observation["schema_version"]!=OBSERVATION_VERSION or observation["request_id"]!=request["request_id"]:
        raise ValueError("source observation correlation mismatch")
    for field in ("source_id","observation_id"):
        if not isinstance(observation[field],str) or not _ID.fullmatch(observation[field]):
            raise ValueError("invalid source identity")
    if observation["status"] not in SOURCE_STATUSES:
        raise ValueError("invalid source status")

    partial_reason=observation.get("partial_reason")
    if observation["status"]=="PARTIAL":
        if partial_reason not in PARTIAL_REASONS:
            raise ValueError("typed partial reason required")
    elif partial_reason is not None:
        raise ValueError("partial reason on non-partial observation")

    _utc(observation["observed_at_utc"])
    if observation["status"] in {"SUCCESS","PARTIAL"}:
        _validated_https_url(observation["public_url"])
        if not isinstance(observation["summary"],str) or not 1<=len(observation["summary"])<=1000:
            raise ValueError("invalid observation summary")
        if observation["error_code"] is not None:
            raise ValueError("successful observation cannot carry error")
        _utc(observation["published_at_utc"]); _utc(observation["available_at_utc"])
        evidence={k:observation[k] for k in ("source_id","public_url","published_at_utc","available_at_utc")}
        if request["mode"]=="HISTORICAL_AS_OF" and not historically_available(evidence,request["as_of_utc"]):
            raise ValueError("historical source lookahead")
    else:
        if any(observation[x] is not None for x in ("published_at_utc","available_at_utc","public_url","summary")):
            raise ValueError("failed source cannot masquerade as evidence")
        if not isinstance(observation["error_code"],str) or not _ID.fullmatch(observation["error_code"]):
            raise ValueError("explicit source error required")
    return observation

def evidence_fingerprint(observation):
    if not isinstance(observation,dict) or observation.get("status") not in {"SUCCESS","PARTIAL"}:
        raise ValueError("evidence-bearing observation required")
    parsed=_validated_https_url(observation.get("public_url"))
    host=parsed.hostname.lower()
    port=parsed.port
    netloc=host if port in (None,443) else host+":"+str(port)
    normalized=urlunsplit(("https",netloc,parsed.path or "/",parsed.query,""))
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()

def normalize_observations(request,observations):
    validate_request(request)
    if not isinstance(observations,list) or not 1<=len(observations)<=100:
        raise ValueError("invalid observation batch")
    seen=set(); evidence_seen=set(); normalized=[]
    for item in observations:
        validate_source_observation(request,item)
        key=(item["source_id"],item["observation_id"])
        if key in seen:
            raise ValueError("duplicate source observation")
        seen.add(key)
        if item["status"] in {"SUCCESS","PARTIAL"}:
            fp=evidence_fingerprint(item)
            if fp in evidence_seen:
                raise ValueError("duplicate evidence fingerprint")
            evidence_seen.add(fp)
        normalized.append(dict(item))
    normalized.sort(key=lambda x:(x["source_id"],x["observation_id"]))
    return normalized

def observation_digest(observation):
    from .research_storage_v1 import canonical_bytes
    return hashlib.sha256(canonical_bytes(observation)).hexdigest()
