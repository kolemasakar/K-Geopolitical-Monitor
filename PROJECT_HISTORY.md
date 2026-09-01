# PROJECT_HISTORY

Chronological record of major approved K-Geopolitical Monitor milestones.

Version: 4.6
Status: ACTIVE / P12_5_VALIDATED

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

## Current State

- strategic ROADMAP: `APPROVED / v4`;
- Phase 12 P12.0-P12.5: `VALIDATED`;
- next activity: `P12.6_PHASE_12_VALIDATION_MATRIX / NEXT_NOT_STARTED`;
- phase gate to evaluate next: `PHASE_12_INTELLIGENCE_SOURCE_NETWORK_FOUNDATION_VALIDATED`;
- paid providers: none approved;
- runtime storage: `PROJECT_LOCAL_ONLY`;
- broad outbound egress: retained explicit owner-approved candidate exception;
- public API/dashboard ingress: not approved/deployed;
- private GPT Action: not connected;
- production/live: `NOT_OPERATIONAL`.
