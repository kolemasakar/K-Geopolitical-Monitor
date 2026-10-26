"""GDACS RSS adapter, not enabled in production or the on-demand dispatcher.

Endpoint verified against GDACS 2025 technical guidance:
https://www.gdacs.org/xml/rss.xml
"""
from __future__ import annotations

from datetime import datetime
from email.utils import parsedate_to_datetime
from hashlib import sha256
from urllib.parse import urlsplit, urlunsplit
import xml.etree.ElementTree as ET

from .live_sources import HttpTransport, LiveSourceItem, _clean_text, _matches_query
from .operational_monitoring import MonitoringWatch, _normalize_time


def gdacs_safe_article_url(value: str) -> tuple[str | None, str]:
    """Normalize only exact GDACS-owned legacy HTTP links, without fetching them.

    No userinfo, fragments, custom ports, control chars, encoded authority, or
    unrelated domains. A normalized URL is NOT dereferenced by this adapter.
    """
    url = (value or "").strip()
    if not url or len(url) > 2048 or any(ord(c) < 32 or ord(c) == 127 for c in url):
        return None, "UNSAFE_OR_NON_HTTPS_LINK"
    if "\\\\" in url or "\\" in url:
        return None, "UNSAFE_OR_NON_HTTPS_LINK"
    try:
        parts = urlsplit(url)
        if (parts.username is not None or parts.password is not None or parts.fragment
                or parts.hostname not in {"www.gdacs.org", "gdacs.org"}
                or parts.scheme not in {"http", "https"}
                or parts.port is not None
                or not parts.path.startswith("/") or parts.path.startswith("//")):
            return None, "UNSAFE_OR_NON_HTTPS_LINK"
    except (TypeError, ValueError):
        return None, "UNSAFE_OR_NON_HTTPS_LINK"
    host = "www.gdacs.org"
    safe_url = urlunsplit(("https", host, parts.path, parts.query, ""))
    return safe_url, ("GDACS_OWNED_LEGACY_HTTP" if parts.scheme == "http"
                      else "GDACS_OWNED_HTTPS")


def gdacs_admission_reason(entry: ET.Element, query: str) -> str:
    """Classify an RSS entry without exposing content or weakening HTTPS-only admission.

    The same decision function is shared by admission and the P5 probe counters,
    avoiding a mismatch between independently coded query predicates.
    """
    title = _clean_text(entry.findtext("title") or "")
    summary = _clean_text(entry.findtext("description") or "")
    if not _matches_query(title, summary, query):
        return "TOPIC_NO_MATCH"
    if not title:
        return "MISSING_TITLE"
    url = (entry.findtext("link") or "").strip()
    if not url:
        return "MISSING_LINK"
    safe_url, category = gdacs_safe_article_url(url)
    if safe_url is None:
        return "UNSAFE_OR_NON_HTTPS_LINK"
    return ("TRUSTED_GDACS_HTTP_NORMALIZED"
            if category == "GDACS_OWNED_LEGACY_HTTP" else "ADMITTED")


class GdacsRssAdapter:
    source_id = "gdacs-rss"
    source_name = "GDACS / Global Disaster Alert and Coordination System"
    source_class = "Structured data"
    feed_url = "https://www.gdacs.org/xml/rss.xml"

    def __init__(self, transport: HttpTransport, *, max_records: int = 25):
        if not 1 <= max_records <= 50:
            raise ValueError("GDACS max_records must be 1..50")
        self.transport = transport
        self.max_records = max_records

    def fetch(self, watch: MonitoringWatch, collected_at: datetime) -> list[LiveSourceItem]:
        timestamp = _normalize_time(collected_at)
        response = self.transport.get(
            self.feed_url,
            headers={"Accept": "application/rss+xml, application/xml, text/xml",
                     "User-Agent": "K-Geopolitical-Monitor on-demand pilot/1.0"},
        )
        try:
            root = ET.fromstring(response.body)
        except ET.ParseError as exc:
            raise RuntimeError("GDACS RSS XML invalid") from exc
        if root.tag != "rss":
            raise RuntimeError("GDACS RSS missing rss root")
        items = []
        for entry in root.findall("./channel/item"):
            title = _clean_text(entry.findtext("title") or "")
            summary = _clean_text(entry.findtext("description") or "")
            url = (entry.findtext("link") or "").strip()
            decision = gdacs_admission_reason(entry, watch.query)
            if decision not in {"ADMITTED", "TRUSTED_GDACS_HTTP_NORMALIZED"}:
                continue
            safe_url, _ = gdacs_safe_article_url(url)
            if safe_url is None:
                continue
            metadata = {"feed": "GDACS RSS", "publisher": "GDACS",
                        "article_link_normalization": decision}
            pub = (entry.findtext("pubDate") or "").strip()
            if pub:
                try:
                    when = parsedate_to_datetime(pub)
                    metadata["published_at"] = _normalize_time(when).isoformat()
                except (ValueError, TypeError, OverflowError):
                    metadata["publication_date_status"] = "UNVERIFIED"
            key = entry.findtext("guid") or safe_url
            item_id = "gdacs-" + sha256(key.encode("utf-8")).hexdigest()[:24]
            items.append(LiveSourceItem(
                item_id=item_id,
                source_id=self.source_id,
                source_name=self.source_name,
                source_class=self.source_class,
                title=title,
                summary=summary or title,
                original_url=safe_url,
                collected_at=timestamp,
                metadata=metadata,
                reliability="official",
            ))
            if len(items) >= self.max_records:
                break
        return items
