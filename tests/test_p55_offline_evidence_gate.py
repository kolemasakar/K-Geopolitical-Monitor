"""P5.5 safe offline candidate/Critic tests (no external access)."""
from dataclasses import replace
from datetime import datetime, timedelta, timezone
from hashlib import sha256
import json
import pytest
from kgeopolitical_monitor.p55_offline_evidence_gate import (
    EvidenceCandidate, evidence_record, critic_gate, gate_json,
)

NOW=datetime(2026,10,26,12,0,tzinfo=timezone.utc)


def item(publisher="GDACS", url="https://www.gdacs.org/report/1",
         days=1, full=True):
    return EvidenceCandidate(
        source_id=publisher.lower(), publisher_id=publisher,
        original_url=url, document_digest_sha256=sha256(url.encode()).hexdigest(),
        published_at=NOW-timedelta(days=days),
        collected_at=NOW, access="FULL_TEXT" if full else "METADATA_ONLY",
        source_page_reviewed=full,
        document_text_verified=full,
        claim_support_reviewed=full,
        publisher_independence_reviewed=full,
    )


def test_discovery_metadata_only_does_not_count_as_verified():
    discovered=replace(item(), access="METADATA_ONLY",
                       source_page_reviewed=False,document_text_verified=False,
                       claim_support_reviewed=False,publisher_independence_reviewed=False)
    result=critic_gate(claim_id="claim-1", candidates=(discovered,),observed_at=NOW)
    assert result["reviewed_candidate_count"]==0
    assert result["critic"]=="SHORTFALL"
    assert result["claim_factuality"]=="NOT_ATTESTED"
    assert result["report_publication"]=="BLOCKED"
    assert result["network"]=="NO_NETWORK"


@pytest.mark.parametrize("url", [
    "http://www.gdacs.org/a", "https://user:pass@www.gdacs.org/a",
    "https://www.gdacs.org:8443/a", "https://www.gdacs.org/a#fragment",
    "file:///etc/passwd", "https://www.gdacs.org/%0a\nb",
])
def test_refuse_unsafe_source_url(url):
    with pytest.raises(ValueError):
        replace(item(), original_url=url)


def test_freshness_fail_closed_on_unknown_future_and_old():
    for published in (None, NOW+timedelta(days=2),NOW-timedelta(days=8)):
        c=replace(item(),published_at=published)
        r=evidence_record(c,observed_at=NOW)
        assert r["checks"]["publication_date_verified"] is False
        assert r["candidate_status"]=="SHORTFALL"


def test_one_good_source_is_not_independent_corroboration():
    out=critic_gate(claim_id="c",candidates=(item(),),observed_at=NOW)
    assert out["reviewed_candidate_count"]==1
    assert out["critic"]=="SHORTFALL"


def test_two_same_publishers_do_not_count_as_independent():
    a=item()
    b=item(url="https://www.gdacs.org/report/2")
    out=critic_gate(claim_id="c",candidates=(a,b),observed_at=NOW)
    assert out["reviewed_candidate_count"]==2
    assert out["distinct_reviewed_publishers"]==1
    assert out["critic"]=="SHORTFALL"


def test_reviewed_distinct_publishers_only_enable_next_manual_step():
    a=item()
    b=item(publisher="Consilium",url="https://www.consilium.europa.eu/en/a")
    out=critic_gate(claim_id="c",candidates=(a,b),observed_at=NOW)
    assert out["critic"]=="READY_FOR_CLAIM_ADJUDICATION"
    assert out["claim_factuality"]=="NOT_ATTESTED"
    assert out["report_publication"]=="BLOCKED"


def test_duplicate_same_document_does_not_count():
    a=item()
    b=replace(item(publisher="Consilium",url="https://www.consilium.europa.eu/en/a"),
              document_digest_sha256=a.document_digest_sha256)
    out=critic_gate(claim_id="c",candidates=(a,b),observed_at=NOW)
    assert out["critic"]=="SHORTFALL"


def test_no_private_url_or_raw_claim_emitted():
    c=item(url="https://www.gdacs.org/report/private-token")
    j=gate_json(claim_id="secret claim text", candidates=(c,),observed_at=NOW)
    assert "secret claim text" not in j
    assert "private-token" not in j
    assert "https://" not in j
    assert json.loads(j)["send"]=="NONE"


def test_naive_datetime_rejected():
    with pytest.raises(ValueError):
        replace(item(), published_at=datetime(2026,10,26))
