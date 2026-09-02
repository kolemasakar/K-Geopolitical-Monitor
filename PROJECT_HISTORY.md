# PROJECT_HISTORY

Chronological record of major approved K-Geopolitical Monitor milestones.

Version: 4.8
Status: ACTIVE / PHASE_13 / P13.2_VALIDATED / P13.3_CURRENT

## Validated Historical Baseline

Phases 0-11, owner-only private GPT pilot, E1-E7 and E9A remain validated as recorded in prior project checkpoints. E8 remains user-deferred and E9 shared production runtime remains not approved.

E9A final state remains `OWNER_ONLY_PRODUCTION_CANDIDATE_READY / COMPLETE`; `PRODUCTION_LIVE = NOT_OPERATIONAL`.

## 2026-09-01 — ROADMAP v4 / Phase 12

Owner approved the sequential intelligence-quality/source-expansion/owner-value development line through Phases 12-16. Phase 17 remains conditional and Phase 18 requires new architecture approval.

## P12.0–P12.2

- P12.0 gate `P12_0_CANONICAL_CONVERGENCE_VALIDATED`;
- P12.1 gate `P12_1_SOURCE_PORTFOLIO_CONTRACT_VALIDATED`;
- P12.2 gate `P12_2_ADAPTER_FRAMEWORK_V2_VALIDATED`.

These gates established canonical convergence, immutable source governance and reusable governed public adapters.

## 2026-09-01 — P12.3 Priority Authoritative Source Pack

P12.3 validated European Commission, European Parliament, GOV.UK and OSCE governed source paths. European Parliament remained explicitly `DEGRADED` because its official RSS endpoint returned non-feed/anti-bot content to unattended acquisition. No bypass or third-party canonical mirror was introduced.

Gate: `P12_3_AUTHORITATIVE_SOURCE_PACK_VALIDATED`.

## 2026-09-01 — P12.4 Local-Language and Media Discovery Pack

Implemented the first explicit public/free local-language media-discovery slice:
- Ukrainska Pravda (`uk`);
- Meduza (`ru`);
- RMF24 (`pl`);
- Haberturk (`tr`).

Implementation lineage:
- initial module commit `5c44618fa2dbc5bcf2270001bf65fbb455a02110`;
- full implementation candidate / validation anchor `595d7f0f0e6316e95aca518bb9309e615f239479`.

Validation anchor evidence:
- x64 CI `33531518780`, job `99935566406`: `370 passed, 1 warning / SUCCESS`;
- native ARM64 `33531518525`, job `99935564828`: native `aarch64`, `370 passed, 1 warning / SUCCESS`, host-bootstrap/unattended/systemd PASS;
- controlled-live `33531518652`, job `99935565895`: `4 SUCCESS / 0 FAILED`.

P12.4 explicitly does not make `uk/ru/pl/tr` global language coverage, does not turn media/language counts into independent-origin counts, and does not translate inside acquisition adapters.

Gate: `P12_4_LOCAL_LANGUAGE_DISCOVERY_VALIDATED`.

## 2026-09-01 — P12.5 Source Health, Freshness and Egress Inventory

Implemented a read-only operational assessment layer over P12.1 governance and persisted source-collection/provenance state. P12.5 separates governed portfolio state, latest operational acquisition state, measurement freshness and observed publisher-content freshness.

Implementation lineage:
- core assessment commit `19f6d1a57e695ab3720d0118b44349dcdfd9c706`;
- full implementation candidate / validation anchor `92d0c0516351e2af7ba836d3ae711dd414d22023`.

Validation evidence:
- x64 CI `33533313297`, job `99941475948`: `382 passed, 1 warning / SUCCESS`;
- native ARM64 `33533313313`, job `99941475266`: native `aarch64`, `382 passed, 1 warning / SUCCESS`, bootstrap/unattended/systemd PASS;
- controlled-live `33533313654`, job `99941475574`: workflow `SUCCESS`, `10/10` source paths measured, `8 SUCCESS / 2 FAILED`, ten HTTPS egress entries.

Measured findings:
- European Parliament — measured `UNAVAILABLE / PARSER`; governed `DEGRADED` retained;
- Haberturk — measured `UNAVAILABLE / UNKNOWN` because an item `original_url` failed HTTP/HTTPS validation; governed `ACTIVE` retained pending reconciliation;
- OSCE — acquisition `HEALTHY`, observed publisher content `STALE`;
- Consilium and European Commission — successful zero-match acquisitions, content freshness left `UNKNOWN` rather than inferred.

P12.5 validates measurement completeness, not universal source health. It adds no schema migration, changes no verification state, and does not turn ten inventoried hosts into an outbound firewall allowlist.

Gate: `P12_5_SOURCE_HEALTH_EGRESS_INVENTORY_VALIDATED`.

## 2026-09-01 — P12.6 Phase 12 Validation Matrix

Phase 12 closed with `PASS_WITH_KNOWN_LIMITATIONS` and gate `PHASE_12_INTELLIGENCE_SOURCE_NETWORK_FOUNDATION_VALIDATED`.

Final Phase 12 closure HEAD: `3211994450c11698a553f5249e3ecec94079b5ad`.
- x64 run `33552777066`, job `100006077954`: `391 passed, 1 warning / SUCCESS`;
- native ARM64 run `33552776997`, job `100006077747`: native `aarch64`, `391 passed, 1 warning / SUCCESS`, bootstrap/unattended/systemd PASS.

