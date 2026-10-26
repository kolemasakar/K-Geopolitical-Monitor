"""P5.5 offline candidate evidence register and fail-closed Critic gates.

No HTTP, filesystem writes, provider work, scheduled polling, or messaging.
Source discovery != independent, verified claim support.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from hashlib import sha256
from urllib.parse import urlsplit
import json

VALID_ACCESS = frozenset({"FULL_TEXT", "ABSTRACT_ONLY", "METADATA_ONLY"})
MAX_AGE = timedelta(days=7)


def utc(value: datetime) -> datetime:
    if not isinstance(value, datetime) or value.tzinfo is None or value.utcoffset() is None:
        raise ValueError("evidence timestamps require aware datetime")
    return value.astimezone(timezone.utc)


def _public_https(url: str) -> bool:
    try:
        parsed = urlsplit(url)
        return bool(parsed.scheme == "https" and parsed.hostname
                    and not parsed.username and not parsed.password
                    and parsed.port in (None, 443) and not parsed.fragment
                    and not any(ord(c) < 32 or ord(c) == 127 for c in url)
                    and len(url) <= 2048)
    except (ValueError, TypeError):
        return False


@dataclass(frozen=True)
class EvidenceCandidate:
    source_id: str
    publisher_id: str
    original_url: str
    document_digest_sha256: str | None
    published_at: datetime | None
    collected_at: datetime
    access: str
    # Explicit review flags are NOT inferred from the source class.
    source_page_reviewed: bool = False
    document_text_verified: bool = False
    claim_support_reviewed: bool = False
    publisher_independence_reviewed: bool = False

    def __post_init__(self) -> None:
        if not self.source_id.strip() or not self.publisher_id.strip():
            raise ValueError("source_id and publisher_id required")
        if not _public_https(self.original_url):
            raise ValueError("unsafe/non-HTTPS source URL")
        if self.access not in VALID_ACCESS:
            raise ValueError("invalid access level")
        utc(self.collected_at)
        if self.published_at is not None:
            utc(self.published_at)
        if self.document_digest_sha256 is not None and (
            len(self.document_digest_sha256) != 64
            or any(c not in "0123456789abcdef" for c in self.document_digest_sha256)
        ):
            raise ValueError("digest must be lowercase sha256")


def evidence_record(candidate: EvidenceCandidate, *, observed_at: datetime) -> dict[str, object]:
    """Redacted, deterministic audit summary; never returns URLs or content."""
    now = utc(observed_at)
    published = utc(candidate.published_at) if candidate.published_at else None
    checks = {
        "source_page_reviewed": candidate.source_page_reviewed,
        "full_text_verified": candidate.access == "FULL_TEXT" and candidate.document_text_verified
                              and candidate.document_digest_sha256 is not None,
        "publication_date_verified": bool(
            published and published <= now + timedelta(hours=1)
            and now - published <= MAX_AGE
        ),
        "claim_support_reviewed": candidate.claim_support_reviewed,
        "publisher_independence_reviewed": candidate.publisher_independence_reviewed,
    }
    # Claim support can never be counted when primary source page and content are unreviewed.
    admissible = all(checks.values())
    stable_ref = sha256(candidate.original_url.encode("utf-8")).hexdigest()
    return {
        "candidate_id": stable_ref[:24],
        "source_id": candidate.source_id,
        "publisher_id_sha256": sha256(candidate.publisher_id.encode("utf-8")).hexdigest(),
        "url_sha256": stable_ref,
        "document_digest_sha256": candidate.document_digest_sha256,
        "access": candidate.access,
        "checks": checks,
        "candidate_status": "REVIEWED_CANDIDATE" if admissible else "SHORTFALL",
    }


def critic_gate(
    *,
    claim_id: str,
    candidates: tuple[EvidenceCandidate, ...],
    observed_at: datetime,
) -> dict[str, object]:
    """Attestation-ready gate, not automated claim truth or publication approval."""
    if not claim_id.strip():
        raise ValueError("claim_id required")
    now = utc(observed_at)
    records = [evidence_record(c, observed_at=now) for c in candidates]
    reviewed = [(c, r) for c, r in zip(candidates, records)
                if r["candidate_status"] == "REVIEWED_CANDIDATE"]
    publishers = {c.publisher_id for c, _ in reviewed}
    distinct_documents = {r["document_digest_sha256"] for _, r in reviewed}
    independent_pair = len(reviewed) >= 2 and len(publishers) >= 2 and len(distinct_documents) >= 2
    # This only shows a manually reviewed candidate pair, not factual proof.
    return {
        "format": "KGM_P5_5_OFFLINE_EVIDENCE_GATE_V1",
        "claim_id_sha256": sha256(claim_id.encode("utf-8")).hexdigest(),
        "observed_at": now.isoformat(),
        "candidate_count": len(candidates),
        "reviewed_candidate_count": len(reviewed),
        "distinct_reviewed_publishers": len(publishers),
        "independent_document_pair_reviewed": independent_pair,
        "records": records,
        "critic": "READY_FOR_CLAIM_ADJUDICATION" if independent_pair else "SHORTFALL",
        "claim_factuality": "NOT_ATTESTED",
        "report_publication": "BLOCKED",
        "send": "NONE",
        "network": "NO_NETWORK",
    }


def gate_json(*, claim_id: str, candidates: tuple[EvidenceCandidate, ...], observed_at: datetime) -> str:
    return json.dumps(critic_gate(claim_id=claim_id, candidates=candidates,
                                  observed_at=observed_at), sort_keys=True)
