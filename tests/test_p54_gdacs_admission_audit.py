"""GDACS P5.4 fail-closed admission auditing; fixture-only tests."""
from types import SimpleNamespace
from datetime import datetime, timezone
import xml.etree.ElementTree as ET

from kgeopolitical_monitor.on_demand_gdacs import (
    GdacsRssAdapter, gdacs_admission_reason,
)
from kgeopolitical_monitor.p5_public_source_probe import _ConsiliumMetadataTransport


def item(title, link, description=""):
    e=ET.Element("item")
    if title is not None:
        ET.SubElement(e,"title").text=title
    if link is not None:
        ET.SubElement(e,"link").text=link
    ET.SubElement(e,"description").text=description
    return e


def test_gdacs_reason_predicate_distinguishes_drops():
    assert gdacs_admission_reason(item("Mexico quake", "https://gdacs.org/report"), "Ukraine")=="TOPIC_NO_MATCH"
    assert gdacs_admission_reason(item(None, "https://gdacs.org/report", "Ukraine alert"), "Ukraine")=="MISSING_TITLE"
    assert gdacs_admission_reason(item("Ukraine quake", None), "Ukraine")=="MISSING_LINK"
    assert gdacs_admission_reason(item("Ukraine quake", "http://www.gdacs.org/report"), "Ukraine")=="UNSAFE_OR_NON_HTTPS_LINK"
    assert gdacs_admission_reason(item("Ukraine quake", "https://user@www.gdacs.org/report"), "Ukraine")=="UNSAFE_OR_NON_HTTPS_LINK"
    assert gdacs_admission_reason(item("Ukraine quake", "https://www.gdacs.org/report#x"), "Ukraine")=="UNSAFE_OR_NON_HTTPS_LINK"
    assert gdacs_admission_reason(item("Ukraine quake", "https://www.gdacs.org/report"), "Ukraine")=="ADMITTED"


class Fake:
    def __init__(self, body):
        self.body=body
    def get(self, url, *, headers=None):
        return SimpleNamespace(body=self.body, content_type="application/xml")


def fixture():
    root=ET.Element("rss")
    ch=ET.SubElement(root,"channel")
    ch.extend([
        item("Ukraine quake", "http://www.gdacs.org/old"),
        item("Ukraine flood", "https://www.gdacs.org/good"),
        item(None, "https://www.gdacs.org/missing", "Ukraine disaster"),
        item("Ukraine report", None),
        item("Mexico event", "https://www.gdacs.org/other"),
    ])
    return ET.tostring(root)


def test_counter_and_adapter_use_same_admission_logic():
    payload=fixture()
    proxy=_ConsiliumMetadataTransport(Fake(payload), "Ukraine")
    proxy.get(GdacsRssAdapter.feed_url)
    assert proxy.gdacs_total_entries == 5
    assert proxy.gdacs_matching_entries == 4
    assert proxy.gdacs_admission_reasons == {
        "ADMITTED": 1,
        "MISSING_TITLE": 1,
        "MISSING_LINK": 1,
        "UNSAFE_OR_NON_HTTPS_LINK": 1,
        "TOPIC_NO_MATCH": 1,
    }
    adapter=GdacsRssAdapter(Fake(payload),max_records=10)
    watch=SimpleNamespace(query="Ukraine")
    records=adapter.fetch(watch,datetime(2026,10,26,tzinfo=timezone.utc))
    assert len(records)==proxy.gdacs_admission_reasons["ADMITTED"]
    assert records[0].original_url=="https://www.gdacs.org/good"


def test_malformed_gdacs_xml_does_not_claim_admission():
    p=_ConsiliumMetadataTransport(Fake(b"oops"),"Ukraine")
    p.get(GdacsRssAdapter.feed_url)
    assert p.gdacs_total_entries is None
    assert p.gdacs_matching_entries is None
    assert p.gdacs_admission_reasons is None


def test_gdacs_reason_does_not_contain_raw_input():
    e=item("Ukraine secret-key", "http://internal.private:123/private?q=secret")
    assert gdacs_admission_reason(e,"Ukraine")=="UNSAFE_OR_NON_HTTPS_LINK"
