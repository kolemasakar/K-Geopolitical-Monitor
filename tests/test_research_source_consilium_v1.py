import pytest
from kgeopolitical_monitor.research_source_consilium_v1 import fetch, SOURCE_ID
from kgeopolitical_monitor.research_source_adapter_v1 import normalize_observations
from test_research_request_v1 import sample

XML="""<?xml version="1.0"?>
<rss><channel>
<item>
<title>EU statement on Ukraine</title>
<description>European Council statement concerning Ukraine and security.</description>
<link>https://www.consilium.europa.eu/en/press/press-releases/2026/09/01/ukraine/</link>
<pubDate>Wed, 01 Sep 2026 11:00:00 +0000</pubDate>
</item>
<item>
<title>Other topic</title>
<description>Unrelated material.</description>
<link>https://www.consilium.europa.eu/en/press/press-releases/2026/09/01/other/</link>
<pubDate>Wed, 01 Sep 2026 10:00:00 +0000</pubDate>
</item>
</channel></rss>"""

def current():
    r=sample(); r["mode"]="CURRENT"; r.pop("as_of_utc"); return r

def test_consilium_fixture_normalizes_official_observation():
    req=current()
    items=fetch(req,observed_at_utc="2026-09-28T12:00:00Z",
                http_get=lambda _:XML,query="Ukraine")
    assert len(items)==1
    item=items[0]
    assert item["source_id"]==SOURCE_ID
    assert item["origin_group"]=="consilium-eu-council"
    assert item["published_at_utc"]=="2026-09-01T11:00:00Z"
    assert normalize_observations(req,items)[0]["status"]=="SUCCESS"

def test_consilium_no_match_is_healthy_empty():
    items=fetch(current(),observed_at_utc="2026-09-28T12:00:00Z",
                http_get=lambda _:XML,query="NoSuchTerm")
    assert items==[]

def test_consilium_historical_live_retrieval_does_not_backdate_availability():
    req=sample()
    items=fetch(req,observed_at_utc="2026-09-28T12:00:00Z",
                http_get=lambda _:XML,query="Ukraine")
    assert items[0]["status"]=="INVALID"
    assert items[0]["error_code"]=="HISTORICAL_AVAILABILITY_UNPROVEN"

def test_consilium_transport_failure_is_explicit():
    items=fetch(current(),observed_at_utc="2026-09-28T12:00:00Z",
                http_get=lambda _:(_ for _ in ()).throw(TimeoutError()),query="Ukraine")
    assert items[0]["status"]=="UNAVAILABLE"

def test_consilium_malformed_xml_fails_closed():
    with pytest.raises(ValueError,match="invalid Consilium XML"):
        fetch(current(),observed_at_utc="2026-09-28T12:00:00Z",
              http_get=lambda _:"<rss>",query="Ukraine")


def test_consilium_missing_pubdate_uses_first_observed_boundary():
    req=current()
    xml="""<rss><channel><item>
    <title>Official EU statement</title>
    <description>Current official statement.</description>
    <link>https://www.consilium.europa.eu/en/press/press-releases/2026/09/01/official-statement/</link>
    </item></channel></rss>"""
    items=fetch(req,observed_at_utc="2026-09-28T12:00:00Z",http_get=lambda _:xml)
    assert items[0]["published_at_utc"]=="2026-09-28T12:00:00Z"
    assert items[0]["available_at_utc"]=="2026-09-28T12:00:00Z"
