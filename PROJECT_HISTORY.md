# PROJECT_HISTORY

Chronological record of major approved K-Geopolitical Monitor milestones.

Version: 4.2
Status: ACTIVE / P12_1_VALIDATED

## 2026-08-24 — Foundation

- Product concept, roadmap and documentation governance established.
- Initial engineering line through M4 created.

## 2026-08-26 — M5 through Phase 11

Validated milestones:

- M5 Operational Intelligence Platform — run `32953343877`, 57 passed.
- M6 Controlled Pilot Monitoring — run `32961649091`, 62 passed.
- M7 Live Public-Source Pilot — run `32962379499`, 68 passed; live smoke `32962576874`.
- M8 Live End-to-End Controlled Pilot — run `32963096313`, 73 passed; live E2E `32963354135`.
- M9 Strategic Alerts — run `32965387054`, 82 passed.
- M10 Multi-Region/Language Coverage — run `32966128001`, 88 passed.
- M11 Advanced Geopolitical Graph — run `32973378757`, 118 passed.
- M12 Advanced Forecasting — run `32980859938`, 154 passed.
- M13 Full Reporting Environment — run `32993269910`, 199 passed.
- ROADMAP Phase 11 Global Operational Coverage — run `33000478908`, 226 passed.

Key truth boundary established: publisher/domain/adapter count is not automatically underlying-origin independence.

## 2026-08-27 — Unattended runtime / private GPT pilot

- unattended monitoring harness validated — run `33012596904`, 236 passed;
- private owner-only GPT truth-boundary pilot completed — `18/18 PASS`;
- no backend Action connected during pilot;
- public sharing remained deferred.

## 2026-08-29 — E1–E7

- E1 translation foundation — `33244484173`, 241 passed.
- E2 source reputation/status history — `33244795277`, 248 passed.
- E3 owner-only read-only backend API foundation — `33247311921`, 254 passed.
- E4 real OCI ARM64 unattended runtime — `33258520620`, SUCCESS.
- E5 read-only admin dashboard — x64 `33263584520`, 282 passed; native ARM64 `33263584515`, SUCCESS.
- E6 reproducibility instrumentation — x64 `33264133429`, 290 passed; native ARM64 `33264133407`, 290 passed.
- E7 forecast probability semantics — x64 `33265984585`, 294 passed; native ARM64 `33265984622`, 294 passed.

Backend HTTPS remained undeployed; private GPT Action remained unconnected.

## 2026-09-01 — E9A owner-only runtime hardening

E9A completed:

- single-instance runtime lease;
- canonical SQLite durability/concurrency profile;
- backup/restore and real clean-project-root DR drill;
- owner-only runtime-health instrumentation;
- systemd/runtime/security hardening;
- x64/native ARM64/real OCI validation.

Evidence:

- real OCI state-preserving run `33486944907`: SUCCESS;
- rpcbind persistent-closure run `33488954688`: SUCCESS;
- final x64 run `33503085538`: `318 passed, 1 warning`, SUCCESS;
- final native ARM64 run `33503085489`: native `aarch64`, `318 passed, 1 warning`, SUCCESS;
- post-E9A canonical sync `33504369245`: `318 passed, 1 warning`, SUCCESS.

Port 111 was removed and remained absent after reboot.

Remaining explicit owner-approved candidate networking exceptions:

- public SSH TCP/22 from `0.0.0.0/0`;
- broad outbound egress.

Final E9A state:
`OWNER_ONLY_PRODUCTION_CANDIDATE_READY / COMPLETE`.

`PRODUCTION_LIVE = NOT_OPERATIONAL`.

## 2026-09-01 — ROADMAP v4 / Phase 12

- owner approved development direction: intelligence quality + source expansion + owner operational value;
- Phase 12–16 approved sequentially;
- Phase 17 remained conditional/not activated;
- Phase 18 remained conditional/new architecture approval required;
- no M14 created.

## 2026-09-01 — P12.0 canonical convergence

P12.0 reconciled current architecture/security/integration/source/model documentation with post-E9A ROADMAP v4 state.

Validation:

- validation commit `374beb4664cd92a4f41063cbbe30f6830ee3a831`;
- CI run `33517021594`;
- job `99886494759`;
- `318 passed, 1 warning / SUCCESS`.

Closure commit:
`606c3341e02acaf0bae59867ebd2262f978c4558`.

Closure CI:
`33517876078 / SUCCESS`.

Gate:
`P12_0_CANONICAL_CONVERGENCE_VALIDATED`.

## 2026-09-01 — P12.1 Source Portfolio Contract and Governance

Implemented additive source governance without activating new live sources.

Added:

- migration `022_source_portfolio_contract.sql`;
- immutable `source_portfolio_versions`;
- `SourcePortfolioService`;
- source identity/class/role governance;
- region/language scope;
- public/credentialed/restricted/user-provided access modes;
- free/paid/unknown cost mode;
- authentication mode;
- freshness/cadence;
- adapter identity/version;
- exact outbound HTTPS hostnames;
- fallback/replacement source IDs;
- availability/degradation;
- data classification;
- provenance/origin and independence constraints;
- licensing/terms and owner/reviewer/review state;
- explicit paid-provider separate-approval field.

Fail-closed semantics:

- identity conflicts rejected;
- operational availability requires approved review state;
- approved sources require adapter identity/version;
- paid provider cannot become APPROVED without separate explicit approval;
- SQL UPDATE/DELETE on portfolio versions rejected;
- portfolio metadata cannot activate collection or promote truth, verification, independent-origin count or coverage confidence.

No new live source was activated and no paid provider was approved.

Validation:

- implementation/validation commit `905a727d85701bf43d18de2d5216b83ab9a2b8bd`;
- CI run `33520371480`;
- job `99897786494`;
- `334 passed, 1 warning / SUCCESS`.

Gate:
`P12_1_SOURCE_PORTFOLIO_CONTRACT_VALIDATED`.

## Current State

- strategic ROADMAP: `APPROVED / v4`;
- Phase 12 P12.0: `VALIDATED`;
- Phase 12 P12.1: `VALIDATED`;
- next activity: `P12.2_LIVE_ADAPTER_FRAMEWORK_V2 / NEXT_NOT_STARTED`;
- controlled-live baseline: Consilium RSS + GDELT DOC 2.0;
- new live sources from P12.1: none;
- paid providers: none approved;
- runtime storage: `PROJECT_LOCAL_ONLY`;
- public API/dashboard ingress: not approved/deployed;
- private GPT Action: not connected;
- production/live: `NOT_OPERATIONAL`.
