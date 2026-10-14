"""Pure v1 validation for synthetic KGM cross-project exchange batches.

NO database reads, network calls, production artifacts, or status promotion.
Consumers validate an allowlisted envelope before optional per-consumer mapping.
"""
from __future__ import annotations

from datetime import datetime, timezone
from hashlib import sha256
import json
from typing import Any, Mapping

SCHEMA_VERSION = "kgm.exchange.v1"
KINDS = frozenset({"CLAIM_EVENT", "CLAIM_REVISION", "CLAIM_CORRECTION", "FORECAST_VERSION", "SOURCE_HEALTH"})
CHANGES = frozenset({"NEW", "UPDATE", "CORRECTION", "HEARTBEAT"})
VERIFICATION = frozenset({"DETECTED", "PARTLY_VERIFIED", "VERIFIED", "DISPUTED", "UNVERIFIABLE"})
CONFIDENCE_LEVELS = frozenset({"UNKNOWN", "LOW", "MEDIUM", "HIGH"})
CONFIDENCE_DIMENSIONS = frozenset({
    "evidence_sufficiency", "provenance_independence", "authority_proximity",
    "contradiction_resolution", "temporal_freshness", "extraction_certainty",
    "translation_certainty", "claim_specific_certainty",
})
CONTRADICTION_STATES = frozenset({"DETECTED", "UNRESOLVED", "EVOLVING", "RESOLVED"})
SOURCE_STATES = frozenset({"UNMEASURED", "HEALTHY", "DEGRADED", "STALE", "UNAVAILABLE"})
MAX_RECORDS = 100
MAX_BYTES = 1024 * 1024
# Prototype policy: reject unknown keys rather than pass through unreviewed data.
BATCH_FIELDS = frozenset({"schema_version","batch_id","generated_at_utc","producer_snapshot_id","producer_code_sha","minimum_available_cursor","high_watermark_cursor","heartbeat","policy_version","records"})
RECORD_FIELDS = frozenset({"record_id","kind","change_type","entity_id","entity_version_id","recorded_at_utc","published_at_utc","ingested_at_utc","exported_at_utc","supersedes_record_id","retraction_state","language","content","provenance","verification","contradiction","forecast","source_health"})
SAFE_CONTENT_FIELDS = frozenset({"summary","event_type","region_tags","topic_tags"})
SAFE_PROVENANCE_FIELDS = frozenset({"publisher","underlying_origin","origin_resolution","public_evidence_refs"})
SAFE_VERIFICATION_FIELDS = frozenset({"canonical_verification_state","compatibility_state","policy_version","confidence_dimensions"})
SAFE_CONTRADICTION_FIELDS = frozenset({"lifecycle_state","dimensions","public_evidence_refs"})
SAFE_FORECAST_FIELDS = frozenset({"scenario_id","forecast_id","forecast_version_id","assumptions","public_input_refs","raw_probability","calibrated_probability","scenario_confidence"})
SAFE_SOURCE_FIELDS = frozenset({"source_id","operational_state","measurement_freshness","content_freshness","last_attempt_at_utc","latest_content_at_utc"})

def _allowlisted(value: Any, name: str, fields: frozenset[str]) -> Mapping[str, Any]:
    obj = _mapping(value, name)
    if set(obj) - fields:
        raise ValueError(f"{name}: unapproved fields")
    return obj



def _utc(value: Any, name: str) -> datetime:
    if not isinstance(value, str) or not value:
        raise ValueError(f"{name}: UTC timestamp required")
    try:
        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError(f"{name}: invalid timestamp") from exc
    if dt.utcoffset() is None or dt.utcoffset().total_seconds() != 0:
        raise ValueError(f"{name}: must use UTC")
    return dt.astimezone(timezone.utc)


def _mapping(value: Any, name: str) -> Mapping[str, Any]:
    if not isinstance(value, dict):
        raise ValueError(f"{name}: object required")
    return value


def _id(value: Any, name: str) -> str:
    if not isinstance(value, str) or not 1 <= len(value) <= 128 or any(c.isspace() for c in value):
        raise ValueError(f"{name}: invalid identifier")
    return value


