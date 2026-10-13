"""P24.1 deterministic transport and provenance regression, no live requests."""
from copy import deepcopy
import pytest

from kgeopolitical_monitor.research_source_gdelt_v1 import fetch as gdelt_fetch
from kgeopolitical_monitor.research_source_usgs_v1 import fetch as usgs_fetch
from kgeopolitical_monitor.research_source_gdacs_v1 import fetch as gdacs_fetch
from kgeopolitical_monitor.research_source_ecb_v1 import fetch as ecb_fetch
from kgeopolitical_monitor.research_source_gfz_v1 import fetch as gfz_fetch
from test_research_request_v1 import sample


def current():
    req=sample()
    req["mode"]="CURRENT"
    req.pop("as_of_utc")
    req["period_start_utc"]="2026-10-07T00:00:00Z"
    req["period_end_utc"]="2026-10-13T23:59:59Z"
    req["max_results"]=3
    return req


OBSERVED="2026-10-13T12:00:00Z"


@pytest.mark.parametrize("err", [
    TimeoutError("TLS handshake timeout"),
    OSError("network unreachable"),
])
def test_gdelt_transport_errors_fail_closed_one_attempt(err):
    calls=[]
    def failing(url):
        calls.append(url)
        raise err
    result=gdelt_fetch(current(),query="Ethiopia",observed_at_utc=OBSERVED,
                       http_get=failing,max_attempts=1)
    assert len(calls)==1
    assert len(result)==1
    assert result[0]["status"]=="UNAVAILABLE"
    assert result[0]["error_code"]=="TRANSPORT_UNAVAILABLE"
    assert result[0]["published_at_utc"] is None
    assert result[0]["available_at_utc"] is None


def test_usgs_timeout_does_not_become_empty_zero_event_result():
    calls=[]
    def timed_out(url):
        calls.append(url)
        raise TimeoutError("simulated USGS timeout")
    out=usgs_fetch(current(),observed_at_utc=OBSERVED,http_get=timed_out)
    assert len(calls)==1
    assert len(out)==1
    assert out[0]["status"]=="UNAVAILABLE"
    assert out[0]["error_code"]=="TRANSPORT_UNAVAILABLE"
    assert out[0]["origin_group"]=="usgs-neic"


def test_gdacs_neic_and_usgs_share_underlying_origin_label():
    feat={
      "type":"Feature",
      "properties":{"eventid":245,"eventtype":"EQ","name":"M 5.2 fixture",
                    "fromdate":"2026-10-12T10:00:00Z",
                    "datemodified":"2026-10-12T11:00:00Z",
                    "source":"NEIC","severitydata":{"severity":5.2}},
      "geometry":{"type":"Point","coordinates":[45.0,12.0,8.0]}}
    out=gdacs_fetch(current(),observed_at_utc=OBSERVED,
                    http_get=lambda _:{"features":[deepcopy(feat)]})
    assert len(out)==1
    assert out[0]["status"]=="SUCCESS"
    assert out[0]["origin_group"]=="usgs-neic"
    assert out[0]["event_identity"] is not None
    assert out[0]["claim_signature"] is not None


def test_gdacs_unknown_eq_source_must_not_assume_neic():
    feat={
      "type":"Feature",
      "properties":{"eventid":246,"eventtype":"EQ","name":"M 5.2 fixture",
                    "fromdate":"2026-10-12T10:00:00Z",
                    "source":"UNKNOWN","severitydata":{"severity":5.2}},
      "geometry":{"type":"Point","coordinates":[45.0,12.0,8.0]}}
    out=gdacs_fetch(current(),observed_at_utc=OBSERVED,
                    http_get=lambda _:{"features":[deepcopy(feat)]})
    assert out[0]["origin_group"] is None


def test_ecb_malformed_xml_is_error_not_success():
    with pytest.raises(ValueError,match="invalid ECB XML"):
        ecb_fetch(current(),observed_at_utc=OBSERVED,
                  http_get=lambda _:b"<rss><channel>")


def test_gfz_malformed_header_is_error_not_success():
    with pytest.raises(ValueError,match="invalid GFZ header"):
        gfz_fetch(current(),observed_at_utc=OBSERVED,
                  http_get=lambda _:"<html>gateway proxy page</html>")
