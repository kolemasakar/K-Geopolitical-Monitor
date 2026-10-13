"""Bounded synthetic request-driven research contract. No provider execution."""
from __future__ import annotations
from datetime import datetime, timezone
import re

REQUEST_VERSION = "kgm.research.request.v1"
MODES = {"CURRENT", "HISTORICAL_AS_OF"}
STATUSES = {"RECEIVED", "ACCEPTED", "PROCESSING", "COMPLETE", "PARTIAL", "FAILED", "EXPIRED"}
_ID = re.compile(r"^[A-Za-z0-9_-]{1,128}$")
_SYMBOL = re.compile(r"^[A-Za-z0-9._:-]{1,32}$")


def _utc(value):
    if not isinstance(value, str) or not value.endswith("Z"):
        raise ValueError("UTC Z timestamp required")
    try:
        parsed = datetime.fromisoformat(value[:-1] + "+00:00")
    except ValueError as exc:
        raise ValueError("invalid UTC timestamp") from exc
    if parsed.utcoffset().total_seconds() != 0:
        raise ValueError("non-UTC timestamp")
    return parsed


def validate_request(req):
    allowed = {"schema_version", "request_id", "consumer_id", "requested_at_utc",
               "mode", "symbols", "period_start_utc", "period_end_utc",
               "as_of_utc", "topic_filters", "max_results", "policy_version"}
    required = allowed - {"as_of_utc", "topic_filters"}
    if not isinstance(req, dict) or not required <= req.keys() or req.keys() - allowed:
        raise ValueError("missing or unapproved request fields")
    if req["schema_version"] != REQUEST_VERSION:
        raise ValueError("unsupported request version")
    for field in ("request_id", "consumer_id", "policy_version"):
        if not isinstance(req[field], str) or not _ID.fullmatch(req[field]):
            raise ValueError("invalid " + field)
    _utc(req["requested_at_utc"])
    start, end = _utc(req["period_start_utc"]), _utc(req["period_end_utc"])
    if start > end or (end - start).days > 366:
        raise ValueError("invalid or unbounded query window")
    if req["mode"] not in MODES:
        raise ValueError("unsupported mode")
    symbols = req["symbols"]
    if not isinstance(symbols, list) or not 1 <= len(symbols) <= 20 or any(
        not isinstance(item, str) or not _SYMBOL.fullmatch(item) for item in symbols
    ) or len(set(symbols)) != len(symbols):
        raise ValueError("invalid symbol scope")
    filters = req.get("topic_filters", [])
    if not isinstance(filters, list) or len(filters) > 10 or any(
        not isinstance(item, str) or not _ID.fullmatch(item) for item in filters
    ):
        raise ValueError("unbounded topic filters")
    if type(req["max_results"]) is not int or not 1 <= req["max_results"] <= 100:
        raise ValueError("invalid result limit")
    if req["mode"] == "HISTORICAL_AS_OF":
        if "as_of_utc" not in req:
            raise ValueError("historical as-of timestamp required")
        as_of = _utc(req["as_of_utc"])
        if end > as_of or _utc(req["requested_at_utc"]) < as_of:
            raise ValueError("historical cutoff must include requested period")
    elif "as_of_utc" in req:
        raise ValueError("current request cannot masquerade as historical")
    return req


def historically_available(evidence, cutoff_utc):
    """Require published AND separately recorded available/ingested by cutoff."""
    cutoff = _utc(cutoff_utc)
    if not isinstance(evidence, dict):
        return False
    try:
        publication = _utc(evidence["published_at_utc"])
        available = _utc(evidence["available_at_utc"])
    except (KeyError, ValueError, TypeError):
        return False
    return publication <= cutoff and available <= cutoff
