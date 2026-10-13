"""GCC Secretariat single-article owner-pilot source: research only.

Does not activate a source or imply independent factual corroboration.
Date-only publisher metadata is anchored at UTC midnight solely for a stable
date representation; it is never evidence of an exact publication hour.
"""
from __future__ import annotations

import hashlib
import html
import re
from datetime import datetime, timezone
from urllib.parse import urlsplit

from .research_request_v1 import validate_request, _utc

SOURCE_ID = "gcc-secretariat-news"
ORIGIN_GROUP = "gcc-secretariat"
HOSTS = frozenset(("gcc-sg.org", "www.gcc-sg.org"))
MAX_BYTES = 2_000_000
PATH_PATTERN = re.compile(
    r"/en/MediaCenter/News/Pages/news-(\d{4})-(\d{2})-(\d{2})-\d+\.aspx"
)


def _plain(raw):
    raw = re.sub(r"<script\b.*?</script>|<style\b.*?</style>", " ", raw, flags=re.I | re.S)
    return " ".join(html.unescape(re.sub(r"<[^>]+>", " ", raw)).split())


def parse_article(raw):
    if isinstance(raw, bytes):
        raw = raw.decode("utf-8", "replace")
    if not isinstance(raw, str) or len(raw.encode("utf-8")) > MAX_BYTES:
        raise ValueError("invalid GCC response type or size")
    if not re.search(r"<html\b", raw, re.I):
        raise ValueError("invalid GCC article HTML")
    match = re.search(
        r'<span\b[^>]*class=["\x27]article-date["\x27][^>]*>\s*(\d{1,2}/\d{1,2}/\d{4})\s*</span>',
        raw, re.I,
    )
    if not match:
        raise ValueError("GCC article publication date missing")
    try:
        dt = datetime.strptime(match.group(1), "%m/%d/%Y")
    except ValueError as exc:
        raise ValueError("invalid GCC publication date") from exc
    title = re.search(
        r'<h2\b[^>]*class=["\x27]article-title["\x27][^>]*>(.*?)</h2>',
        raw, re.I | re.S,
    )
    body = re.search(
        r'<div\b[^>]*class=["\x27]article-body["\x27][^>]*>(.*?)'
        r'(?=<div\b[^>]*class=["\x27](?:share|related|article-footer)|</main>|</body>)',
        raw, re.I | re.S,
    )
    if not title or not body:
        raise ValueError("GCC article title/body missing")
    heading, article = _plain(title.group(1)), _plain(body.group(1))
    if len(heading) < 12 or len(article) < 60:
        raise ValueError("GCC article content too short")
    # Midnight is a date anchor, not a verified publication time.
    return dt.replace(tzinfo=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"), heading, article


def fetch(request, *, observed_at_utc, http_get, public_url):
    validate_request(request)
    observed = _utc(observed_at_utc)
    u = urlsplit(public_url)
    if (u.scheme != "https" or u.hostname not in HOSTS or
            u.username is not None or u.password is not None or
            u.fragment or u.query):
        raise ValueError("invalid GCC source provenance")
    path = PATH_PATTERN.fullmatch(u.path)
    if not path:
        raise ValueError("invalid GCC article path")
    try:
        raw = http_get(public_url)
    except (TimeoutError, OSError):
        return [{
            "schema_version": "kgm.source.observation.v1",
            "request_id": request["request_id"], "source_id": SOURCE_ID,
            "observation_id": "gcc-transport", "status": "UNAVAILABLE",
            "observed_at_utc": observed_at_utc, "published_at_utc": None,
            "available_at_utc": None, "public_url": None, "summary": None,
            "error_code": "TRANSPORT_UNAVAILABLE", "origin_group": ORIGIN_GROUP,
        }]
    published, title, body = parse_article(raw)
    expected_day = "-".join(path.groups()[:3])
    if published[:10] != expected_day:
        raise ValueError("GCC publisher date conflicts with article URL")
    if not (_utc(request["period_start_utc"]) <= _utc(published) <=
            _utc(request.get("as_of_utc", request["period_end_utc"]))):
        return []
    oid = "gcc-" + hashlib.sha256(public_url.encode("utf-8")).hexdigest()[:24]
    if request["mode"] == "HISTORICAL_AS_OF" and observed > _utc(request["as_of_utc"]):
        return [{
            "schema_version": "kgm.source.observation.v1",
            "request_id": request["request_id"], "source_id": SOURCE_ID,
            "observation_id": oid, "status": "INVALID",
            "observed_at_utc": observed_at_utc, "published_at_utc": None,
            "available_at_utc": None, "public_url": None, "summary": None,
            "error_code": "HISTORICAL_AVAILABILITY_UNPROVEN", "origin_group": None,
        }]
    return [{
        "schema_version": "kgm.source.observation.v1",
        "request_id": request["request_id"], "source_id": SOURCE_ID,
        "observation_id": oid, "status": "SUCCESS",
        "observed_at_utc": observed_at_utc, "published_at_utc": published,
        "available_at_utc": observed_at_utc, "public_url": public_url,
        "summary": (title + ": " + body)[:1000], "error_code": None,
        "origin_group": ORIGIN_GROUP,
    }]