Known limitations remained explicit: European Parliament parser degradation, Haberturk item-URL failure observation, stale OSCE content observation, limited `uk/ru/pl/tr` language slice, broad outbound egress and public SSH candidate exceptions. None of these observations were converted into truth or exhaustive coverage claims.

## 2026-09-01 — P13.0 Semantic Verification Architecture Contract

Phase 13 began with an architecture/test contract rather than a schema change.

Gate: `P13_0_SEMANTIC_VERIFICATION_ARCHITECTURE_CONTRACT_VALIDATED`.
Validation anchor: `4422fae5e2a4546585a43237d2124f466c457543`.
- x64 run `33554568574`, job `100012110127`: `399 passed, 1 warning / SUCCESS`;
- native ARM64 run `33554568570`, job `100012110488`: native `aarch64`, `399 passed, 1 warning / SUCCESS`, bootstrap/unattended/systemd PASS.

P13.0 established that semantic claim identity is not headline identity; publisher/publication is distinct from cited source and underlying origin; evidence relation, independence, contradiction and verification are separate layers; count-based domain/host shortcuts cannot become canonical truth rules; extraction, factual and coverage confidence remain separate.

## 2026-09-01 — P13.1 Structured Semantic Claim Model

P13.1 introduced the first additive Phase 13 semantic schema.

Implementation/validation anchor: `69c3282077ad8dd90ef239c0594be56f9363bfe5`.
- migration `023_structured_semantic_claim_model.sql`;
- module `src/kgeopolitical_monitor/semantic_claims.py`;
- deterministic regression suite `tests/test_semantic_claims.py`;
- canonical database migration guard updated for migration 023.

Validation evidence:
- x64 run `33555804493`, job `100016206225`: `408 passed, 1 warning / SUCCESS`;
- native ARM64 run `33555804396`, job `100016205406`: native `aarch64`, `408 passed, 1 warning / SUCCESS`, bootstrap/unattended/systemd PASS.

Validated behavior:
- explicit caller-controlled semantic claim identity;
- append-only versioning and supersession;
- structured proposition, actor/subject/object/action, polarity, modality, time/location/quantity, original-language and extraction metadata;
- non-evidentiary links to legacy claims, live-analysis claims and raw items;
- Unicode/original-language preservation;
- extraction confidence remains separate from factual confidence;
- no P13.2-P13.5 provenance/independence/contradiction/verification-policy fields were introduced.

Gate: `P13_1_STRUCTURED_SEMANTIC_CLAIM_MODEL_VALIDATED`.

## 2026-09-02 — P13.2 Provenance / Underlying-Origin Relation Model

P13.2 introduced additive append-only provenance/origin persistence tied to P13.1 semantic claims and existing source/raw objects.

Implementation/validation anchor: `6cd37a334b122ae5de2b4cb6272f9cc222f1f174`.
- migration `024_semantic_provenance_origin_relation_model.sql`;
- module `src/kgeopolitical_monitor/semantic_provenance.py`;
- legacy API compatibility preserved through `src/kgeopolitical_monitor/provenance.py`;
- deterministic provenance regression coverage.

Validation evidence:
- x64 run `33558425194`, job `100024835794`: `420 passed, 1 warning / SUCCESS`;
- native ARM64 run `33558425252`, job `100024836399`: native `aarch64`, `420 passed, 1 warning / SUCCESS`, bootstrap/unattended/systemd PASS.

Validated behavior:
- publication/publisher, immediate acquired source, cited/quoted source and underlying origin remain distinct;
- official statement/document, wire, dataset, social/user-provided, unknown and mixed origins are explicit;
- citation, syndication, repost, translation and derivation are provenance relationships, not independent corroboration;
- unresolved/mixed origin remains explicit rather than inferred from publisher/domain/language differences;
- source/raw traceability and URL credential-leak guards fail closed;
- no P13.3 independence, P13.4 contradiction, P13.5 verification/confidence or P13.6 live cutover semantics were introduced.

Gate: `P13_2_PROVENANCE_ORIGIN_RELATION_MODEL_VALIDATED`.

## Current State

- strategic ROADMAP: `APPROVED / v4`;
- Phase 12: `PHASE_12_INTELLIGENCE_SOURCE_NETWORK_FOUNDATION_VALIDATED / PASS_WITH_KNOWN_LIMITATIONS`;
- Phase 13: `APPROVED / ACTIVE_ENGINEERING_PHASE`;
- P13.0: `P13_0_SEMANTIC_VERIFICATION_ARCHITECTURE_CONTRACT_VALIDATED`;
- P13.1: `P13_1_STRUCTURED_SEMANTIC_CLAIM_MODEL_VALIDATED`;
- P13.2: `P13_2_PROVENANCE_ORIGIN_RELATION_MODEL_VALIDATED`;
- current activity: `P13.3_EVIDENCE_RELATION_INDEPENDENCE / CURRENT_NOT_STARTED`;
- next gate: `P13_3_EVIDENCE_RELATION_INDEPENDENCE_VALIDATED`;
- paid providers: none approved;
- runtime storage: `PROJECT_LOCAL_ONLY`;
- broad outbound egress: retained explicit owner-approved candidate exception;
- public API/dashboard ingress: not approved/deployed;
- private GPT Action: not connected;
- production/live: `NOT_OPERATIONAL`.

Production/live operational status: NOT_OPERATIONAL
Runtime storage mode: PROJECT_LOCAL_ONLY
