"""African Union official single-article parser: fixture-only research candidate.

No enabled source registration, persistent crawl, or factual verification credit.
Only allowlisted official article URLs; timestamps must be explicit, timezone
aware for precise datetimes or declared as date-only UTC anchors.
"""
from __future__ import annotations

import hashlib
import html
import re
from datetime import datetime, timezone
from urllib.parse import urlsplit

from .research_request_v1 import validate_request, _utc

SOURCE_ID = "african-union-press"
ORIGIN_GROUP = "african-union"
ALLOWED_HOSTS = frozenset(("au.int", "www.au.int"))
MAX_BYTES = 2_000_000


def parse_official_article(raw):
    if isinstance(raw, bytes):
        raw = raw.decode("utf-8", "replace")
    if not isinstance(raw, str) or len(raw.encode("utf-8")) > MAX_BYTES:
        raise ValueError("invalid or oversized African Union response")
    if not re.search(r"<html\b", raw, re.I):
        raise ValueError("invalid African Union HTML")
    # Explicit publisher metadata only. Never infer the publication clock
    # from file names, image names, observation timestamp or article URL.
    # The AU HTML includes a carousel of other articles before its own
    # <article>. Never use the first unscoped <time> from that carousel.
    article = re.search(r'<article\b[^>]*class=["\x27][^"\x27]*node-pressrelease[^"\x27]*["\x27][^>]*>(.*?)</article>', raw, re.I | re.S)
    scoped = article.group(1) if article else ""
    match = (
        re.search(
            r'class=["\x27][^"\x27]*field--name-field-date[^"\x27]*["\x27][^>]*>[\s\S]{0,250}?'
            r'<time\b[^>]*datetime=["\x27]([^"\x27]+)["\x27]',
            scoped, re.I)
        or re.search(r'property=["\x27]article:published_time["\x27][^>]*content=["\x27]([^"\x27]+)["\x27]', raw, re.I)
        or re.search(r'"datePublished"\s*:\s*"([^"]+)"', raw, re.I)
    )
    if not match:
        raise ValueError("African Union publication timestamp missing")
    value = match.group(1)
    if re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
        # Explicit day-only source precision; NOT verified clock time.
        try:
            day = datetime.strptime(value, "%Y-%m-%d")
        except ValueError as exc:
            raise ValueError("invalid African Union publication day") from exc
        dt = day.replace(tzinfo=timezone.utc)
    else:
        try:
            dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError as exc:
            raise ValueError("invalid African Union timestamp") from exc
        if dt.tzinfo is None:
            raise ValueError("naive African Union timestamp")
    title = re.search(r'<h1\b[^>]*>(.*?)</h1\s*>', raw, re.I | re.S)
    if not title:
        raise ValueError("African Union article heading missing")
    text = re.sub(r"<script\b.*?</script>|<style\b.*?</style>", " ", raw, flags=re.I | re.S)
    text = " ".join(html.unescape(re.sub(r"<[^>]+>", " ", text)).split())
    heading = " ".join(html.unescape(re.sub(r"<[^>]+>", " ", title.group(1))).split())
    if not heading or len(text) < 60:
        raise ValueError("African Union article content missing")
    published = dt.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    return published, heading, text[:1000]


def fetch(request, *, observed_at_utc, http_get, public_url):
    validate_request(request)
    observed = _utc(observed_at_utc)
    u = urlsplit(public_url)
    if (u.scheme != "https" or u.hostname not in ALLOWED_HOSTS or
            u.username is not None or u.password is not None or u.fragment or
            not re.fullmatch(r"/en/pressreleases/\d{8}/[a-z0-9-]+", u.path)):
        raise ValueError("invalid African Union provenance")
    try:
        raw = http_get(public_url)
    except (TimeoutError, OSError):
        return [{
            "schema_version": "kgm.source.observation.v1",
            "request_id": request["request_id"], "source_id": SOURCE_ID,
            "observation_id": "african-union-transport",
            "status": "UNAVAILABLE", "observed_at_utc": observed_at_utc,
            "published_at_utc": None, "available_at_utc": None,
            "public_url": None, "summary": None,
            "error_code": "TRANSPORT_UNAVAILABLE", "origin_group": ORIGIN_GROUP,
        }]
    published, heading, body = parse_official_article(raw)
    start = _utc(request["period_start_utc"])
    end = _utc(request.get("as_of_utc", request["period_end_utc"]))
    if not start <= _utc(published) <= end:
        return []
    identity = "au-" + hashlib.sha256(public_url.encode("utf-8")).hexdigest()[:24]
    if request["mode"] == "HISTORICAL_AS_OF" and observed > _utc(request["as_of_utc"]):
        return [{
            "schema_version": "kgm.source.observation.v1",
            "request_id": request["request_id"], "source_id": SOURCE_ID,
            "observation_id": identity, "status": "INVALID",
            "observed_at_utc": observed_at_utc, "published_at_utc": None,
            "available_at_utc": None, "public_url": None, "summary": None,
            "error_code": "HISTORICAL_AVAILABILITY_UNPROVEN",
            "origin_group": None,
        }]
    return [{
        "schema_version": "kgm.source.observation.v1",
        "request_id": request["request_id"], "source_id": SOURCE_ID,
        "observation_id": identity, "status": "SUCCESS",
        "observed_at_utc": observed_at_utc, "published_at_utc": published,
        "available_at_utc": observed_at_utc, "public_url": public_url,
        "summary": (heading + ": " + body)[:1000],
        "error_code": None, "origin_group": ORIGIN_GROUP,
    }]
