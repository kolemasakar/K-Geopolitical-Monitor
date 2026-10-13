"""Discovery does not equal execution, corroboration or multilingual coverage."""
import pytest
from kgeopolitical_monitor.research_regional_source_candidates_p24_1 import (
    regional_source_candidates, validated_candidate,
)

EXPECTED={
    "african-union-press": "AFRICA",
    "asean-news": "ASIA",
    "gcc-secretariat-news": "MIDDLE_EAST",
    "oas-press": "AMERICAS",
}

@pytest.mark.parametrize("source,region", EXPECTED.items())
def test_four_region_candidates_are_known_but_never_enabled(source,region):
    x=validated_candidate(source)
    assert x["region"]==region
    assert x["source_id"]==source
    assert x["adapter_enabled"] is False
    assert x["parsing_validated"] is False
    assert x["source_independence_credit"] is False
    assert x["factual_verification_credit"] is False
    assert x["entry_url"].startswith("https://")
    assert x["origin_group"] != ""

@pytest.mark.parametrize("name", [
    "unknown-source", "news-republisher", "asean.org", "", None, 123,
])
def test_non_registered_source_fails_closed(name):
    with pytest.raises((ValueError,TypeError)):
        validated_candidate(name)

def test_catalog_returns_defensive_copy():
    a=regional_source_candidates()
    a["african-union-press"]["region"]="EUROPE"
    a["asean-news"]["languages_observed"].append("invented")
    b=regional_source_candidates()
    assert b["african-union-press"]["region"]=="AFRICA"
    assert b["asean-news"]["languages_observed"]==["en"]

def test_transport_status_cannot_be_equated_to_parsed_data():
    for name in EXPECTED:
        x=validated_candidate(name)
        assert x["parsing_validated"] is False
        assert x["adapter_enabled"] is False

def test_redirect_and_unchecked_states_remain_explicit():
    assert validated_candidate("asean-news")["transport"]=="REDIRECT_307_NOT_RESOLVED"
    for name in ("oas-press","gcc-secretariat-news"):
        assert validated_candidate(name)["transport"]=="NOT_TESTED"
