"""Evidence independence and freshness assessment without implied verification.

This module never declares source *ownership* independence based on URL count.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from urllib.parse import urlsplit


@dataclass(frozen=True)
class EvidenceAssessment:
    source_records: int
    valid_origin_hosts: int
    source_ids: int
    origins_independence: str
    freshness: str
    newest_published_at: str | None
    dated_records: int
    stale_records: int
    undated_records: int
    future_records: int


def _parse_publication_time(value: object) -> datetime | None:
    if not isinstance(value, str):
        return None
    try:
        text = value.strip()
        if len(text) == 16 and text[8] == "T" and text[-1] == "Z":
            parsed = datetime.strptime(text, "%Y%m%dT%H%M%SZ").replace(tzinfo=timezone.utc)
        else:
            parsed = datetime.fromisoformat(text.replace("Z", "+00:00"))
        if parsed.tzinfo is None:
            return None
        return parsed.astimezone(timezone.utc)
    except (ValueError, OverflowError):
        return None


def assess_evidence(items, *, observed_at: datetime, freshness_hours: int = 48) -> EvidenceAssessment:
    """Items expose original_url, source_id, metadata. No network or writes."""
    if observed_at.tzinfo is None:
        raise ValueError("observed_at must be timezone-aware")
    if not 1 <= freshness_hours <= 720:
        raise ValueError("freshness threshold out of bounds")
    now = observed_at.astimezone(timezone.utc)
    records = tuple(items)
    hosts: set[str] = set()
    source_ids: set[str] = set()
    dated = stale = undated = future = 0
    newest = None
    for item in records:
        url = urlsplit(str(getattr(item, "original_url", "")))
        if url.scheme in ("http", "https") and url.hostname:
            hosts.add(url.hostname.lower().removeprefix("www."))
        source_ids.add(str(getattr(item, "source_id", "")))
        metadata = getattr(item, "metadata", {}) or {}
        # GDACS/Consilium may offer published_at, GDELT offers article seendate.
        published = _parse_publication_time(
            metadata.get("published_at") or metadata.get("seendate")
        ) if isinstance(metadata, dict) else None
        if published is None:
            undated += 1
            continue
        dated += 1
        newest = max(newest, published) if newest is not None else published
        if published > now + timedelta(minutes=5):
            future += 1
        elif now - published > timedelta(hours=freshness_hours):
            stale += 1
    if not records:
        freshness = "NO_EVIDENCE"
    elif future:
        freshness = "INVALID_FUTURE_TIMESTAMP"
    elif undated:
        freshness = "UNKNOWN_INCOMPLETE_DATES"
    elif stale:
        freshness = "PARTIAL_STALE" if stale < len(records) else "STALE"
    else:
        freshness = "FRESH_BY_PUBLISHED_TIMESTAMP"
    return EvidenceAssessment(
        source_records=len(records),
        valid_origin_hosts=len(hosts),
        source_ids=len(source_ids),
        origins_independence="NOT_ATTESTED_OWNERSHIP_OR_SYNDICATION",
        freshness=freshness,
        newest_published_at=newest.isoformat() if newest is not None else None,
        dated_records=dated,
        stale_records=stale,
        undated_records=undated,
        future_records=future,
    )
