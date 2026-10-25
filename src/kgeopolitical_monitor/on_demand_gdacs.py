"""GDACS RSS adapter, not enabled in production or the on-demand dispatcher.

Endpoint verified against GDACS 2025 technical guidance:
https://www.gdacs.org/xml/rss.xml
"""
from __future__ import annotations

from datetime import datetime
from email.utils import parsedate_to_datetime
from hashlib import sha256
from urllib.parse import urlsplit
import xml.etree.ElementTree as ET

from .live_sources import HttpTransport, LiveSourceItem, _clean_text, _matches_query
from .operational_monitoring import MonitoringWatch, _normalize_time


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
            if not title or not url or not _matches_query(title, summary, watch.query):
                continue
            parsed = urlsplit(url)
            if parsed.scheme != "https" or not parsed.hostname:
                continue
            metadata = {"feed": "GDACS RSS", "publisher": "GDACS"}
            pub = (entry.findtext("pubDate") or "").strip()
            if pub:
                try:
                    when = parsedate_to_datetime(pub)
                    metadata["published_at"] = _normalize_time(when).isoformat()
                except (ValueError, TypeError, OverflowError):
                    metadata["publication_date_status"] = "UNVERIFIED"
            key = entry.findtext("guid") or url
            item_id = "gdacs-" + sha256(key.encode("utf-8")).hexdigest()[:24]
            items.append(LiveSourceItem(
                item_id=item_id,
                source_id=self.source_id,
                source_name=self.source_name,
                source_class=self.source_class,
                title=title,
                summary=summary or title,
                original_url=url,
                collected_at=timestamp,
                metadata=metadata,
                reliability="official",
            ))
            if len(items) >= self.max_records:
                break
        return items
