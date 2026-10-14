"""Synthetic contract fixtures; not a successful live-source acceptance."""
import pytest
from kgeopolitical_monitor.research_source_african_union_v1 import fetch,parse_official_article
from test_research_request_v1 import sample

URL="https://au.int/en/pressreleases/20261012/african-union-advances-implementation-africa-urban-resilience-programme"
BODY="""<html><head><meta property="article:published_time" content="2026-10-12T12:30:00+03:00"></head>
<body><main><h1>The African Union advances implementation of the Africa Urban Resilience Programme</h1>
<p>The African Union Commission has concluded the second meetings of the Technical Working
Group and Steering Committee of the Africa Urban Resilience Programme, held in Lome.</p>
</main></body></html>"""
OBS="2026-10-13T11:00:00Z"

def current():
    r=sample()
    r["mode"]="CURRENT"
    r.pop("as_of_utc")
    r["period_start_utc"]="2026-10-11T00:00:00Z"
    r["period_end_utc"]="2026-10-13T23:59:59Z"
    return r

def test_explicit_article_timestamp_and_official_origin():
    out=fetch(current(),observed_at_utc=OBS,http_get=lambda _:BODY,public_url=URL)
    assert len(out)==1
    x=out[0]
    assert x["status"]=="SUCCESS"
    assert x["published_at_utc"]=="2026-10-12T09:30:00Z"
    assert x["available_at_utc"]==OBS
    assert x["origin_group"]=="african-union"
    assert x["source_id"]=="african-union-press"
    assert "verification" not in x
    assert "event_identity" not in x

def test_date_only_metadata_uses_day_anchor_without_claiming_clock():
    page=BODY.replace("2026-10-12T12:30:00+03:00","2026-10-12")
    published,_,_=parse_official_article(page)
    assert published=="2026-10-12T00:00:00Z"

@pytest.mark.parametrize("stamp", [
    "", "2026-10-12T12:00:00", "2026-99-99", "nonsense",
])
def test_missing_invalid_or_naive_publication_timestamp_fails_closed(stamp):
    page=BODY.replace("2026-10-12T12:30:00+03:00",stamp)
    with pytest.raises(ValueError):
        parse_official_article(page)

@pytest.mark.parametrize("url",[
    "https://example.com/en/pressreleases/20261012/article",
    "http://au.int/en/pressreleases/20261012/article",
    "https://au.int.evil.test/en/pressreleases/20261012/article",
    "https://visitor@au.int/en/pressreleases/20261012/article",
    "https://au.int/en/pressreleases/20261012/article#secret",
    "https://au.int/en/happening/pressreleases",
])
def test_non_authorized_url_rejected_before_fetch(url):
    calls=[]
    with pytest.raises(ValueError,match="provenance"):
        fetch(current(),observed_at_utc=OBS,http_get=lambda x:calls.append(x),public_url=url)
    assert calls==[]

@pytest.mark.parametrize("err", [TimeoutError("tls"), OSError("403 as transport")])
def test_transport_unavailable_is_not_zero_events(err):
    def fail(_):
        raise err
    out=fetch(current(),observed_at_utc=OBS,http_get=fail,public_url=URL)
    assert len(out)==1
    assert out[0]["status"]=="UNAVAILABLE"
    assert out[0]["error_code"]=="TRANSPORT_UNAVAILABLE"
    assert out[0]["published_at_utc"] is None

def test_absent_headline_fails_closed():
    with pytest.raises(ValueError,match="heading missing"):
        parse_official_article(BODY.replace("<h1>","<h2>").replace("</h1>","</h2>"))

def test_historical_no_lookahead():
    r=current()
    r["mode"]="HISTORICAL_AS_OF"
    r["as_of_utc"]="2026-10-12T12:00:00Z"
    r["period_end_utc"]="2026-10-12T12:00:00Z"
    r["requested_at_utc"]="2026-10-13T12:00:00Z"
    x=fetch(r,observed_at_utc=OBS,http_get=lambda _:BODY,public_url=URL)[0]
    assert x["status"]=="INVALID"
    assert x["error_code"]=="HISTORICAL_AVAILABILITY_UNPROVEN"

def test_out_of_period_yields_empty_not_fabricated_event():
    r=current()
    r["period_start_utc"]="2026-10-13T00:00:00Z"
    assert fetch(r,observed_at_utc=OBS,http_get=lambda _:BODY,public_url=URL)==[]

def test_non_html_and_oversize_rejected():
    with pytest.raises(ValueError):
        parse_official_article("<p>fake</p>")
    with pytest.raises(ValueError):
        parse_official_article(BODY + ("x"*2_000_001))


def test_article_scoped_date_outweighs_newer_sidebar_time():
    page = (
        '<html><body><aside class="news-carousel">'
        '<time datetime="2026-10-13T15:03:10Z">2026-10-13</time></aside>'
        '<h1>African Union advances community resilience programme</h1>'
        '<article data-history-node-id="47081" class="node-pressrelease">'
        '<div class="field field--name-field-date field--type-daterange">'
        '<time datetime="2026-10-12T07:15:26Z">Oct 12, 2026</time></div>'
        '<div>Official African Union Commission programme statement with '
        'representatives of member states and regional bodies meeting on '
        'September twenty-second through twenty-fourth.</div>'
        '</article></body></html>'
    )
    published, title, content = parse_official_article(page)
    assert published == "2026-10-12T07:15:26Z"
    assert "resilience" in title
    assert len(content) > 60


def test_sidebar_only_time_cannot_establish_au_article_publication():
    page = (
        '<html><aside><time datetime="2026-10-13T15:03:10Z">'
        '2026-10-13</time></aside><h1>Example official release</h1>'
        '<article class="node-pressrelease">'
        '<div>The African Union Commission published a public news statement '
        'with detailed institutional text but no document publication date.'
        '</div></article></html>'
    )
    with pytest.raises(ValueError, match="timestamp missing"):
        parse_official_article(page)
