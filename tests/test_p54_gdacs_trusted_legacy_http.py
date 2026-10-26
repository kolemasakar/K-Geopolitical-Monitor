from types import SimpleNamespace
from datetime import datetime, timezone
import xml.etree.ElementTree as ET
import pytest
from kgeopolitical_monitor.on_demand_gdacs import gdacs_safe_article_url, GdacsRssAdapter


@pytest.mark.parametrize("url", [
    "http://evil.example/a", "http://www.gdacs.org.evil.example/a",
    "http://user@www.gdacs.org/a", "http://www.gdacs.org:81/a",
    "http://www.gdacs.org//evil", "http://www.gdacs.org/a#frag",
    "http://www.gdacs.org/\\@evil", "file:///etc/passwd",
    "https://other.example/a", "https://www.gdacs.org:443/a",
])
def test_only_exact_gdacs_hosts_without_unsafe_authority(url):
    assert gdacs_safe_article_url(url)[0] is None


def test_exact_gdacs_http_normalization_is_link_only():
    assert gdacs_safe_article_url("http://gdacs.org/report.aspx?eventid=123") == (
        "https://www.gdacs.org/report.aspx?eventid=123", "GDACS_OWNED_LEGACY_HTTP"
    )
    assert gdacs_safe_article_url("https://www.gdacs.org/report.aspx") == (
        "https://www.gdacs.org/report.aspx", "GDACS_OWNED_HTTPS"
    )


def test_trusted_http_url_only_stored_not_fetched():
    rss=b"<rss><channel><item><title>Ukraine flood</title><link>http://www.gdacs.org/report.aspx</link></item></channel></rss>"
    class Stub:
        def __init__(self):
            self.calls=[]
        def get(self,url,*,headers=None):
            self.calls.append(url)
            return SimpleNamespace(body=rss,content_type="application/xml")
    t=Stub()
    watch=SimpleNamespace(query="Ukraine")
    items=GdacsRssAdapter(t).fetch(watch,datetime(2026,10,26,tzinfo=timezone.utc))
    assert t.calls==["https://www.gdacs.org/xml/rss.xml"]
    assert len(items)==1
    assert items[0].original_url=="https://www.gdacs.org/report.aspx"
    assert items[0].metadata["article_link_normalization"]=="TRUSTED_GDACS_HTTP_NORMALIZED"
