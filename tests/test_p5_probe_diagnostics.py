import pytest

from kgeopolitical_monitor.p5_probe_diagnostics import classify_attempt


@pytest.mark.parametrize("raw,expected,code", [
    ("source_http_status_429", "HTTP_RESPONSE_FAILURE", 429),
    ("source_http_status_404", "HTTP_RESPONSE_FAILURE", 404),
    ("source network failure", "NETWORK_FAILURE", None),
    ("source redirect refused", "REDIRECT_REFUSED", None),
    ("source response exceeds configured bound", "SIZE_LIMIT_EXCEEDED", None),
    ("GDELT response is not valid JSON", "GDELT_PAYLOAD_SCHEMA", None),
    ("GDACS RSS XML invalid", "RSS_PAYLOAD_SCHEMA", None),
    ("secrets=topsecret https://private.invalid/p?q=token", "UNKNOWN_FAILURE", None),
])
def test_diagnostic_categories_do_not_leak_raw_error(raw, expected, code):
    result = classify_attempt(status="FAILED", item_count=0, error=raw)
    assert result["diagnostic"] == expected
    assert result["http_status"] == code
    assert raw not in repr(result)
    assert "topsecret" not in repr(result)


def test_zero_matches_not_successful_evidence():
    d = classify_attempt(status="SUCCESS", item_count=0, error=None)
    assert d["diagnostic"] == "ZERO_MATCHES_OR_EMPTY_FEED"
    assert d["retry_guidance"] == "NONE"


def test_matched_items_treated_as_only_data_observed():
    d = classify_attempt(status="SUCCESS", item_count=3, error=None)
    assert d["diagnostic"] == "MATCHED_ITEMS"


def test_bad_http_status_rejected_without_number():
    d = classify_attempt(status="FAILED", item_count=0,
                         error="source_http_status_429 http://secret.invalid")
    assert d["diagnostic"] == "UNKNOWN_FAILURE"
    assert d["http_status"] is None
