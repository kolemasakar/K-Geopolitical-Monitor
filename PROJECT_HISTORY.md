# PROJECT_HISTORY

Chronological record of major approved K-Geopolitical Monitor milestones.

Version: 4.4
Status: ACTIVE / P12_3_VALIDATED

## Validated Historical Baseline

Phases 0-11, owner-only private GPT pilot, E1-E7 and E9A remain validated as recorded in prior project checkpoints. E8 remains user-deferred and E9 shared production runtime remains not approved.

E9A final state remains `OWNER_ONLY_PRODUCTION_CANDIDATE_READY / COMPLETE`; `PRODUCTION_LIVE = NOT_OPERATIONAL`.

## 2026-09-01 — ROADMAP v4 / Phase 12

Owner approved the sequential intelligence-quality/source-expansion/owner-value development line through Phases 12-16. Phase 17 remains conditional and Phase 18 requires new architecture approval.

## 2026-09-01 — P12.0 Canonical Convergence

- validation anchor `374beb4664cd92a4f41063cbbe30f6830ee3a831`;
- CI `33517021594`, job `99886494759`, `318 passed, 1 warning / SUCCESS`;
- gate `P12_0_CANONICAL_CONVERGENCE_VALIDATED`.

## 2026-09-01 — P12.1 Source Portfolio Contract and Governance

- implementation/validation `905a727d85701bf43d18de2d5216b83ab9a2b8bd`;
- CI `33520371480`, job `99897786494`, `334 passed, 1 warning / SUCCESS`;
- immutable source-portfolio governance added without source activation;
- gate `P12_1_SOURCE_PORTFOLIO_CONTRACT_VALIDATED`.

## 2026-09-01 — P12.2 Live Adapter Framework v2

- reusable bounded read-only HTTPS transport, deterministic RSS/Atom/JSON parsers and governed adapter contracts added;
- validation anchor `cb6866e82d5dc4a26042e0b9d08e9098aae10ecb`;
- CI `33523574819`, job `99908604206`, `346 passed, 1 warning / SUCCESS`;
- no new source activated and no paid provider approved;
- gate `P12_2_ADAPTER_FRAMEWORK_V2_VALIDATED`.

## 2026-09-01 — P12.3 Priority Authoritative Source Pack

Implemented a P12.1-governed/P12.2-compatible public/free authoritative pack:
- European Commission Press Corner;
- European Parliament Press Releases;
- UK Government News and Communications;
- OSCE Latest News.

Implementation lineage:
- pack implementation `02ba74c59f34d70cbc1ceec9cc806159554f603b`;
- controlled-live smoke `dbeed606db6d07602b0a17d86c30838afd8a4213`;
- governance-corrected validation anchor `038122e44139d6ff23bc5d79bb50a8dee3c38cde`.

Validation anchor evidence:
- x64 CI `33527433110`, job `99921745359`: `356 passed, 1 warning / SUCCESS`;
- native ARM64 `33527433197`, job `99921746285`: `356 passed, 1 warning / SUCCESS` plus bootstrap/unattended/systemd checks PASS;
- controlled-live repeat `33527433106`, job `99921745640`: 3 source acquisitions `SUCCESS`, European Parliament `FAILED`/governed `DEGRADED`, workflow SUCCESS.

European Parliament's official RSS endpoint returned anti-bot HTML rather than XML to the unattended runner. The official endpoint was retained and governed as `DEGRADED`; no bypass or third-party canonical mirror was introduced.

Validated source states:
- European Commission `ACTIVE`;
- European Parliament `DEGRADED`;
- GOV.UK `ACTIVE`;
- OSCE `ACTIVE`.

P12.3 validation explicitly does not mean 4/4 endpoint health, independent-origin count, exhaustive coverage or production/live activation.

Gate: `P12_3_AUTHORITATIVE_SOURCE_PACK_VALIDATED`.

## Current State

- strategic ROADMAP: `APPROVED / v4`;
- Phase 12 P12.0-P12.3: `VALIDATED`;
- next activity: `P12.4_LOCAL_LANGUAGE_AND_MEDIA_DISCOVERY_PACK / NEXT_NOT_STARTED`;
- P12.3 live state: 3 `ACTIVE`, European Parliament `DEGRADED`;
- paid providers: none approved;
- runtime storage: `PROJECT_LOCAL_ONLY`;
- public API/dashboard ingress: not approved/deployed;
- private GPT Action: not connected;
- production/live: `NOT_OPERATIONAL`.
