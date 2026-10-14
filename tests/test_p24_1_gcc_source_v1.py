"""GCC publisher parser test: synthetic fixtures, plus separately logged live probe."""
import pytest
from kgeopolitical_monitor.research_source_gcc_v1 import parse_article, fetch
from test_research_request_v1 import sample

URL="https://www.gcc-sg.org/en/MediaCenter/News/Pages/news-2026-10-13-1.aspx"
STAMP="10/13/2026"
PAGE=(
    '<html><body><span class="article-date">'+STAMP+'</span>'
    '<h2 class="article-title">GCC Secretariat reports regional consultation results</h2>'
    '<div class="article-body"><p>The Secretary General held a formal public meeting '
    'with the representatives of member states and published the outcome of '
    'regional consultations on infrastructure and economic cooperation.</p></div>'
    '</body></html>'
)
OBS="2026-10-13T15:00:00Z"

def request():
    r=sample()
    r["mode"]="CURRENT"
    r.pop("as_of_utc")
    r["period_start_utc"]="2026-10-12T00:00:00Z"
    r["period_end_utc"]="2026-10-13T23:59:59Z"
    return r

def test_day_precision_and_origin_do_not_verify_event():
    result=fetch(request(),observed_at_utc=OBS,http_get=lambda _:PAGE,public_url=URL)
    assert len(result)==1
    item=result[0]
    assert item["status"]=="SUCCESS"
    assert item["published_at_utc"]=="2026-10-13T00:00:00Z"
    assert item["origin_group"]=="gcc-secretariat"
    assert item["available_at_utc"]==OBS
    assert "verification" not in item
    assert "event_identity" not in item

@pytest.mark.parametrize("value",["", "13/13/2026","99/13/2026","2026-10-13"])
def test_invalid_date_fails_closed(value):
    with pytest.raises(ValueError):
        parse_article(PAGE.replace(STAMP,value))

@pytest.mark.parametrize("url",[
    "http://www.gcc-sg.org/en/MediaCenter/News/Pages/news-2026-10-13-1.aspx",
    "https://www.gcc-sg.org.evil.test/en/MediaCenter/News/Pages/news-2026-10-13-1.aspx",
    "https://user@www.gcc-sg.org/en/MediaCenter/News/Pages/news-2026-10-13-1.aspx",
    "https://www.gcc-sg.org/en/MediaCenter/News/Pages/news-2026-10-13-1.aspx#x",
    "https://www.gcc-sg.org/en/MediaCenter/News/Pages/default.aspx",
    "https://www.gcc-sg.org/ar/MediaCenter/News/Pages/news-2026-10-13-1.aspx",
])
def test_host_path_and_query_provenance_prevents_fetch(url):
    called=[]
    with pytest.raises(ValueError):
        fetch(request(),observed_at_utc=OBS,http_get=lambda u:called.append(u),public_url=url)
    assert called==[]

def test_disagreement_between_page_date_and_url_fails_closed():
    with pytest.raises(ValueError,match="conflicts"):
        fetch(request(),observed_at_utc=OBS,http_get=lambda _:PAGE.replace(STAMP,"10/12/2026"),public_url=URL)

def test_no_title_or_body_fails_closed():
    for fragment in [PAGE.replace("article-title","wrong-class"),PAGE.replace("article-body","wrong-class")]:
        with pytest.raises(ValueError):
            parse_article(fragment)

@pytest.mark.parametrize("err",[TimeoutError("TLS handshake"),OSError("network")])
def test_transport_failure_not_no_news(err):
    def failed(_):raise err
    item=fetch(request(),observed_at_utc=OBS,http_get=failed,public_url=URL)[0]
    assert item["status"]=="UNAVAILABLE"
    assert item["error_code"]=="TRANSPORT_UNAVAILABLE"
    assert item["published_at_utc"] is None

def test_historical_unavailable_at_cutoff():
    r=request()
    r["mode"]="HISTORICAL_AS_OF"
    r["period_end_utc"]="2026-10-13T12:00:00Z"
    r["as_of_utc"]="2026-10-13T12:00:00Z"
    r["requested_at_utc"]="2026-10-13T15:00:00Z"
    x=fetch(r,observed_at_utc=OBS,http_get=lambda _:PAGE,public_url=URL)[0]
    assert x["status"]=="INVALID"
    assert x["error_code"]=="HISTORICAL_AVAILABILITY_UNPROVEN"

def test_not_html_or_oversized_rejected():
    with pytest.raises(ValueError):
        parse_article("not html")
    with pytest.raises(ValueError):
        parse_article(PAGE + "x"*2_000_001)
