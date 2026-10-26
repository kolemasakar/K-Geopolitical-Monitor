from types import SimpleNamespace
import pytest

from kgeopolitical_monitor.on_demand_source_policy import RestrictedSourcePolicy, RestrictedSourceTransport
from kgeopolitical_monitor.p5_public_source_probe import _ConsiliumMetadataTransport
from kgeopolitical_monitor.on_demand_gdacs import GdacsRssAdapter


class Reply:
    headers = {"Content-Type": "application/xml"}
    def __enter__(self):
        return self
    def __exit__(self, *args):
        return False
    def read(self, count):
        return b"<rss><channel></channel></rss>"


def test_gdelt_timeout_applies_only_to_gdelt(monkeypatch):
    t = RestrictedSourceTransport(RestrictedSourcePolicy(max_requests=3, timeout_seconds=7,
                                                          gdelt_timeout_seconds=12))
    seen = []
    def open_response(req, timeout):
        seen.append((req.full_url, timeout))
        return Reply()
    monkeypatch.setattr(t._opener, "open", open_response)
    t.get("https://api.gdeltproject.org/api/v2/doc/doc?query=Ukraine")
    t.get("https://www.gdacs.org/xml/rss.xml")
    t.get("https://www.consilium.europa.eu/en/rss/pressreleases.ashx")
    assert [v[1] for v in seen] == [12, 7, 7]
    assert t.calls == 3


@pytest.mark.parametrize("timeout", [0, 6, 15.1, 200])
def test_gdelt_timeout_not_outside_budget(timeout):
    with pytest.raises(ValueError, match="GDELT timeout"):
        RestrictedSourcePolicy(timeout_seconds=7, gdelt_timeout_seconds=timeout)


def test_gdacs_feed_counts_before_filter_without_raw_content():
    rss = (b'<rss><channel><item><title>Ukraine flood</title>'
           b'<description>Alert</description></item><item>'
           b'<title>Mexico earthquake</title><description>Alert</description>'
           b'</item></channel></rss>')
    class Fake:
        def get(self, url, *, headers=None):
            return SimpleNamespace(body=rss, content_type="application/xml")
    wrapper = _ConsiliumMetadataTransport(Fake(), "Ukraine")
    response = wrapper.get(GdacsRssAdapter.feed_url)
    assert len(response.body) == len(rss)
    assert wrapper.gdacs_total_entries == 2
    assert wrapper.gdacs_matching_entries == 1
    assert wrapper.total_entries is None
    assert wrapper.matching_entries is None


def test_nonrss_gdacs_does_not_fabricate_count():
    class Fake:
        def get(self, url, *, headers=None):
            return SimpleNamespace(body=b"<html></html>", content_type="text/html")
    wrapper = _ConsiliumMetadataTransport(Fake(), "Ukraine")
    wrapper.get(GdacsRssAdapter.feed_url)
    assert wrapper.gdacs_total_entries is None
    assert wrapper.gdacs_matching_entries is None
