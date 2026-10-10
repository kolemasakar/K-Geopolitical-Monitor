import pytest
from kgeopolitical_monitor.research_source_gdelt_v1 import build_query, fetch
from kgeopolitical_monitor.research_source_adapter_v1 import normalize_observations
from test_research_request_v1 import sample

ARTICLE={"url":"https://example.test/news","title":"Synthetic GDELT fixture",
         "seendate":"20260902T110000Z"}

def current():
    r=sample(); r["mode"]="CURRENT"; r.pop("as_of_utc"); return r

def test_query_is_https_bounded_and_exact_window():
    url=build_query(current(),query="Ukraine")
    assert url.startswith("https://api.gdeltproject.org/")
    assert "maxrecords=20" in url and "startdatetime=20260901000000" in url
    assert "enddatetime=20260902000000" in url

def test_fixture_normalizes_with_observed_availability():
    req=current()
    items=fetch(req,query="Ukraine",observed_at_utc="2026-09-28T12:00:00Z",
                http_get=lambda _:{"articles":[ARTICLE]})
    assert items[0]["available_at_utc"]=="2026-09-28T12:00:00Z"
    assert normalize_observations(req,items)[0]["status"]=="SUCCESS"

def test_historical_live_retrieval_cannot_backdate_availability():
    req=sample()
    items=fetch(req,query="Ukraine",observed_at_utc="2026-09-28T12:00:00Z",
                http_get=lambda _:{"articles":[ARTICLE]})
    assert items[0]["status"]=="INVALID"
    assert items[0]["error_code"]=="HISTORICAL_AVAILABILITY_UNPROVEN"
    assert normalize_observations(req,items)[0]["status"]=="INVALID"

def test_non_https_article_fails_closed():
    req=current(); bad=dict(ARTICLE,url="http://example.test/news")
    with pytest.raises(ValueError,match="non-HTTPS"):
        fetch(req,query="Ukraine",observed_at_utc="2026-09-28T12:00:00Z",
              http_get=lambda _:{"articles":[bad]})

def test_malformed_response_fails_closed():
    with pytest.raises(ValueError,match="invalid GDELT response"):
        fetch(current(),query="Ukraine",observed_at_utc="2026-09-28T12:00:00Z",
              http_get=lambda _:{"wrong":[]})

def test_rate_limit_maps_to_unavailable():
    req=current()
    class RateLimited(OSError):
        code=429
    items=fetch(req,query="Ukraine",observed_at_utc="2026-09-28T12:01:00Z",
                http_get=lambda _: (_ for _ in ()).throw(RateLimited()))
    assert items[0]["status"]=="UNAVAILABLE"
    assert items[0]["error_code"]=="RATE_LIMITED"
    assert normalize_observations(req,items)[0]["status"]=="UNAVAILABLE"

def test_timeout_maps_to_unavailable():
    req=current()
    items=fetch(req,query="Ukraine",observed_at_utc="2026-09-28T12:01:00Z",
                http_get=lambda _: (_ for _ in ()).throw(TimeoutError()))
    assert items[0]["error_code"]=="TRANSPORT_UNAVAILABLE"

def test_rate_limit_retry_is_bounded_and_backed_off():
    req=current(); calls=[]; sleeps=[]
    class RateLimited(OSError): code=429
    def transport(_):
        calls.append(1)
        if len(calls)==1: raise RateLimited()
        return {"articles":[ARTICLE]}
    items=fetch(req,query="Ukraine",observed_at_utc="2026-09-28T12:01:00Z",
                http_get=transport,sleep=sleeps.append)
    assert len(calls)==2 and sleeps==[1]
    assert items[0]["status"]=="SUCCESS"

def test_attempt_bound_cannot_exceed_two():
    with pytest.raises(ValueError,match="attempt bound"):
        fetch(current(),query="Ukraine",observed_at_utc="2026-09-28T12:01:00Z",
              http_get=lambda _:{"articles":[]},max_attempts=3)
