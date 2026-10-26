# KGM P5.5: Offline Evidence Candidate Register & Critic — v0.1

Date: 2026-10-26. The project has **one** source item admitted during owner manual P5.4 run #40272331792, **but not the item's retained full text, independent attribution or factual adjudication**. The source evidence from that run was ephemeral. This module does NOT recover the missing item.

## Scope and model

The offline-only `p55_offline_evidence_gate.py` accepts explicitly submitted `EvidenceCandidate` objects, with source ID, publisher ID, original HTTPS URL, optional document SHA-256 digest, observed and publication times, declared access tier (FULL_TEXT/ABSTRACT_ONLY/METADATA_ONLY), and four explicit **review flags**.

It emits only a redacted, deterministic register: SHA-256 identifiers, source code, hashed publisher ID, access classification, boolean review checks and gate status. Original URL, title, summary, primary text, claim text and authentication details are never printed by this module. It makes **zero HTTP calls**, creates no files or watch and sends no notifications. Caller is responsible for secure handling of any original document outside the register.

Acceptance checks for one *candidate* require:
- manually marked original page reviewed;
- FULL_TEXT access and a populated digest plus affirmative document-text review;
- timezone-aware publication date not later than 1h in the future nor more than seven days old relative to observation;
- manually marked claim support reviewed;
- manually marked publisher independence reviewed.

A claim with two such candidates must also have different declared publisher IDs and distinct document digests to reach `READY_FOR_CLAIM_ADJUDICATION`. Even at that stage **`claim_factuality=NOT_ATTESTED`** and **`report_publication=BLOCKED`**. The user-supplied review flags and publisher IDs are *not* cryptographic or independent attestations and cannot imply empirical accuracy.

## Mandatory Critic limitations

- Source freshness threshold is a provisional pilot gate (7 days), not a completeness guarantee; backdated documents, retrospective investigations, inaccessible original publications and source clocks need specialist handling.
- Independence based on human-entered publisher IDs does not prove ownership / funding / upstream copying independence.
- A matching content SHA identifies byte-identical text only; document variants may share the same upstream newswire.
- `source_page_reviewed=True` is a declaration, not a validated browser retrieval.
- No API, deployment, web fetch, source collector integration, GitHub Actions live workflow change, Telegram or persistent storage is authorized.
- No automatic promotion from P5.4 to P5.5, even though one raw GDACS item was admitted. The actor and context of its title, original date and event accuracy are unknown.
- Continue treating GDELT HTTP 429 as `MANUAL_BACKOFF_ONLY`; do not schedule retry.

## Acceptance path

1. Run fixture-only CI, including single-source SHORTFALL, expired/unknown/future dates, URL rejection, duplicate publishers and duplicate digests, no leaked raw sources.
2. Manual review of the acceptance schema, alternate original-source paths and ethics/privacy assumptions.
3. Separately authorized, bounded source *retrieval and provenance review* protocol if a real P5.5 research task is requested.
4. Only after at least two independently assessed primary documents, adjudicate claims with references, contradictions, timestamps and Critic. A complete report is a distinct future acceptance gate.

**Gate**: `P5_5_OFFLINE_EVIDENCE_REGISTER_CI_PENDING / P5_5_REAL_EVIDENCE_VERIFICATION_BLOCKED / PRODUCTION_NO_GO`.

Policies: FREE_ONLY / ON_DEMAND_ONLY / NO_SEND / CLEANUP_HOLD.
