# PROJECT_HISTORY

Chronological record of major approved K-Geopolitical Monitor milestones.

Version: 4.5
Status: ACTIVE / P12_4_VALIDATED

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

P12.3 validated European Commission, European Parliament, GOV.UK and OSCE governed source paths. European Parliament remained explicitly `DEGRADED` because its official RSS endpoint returned anti-bot HTML to unattended acquisition. No bypass or third-party canonical mirror was introduced.

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

Validated behavior:
- P12.1 portfolio governance and fail-closed drift detection;
- P12.2-compatible public anonymous HTTPS feed adapters;
- deterministic `uk/ru/pl/tr` fixtures;
- original Unicode content preservation;
- native controlled-probe terms (`Україна`, `Украина`, `Ukraina`, `Ukrayna`);
- broad discovery collection without assuming English-query equivalence;
- source-specific failure isolation;
- explicit translation, provenance, verification and coverage boundaries.

Validation anchor evidence:
- x64 CI `33531518780`, job `99935566406`: `370 passed, 1 warning / SUCCESS`;
- native ARM64 `33531518525`, job `99935564828`: native `aarch64`, `370 passed, 1 warning / SUCCESS`, host-bootstrap/unattended/systemd PASS;
- controlled-live `33531518652`, job `99935565895`: `4 SUCCESS / 0 FAILED`.

Controlled-live native-query matches were 0 for Ukrainska Pravda, 1 for Meduza, 1 for RMF24 and 0 for Haberturk. Zero matches were correctly treated as non-failures because the acquisition/parser paths succeeded.

All four paths are governed `ACTIVE` at the validation observation. This does not claim continuous uptime.

P12.4 explicitly does not make `uk/ru/pl/tr` global language coverage, does not turn media/language counts into independent-origin counts, and does not translate inside acquisition adapters.

Gate: `P12_4_LOCAL_LANGUAGE_DISCOVERY_VALIDATED`.

## Current State

- strategic ROADMAP: `APPROVED / v4`;
- Phase 12 P12.0-P12.4: `VALIDATED`;
- next activity: `P12.5_SOURCE_HEALTH_EGRESS_INVENTORY / NEXT_NOT_STARTED`;
- paid providers: none approved;
- runtime storage: `PROJECT_LOCAL_ONLY`;
- public API/dashboard ingress: not approved/deployed;
- private GPT Action: not connected;
- production/live: `NOT_OPERATIONAL`.
