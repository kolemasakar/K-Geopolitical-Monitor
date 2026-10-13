"""P24.1 bounded synthetic regression: parser semantics, origin independence, negative mapping.

All page fragments are LOCAL FIXTURES and must not be counted as evidence of
real historical events or live-source availability.
"""
import copy

import pytest

from kgeopolitical_monitor.research_generic_mapping_profile_v1 import apply_mapping_profile
from kgeopolitical_monitor.research_generic_mapping_v1 import correlate_explicit_facts
from kgeopolitical_monitor.research_source_govuk_v1 import fetch as govuk_fetch
from kgeopolitical_monitor.research_source_bundesregierung_v1 import fetch as de_fetch
from kgeopolitical_monitor.research_source_moldova_mfa_v1 import fetch as moldova_fetch
from test_research_request_v1 import sample


EVENT = {
    "family": "DIPLOMATIC", "event_date_utc": "2026-10-08T00:00:00Z",
    "action_key": "MEET",
    "actor_keys": ["moldova-dpm-mfa-mihai-popsoi", "nato-dsg-radmila-shekerinska"],
    "target_keys": [], "subject_key": "nato-moldova-bilateral-meeting",
    "location_key": "chisinau-moldova",
}
CLAIM = {"claim_type": "STATUS", "value_keys": ["meeting-held"], "unit_key": None}


def mapping(source_id, phrases):
    return {
        "source_id": source_id, "required_phrases": list(phrases),
        "event_descriptor": copy.deepcopy(EVENT),
        "claim_descriptor": copy.deepcopy(CLAIM),
    }


# The source-specific profiles deliberately do not infer cross-language synonyms.
MOLDOVA_PROFILE = mapping("moldova-mfa", ("mihai popșoi", "radmila shekerinska"))
NATO_PROFILE = mapping("nato-news", ("mihai popsoi", "radmila shekerinska"))


def request():
    r = sample()
    r["mode"] = "CURRENT"
    r.pop("as_of_utc", None)
    r["period_start_utc"] = "2026-10-08T00:00:00Z"
    r["period_end_utc"] = "2026-10-09T23:59:59Z"
    return r


def moldova_html(body, timestamp="2026-10-08T16:17:15+03:00"):
    return (f'<html><span property="dc:date dc:created" content="{timestamp}"></span>'
            f'<div class="field-name-body"><div class="field-item even">'
            f'{body}</div></div></div></html>')


def govuk_html(body, timestamp="2026-10-08T14:36:40+01:00"):
    return (f'<html><script type="application/ld+json">'
            f'{{"datePublished":"{timestamp}"}}</script><body>{body}</body></html>')


def synthetic_fact(source_id, origin, day="2026-10-08T00:00:00Z", claim=None):
    event = copy.deepcopy(EVENT)
    event["event_date_utc"] = day
    return {
        "schema_version": "kgm.research.generic-mapping.v1",
        "source_id": source_id, "origin_group": origin,
        "source_fact_id": source_id + "-fixture",
        "public_url": "https://example.org/fixtures/" + source_id,
        "event_descriptor": event,
        "claim_descriptor": copy.deepcopy(CLAIM if claim is None else claim),
    }


def test_moldova_parser_normalizes_tz_and_strict_local_language_profile():
    page = moldova_html("<p>Mihai Popșoi met Radmila Shekerinska.</p>")
    x = moldova_fetch(request(), observed_at_utc="2026-10-09T10:00:00Z",
                      http_get=lambda _: page,
                      public_url="https://mfa.gov.md/ro/content/fixture",
                      mapping_profile=MOLDOVA_PROFILE)[0]
    assert x["status"] == "SUCCESS"
    assert x["published_at_utc"] == "2026-10-08T13:17:15Z"
    assert x["origin_group"] == "moldova-mfa"
    assert x["event_descriptor"] == EVENT


@pytest.mark.parametrize("body", [
    "<p>Mihai Popșoi met another minister.</p>",
    "<p>Radmila Shekerinska met another minister.</p>",
    "<p>Other names and event.</p>",
    "<p>Mihai Popsoi met Radmila Shekerinska.</p>",  # diacritics not guessed
])
def test_moldova_mapping_fails_closed_without_both_exact_phrases(body):
    page = moldova_html(body)
    x = moldova_fetch(request(), observed_at_utc="2026-10-09T10:00:00Z",
                      http_get=lambda _: page,
                      public_url="https://mfa.gov.md/ro/content/fixture",
                      mapping_profile=MOLDOVA_PROFILE)[0]
    assert x["status"] == "SUCCESS"
    assert "event_identity" not in x
    assert "claim_signature" not in x