def validate_record(record: Mapping[str, Any], exported_at: datetime) -> None:
    _allowlisted(record, "record", RECORD_FIELDS)
    for field, allowed in (("content",SAFE_CONTENT_FIELDS),("provenance",SAFE_PROVENANCE_FIELDS),("verification",SAFE_VERIFICATION_FIELDS),("contradiction",SAFE_CONTRADICTION_FIELDS),("forecast",SAFE_FORECAST_FIELDS),("source_health",SAFE_SOURCE_FIELDS)):
        if record.get(field) is not None:
            _allowlisted(record[field], field, allowed)
    kind = record.get("kind")
    change = record.get("change_type")
    if kind not in KINDS or change not in CHANGES:
        raise ValueError("invalid kind or change")
    for key in ("record_id", "entity_id", "entity_version_id"):
        _id(record.get(key), key)
    created = _utc(record.get("recorded_at_utc"), "recorded_at_utc")
    record_export = _utc(record.get("exported_at_utc"), "exported_at_utc")
    if created > record_export or record_export > exported_at:
        raise ValueError("record timestamps inconsistent")
    published = record.get("published_at_utc")
    ingested = record.get("ingested_at_utc")
    if published is not None:
        if _utc(published, "published_at_utc") > record_export:
            raise ValueError("published after export")
    if ingested is not None:
        if _utc(ingested, "ingested_at_utc") > record_export:
            raise ValueError("ingested after export")
    if published is not None and ingested is not None:
        if _utc(published, "published_at_utc") > _utc(ingested, "ingested_at_utc"):
            raise ValueError("ingested before published")
    if kind == "CLAIM_CORRECTION":
        _id(record.get("supersedes_record_id"), "supersedes_record_id")
        if change != "CORRECTION":
            raise ValueError("correction must be explicitly typed")
    if kind == "FORECAST_VERSION" and change == "CORRECTION":
        raise ValueError("forecast update must not impersonate claim correction")
    if kind == "SOURCE_HEALTH":
        state = _mapping(record.get("source_health"), "source_health").get("operational_state")
        if state not in SOURCE_STATES:
            raise ValueError("source health must preserve canonical state")
    if kind in {"CLAIM_EVENT", "CLAIM_REVISION", "CLAIM_CORRECTION"}:
        verification = _mapping(record.get("verification"), "verification")
        state = verification.get("canonical_verification_state")
        if state is not None and state not in VERIFICATION:
            raise ValueError("invalid canonical verification state")
        values = _mapping(verification.get("confidence_dimensions", {}), "confidence_dimensions")
        if set(values) - CONFIDENCE_DIMENSIONS:
            raise ValueError("unknown confidence dimension")
        if any(value not in CONFIDENCE_LEVELS for value in values.values()):
            raise ValueError("canonical confidence must remain dimensional")
        contradiction = record.get("contradiction")
        if contradiction is not None:
            state2 = _mapping(contradiction, "contradiction").get("lifecycle_state")
            if state2 is not None and state2 not in CONTRADICTION_STATES:
                raise ValueError("invalid contradiction lifecycle")
            if state2 in {"DETECTED", "UNRESOLVED", "EVOLVING"} and state == "VERIFIED":
                raise ValueError("unresolved contradiction cannot be marked verified")
    if kind == "FORECAST_VERSION":
        forecast = _mapping(record.get("forecast"), "forecast")
        for field in ("raw_probability", "calibrated_probability"):
            value = forecast.get(field)
            if value is not None and (type(value) not in (int, float) or not 0 <= value <= 1):
                raise ValueError(f"{field}: invalid")
        if "scenario_confidence" in forecast and type(forecast["scenario_confidence"]) not in (int, float, str, type(None)):
            raise ValueError("scenario confidence must not be coerced")
        if "canonical_verification_state" in forecast:
            raise ValueError("forecast must never have factual verification")
    if any(k in record for k in ("confidence", "severity", "trading_action", "private_database_path", "raw_full_text")):
        raise ValueError("unsupported consumer policy or sensitive field")


def validate_batch(batch: Mapping[str, Any]) -> str:
    obj = _allowlisted(batch, "batch", BATCH_FIELDS)
    if obj.get("schema_version") != SCHEMA_VERSION:
        raise ValueError("unsupported schema_version")
    for key in ("batch_id", "producer_snapshot_id", "producer_code_sha", "policy_version"):
        _id(obj.get(key), key)
    produced = _utc(obj.get("generated_at_utc"), "generated_at_utc")
    heartbeat = _mapping(obj.get("heartbeat"), "heartbeat")
    _allowlisted(heartbeat, "heartbeat", frozenset({"state", "observed_at_utc"}))
    if heartbeat.get("state") not in {"HEALTHY", "DEGRADED", "UNKNOWN"}:
        raise ValueError("heartbeat.state must be explicit")
    _utc(heartbeat.get("observed_at_utc"), "heartbeat.observed_at_utc")
    records = obj.get("records")
    if not isinstance(records, list) or len(records) > MAX_RECORDS:
        raise ValueError("records must be bounded array")
    cursor = obj.get("high_watermark_cursor")
    _id(cursor, "high_watermark_cursor")
    minimum = obj.get("minimum_available_cursor")
    _id(minimum, "minimum_available_cursor")
    for record in records:
        validate_record(_mapping(record, "record"), produced)
    encoded = json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False).encode("utf-8")
    if len(encoded) > MAX_BYTES:
        raise ValueError("batch exceeds 1 MiB")
    return sha256(encoded).hexdigest()