def test_profile_cannot_be_reused_across_source_identifiers():
    with pytest.raises(ValueError, match="source mismatch"):
        apply_mapping_profile(
            {"source_id": "nato-news", "observation_id": "fixture"},
            "Mihai Popșoi met Radmila Shekerinska.", MOLDOVA_PROFILE,
        )


@pytest.mark.parametrize("stamp", ["", "2026-10-08T13:30:00", "not-a-date"])
def test_govuk_parser_rejects_missing_naive_or_invalid_publication_time(stamp):
    if stamp:
        page = govuk_html("Synthetic test text", stamp)
    else:
        page = "<html><body>Synthetic test text</body></html>"
    with pytest.raises(ValueError):
        govuk_fetch(request(), observed_at_utc="2026-10-09T10:00:00Z",
                    http_get=lambda _: page,
                    public_url="https://www.gov.uk/government/news/fixture")


def test_govuk_tls_timeout_emits_unavailable_not_empty_or_success():
    x = govuk_fetch(request(), observed_at_utc="2026-10-09T10:00:00Z",
                    http_get=lambda _: (_ for _ in ()).throw(TimeoutError("TLS fixture")),
                    public_url="https://www.gov.uk/government/news/fixture")[0]
    assert x["status"] == "UNAVAILABLE"
    assert x["error_code"] == "TRANSPORT_UNAVAILABLE"
    assert x["origin_group"] == "uk-government"


def test_bundesregierung_transport_oserror_emits_unavailable():
    x = de_fetch(request(), observed_at_utc="2026-10-09T10:00:00Z",
                 http_get=lambda _: (_ for _ in ()).throw(OSError("socket fixture")),
                 public_url="https://www.bundesregierung.de/breg-en/news/fixture")[0]
    assert x["status"] == "UNAVAILABLE"
    assert x["error_code"] == "TRANSPORT_UNAVAILABLE"


def test_same_underlying_origin_across_distinct_publishers_is_not_independent():
    x = correlate_explicit_facts([
        synthetic_fact("publisher-a", "single-ministry"),
        synthetic_fact("publisher-b", "single-ministry"),
    ])
    assert x["event_match"] is True
    assert x["claim_match"] is True
    assert x["independent_origin_candidate"] is False
    assert "verification" not in x


def test_different_origin_same_claim_only_origin_candidate_not_verification():
    x = correlate_explicit_facts([
        synthetic_fact("moldova-mfa", "moldova-mfa"),
        synthetic_fact("nato-news", "nato"),
    ])
    assert x["event_match"] and x["claim_match"]
    assert x["independent_origin_candidate"] is True
    assert "verification" not in x
    assert "factual_verification_credit" not in x


def test_independent_origin_disagreement_does_not_match_claim():
    contrary = {"claim_type": "STATUS", "value_keys": ["meeting-cancelled"], "unit_key": None}
    x = correlate_explicit_facts([
        synthetic_fact("moldova-mfa", "moldova-mfa"),
        synthetic_fact("nato-news", "nato", claim=contrary),
    ])
    assert x["event_match"] is True
    assert x["claim_match"] is False
    assert x["independent_origin_candidate"] is True
    assert "verification" not in x


def test_day_mismatch_prohibits_event_merge_despite_identical_claim():
    x = correlate_explicit_facts([
        synthetic_fact("source-a", "origin-a"),
        synthetic_fact("source-b", "origin-b", day="2026-10-09T00:00:00Z"),
    ])
    assert x["event_match"] is False
    assert x["event_identity"] is None


def test_duplicate_publisher_in_fact_batch_rejected():
    with pytest.raises(ValueError, match="duplicate source"):
        correlate_explicit_facts([
            synthetic_fact("source-a", "origin-a"),
            synthetic_fact("source-a", "origin-b"),
        ])


def test_bundesregierung_live_shape_date_only_article_header_is_parsed():
    page = ('<html><ul class="bpa-collection-list">'
            '<li class="bpa-collection-item">Transcript of press conference</li>'
            '<li class="bpa-collection-item" >Thursday, 8 October 2026</li>'
            '</ul><body>Federal Government confirms a public statement.</body></html>')
    x = de_fetch(request(), observed_at_utc="2026-10-09T10:00:00Z",
                 http_get=lambda _: page,
                 public_url="https://www.bundesregierung.de/breg-en/news/fixture")[0]
    assert x["status"] == "SUCCESS"
    # Day-only precision uses 00Z as a day anchor, not a known article clock time.
    assert x["published_at_utc"] == "2026-10-08T00:00:00Z"
    assert x["origin_group"] == "germany-federal-government"


@pytest.mark.parametrize("fragment", [
    '<li class="bpa-collection-item">Monday, 8 October 2026</li>',
    '<li class="bpa-collection-item">Thursday, 8 October 2026</li>'
    '<li class="bpa-collection-item">Friday, 9 October 2026</li>',
    '<p>Thursday, 8 October 2026</p>',
])
def test_bundesregierung_date_only_fallback_fails_closed_on_ambiguity_or_wrong_location(fragment):
    with pytest.raises(ValueError, match="Bundesregierung publication"):
        de_fetch(request(), observed_at_utc="2026-10-09T10:00:00Z",
                 http_get=lambda _: "<html><body>" + fragment + "</body></html>",
                 public_url="https://www.bundesregierung.de/breg-en/news/fixture")


def test_explicit_uk_german_profiles_match_one_event_but_not_verified():
    from kgeopolitical_monitor.research_mapping_profiles_p24_1_v1 import (
        get_ratification_profile, SOURCE_URLS,
    )
    from kgeopolitical_monitor.research_generic_mapping_v1 import SCHEMA
    uk=get_ratification_profile("govuk-official")
    de=get_ratification_profile("germany-federal-government")
    statement=("Federal Chancellor Friedrich Merz and Prime Minister Andy Burnham "
               "finalised the ratification of the Kensington Treaty.")
    uk_ob,matched_uk=apply_mapping_profile({"source_id":"govuk-official"},statement,uk)
    de_ob,matched_de=apply_mapping_profile(
        {"source_id":"germany-federal-government"},statement,de)
    assert matched_uk and matched_de
    assert uk_ob["event_identity"]==de_ob["event_identity"]
    facts=[]
    for mapped,source,origin in [
        (uk_ob,"govuk-official","uk-government"),
        (de_ob,"germany-federal-government","germany-federal-government"),
    ]:
        facts.append({
            "schema_version":SCHEMA,
            "source_id":source,"origin_group":origin,
            "source_fact_id":source+"-fixture",
            "public_url":SOURCE_URLS[source],
            "event_descriptor":mapped["event_descriptor"],
            "claim_descriptor":mapped["claim_descriptor"],
        })
    result=correlate_explicit_facts(facts)
    assert result["event_match"] and result["claim_match"]
    assert result["independent_origin_candidate"] is True
    assert "verification" not in result
    assert "factual_verification_credit" not in result


def test_uk_german_profiles_source_gate_and_copy_isolation():
    from kgeopolitical_monitor.research_mapping_profiles_p24_1_v1 import (
        get_ratification_profile,
    )
    with pytest.raises(ValueError,match="unapproved"):
        get_ratification_profile("a-reposter")
    p=get_ratification_profile("govuk-official")
    p["required_phrases"].append("synthetic unrelated marker")
    q=get_ratification_profile("govuk-official")
    assert "synthetic unrelated marker" not in q["required_phrases"]
    with pytest.raises(ValueError,match="source mismatch"):
        apply_mapping_profile({"source_id":"germany-federal-government"},
                              "Friedrich Merz Kensington Treaty ratification",q)


def test_uk_german_profiles_do_not_merge_same_actors_different_action():
    from kgeopolitical_monitor.research_mapping_profiles_p24_1_v1 import (
        get_ratification_profile,
    )
    profile=get_ratification_profile("govuk-official")
    item,matched=apply_mapping_profile({"source_id":"govuk-official"},
        "Friedrich Merz and PM met to discuss the Kensington Treaty.",profile)
    assert matched is False
    assert "event_identity" not in item
