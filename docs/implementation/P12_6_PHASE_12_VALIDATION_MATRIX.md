# P12.6 — Phase 12 Validation Matrix

Date: 2026-09-01
State: `VALIDATION_CANDIDATE / REGRESSION_PENDING`
Project: K-Geopolitical Monitor
Target phase gate: `PHASE_12_INTELLIGENCE_SOURCE_NETWORK_FOUNDATION_VALIDATED`
Candidate decision: `PASS_WITH_KNOWN_LIMITATIONS`
Base closure HEAD: `248c38f02724f6e210850df56e96c95a97a14d53`

## Purpose

Validate the complete Phase 12 chain P12.0-P12.5 as one intelligence-quality/source-network foundation. The matrix evaluates whether the implemented governance, adapter, source-pack, language-discovery, operational-health and egress-inventory layers are mutually consistent and preserve permanent truth/security/runtime boundaries.

A Phase 12 pass does **not** mean every external source is healthy, all languages or regions are covered, production is live, public ingress is deployed, or outbound egress is restricted. Known limitations pass only when they are explicit, isolated, reproducible and prevented from becoming stronger factual/coverage/production claims.

## Gate Evidence Matrix

| Gate | Stored evidence | Validation state | P12.6 interpretation |
|---|---|---|---|
| P12.0 Canonical Convergence | `docs/implementation/P12_0_CANONICAL_CONVERGENCE_RESULT.md`; commit `374beb4664cd92a4f41063cbbe30f6830ee3a831`; CI `33517021594 / 99886494759`; `318 passed, 1 warning` | `P12_0_CANONICAL_CONVERGENCE_VALIDATED` | `PASS` — canonical architecture/security/integration/runtime/storage contracts converged before source-network expansion. |
| P12.1 Source Portfolio Contract | `docs/implementation/P12_1_SOURCE_PORTFOLIO_CONTRACT_RESULT.md`; commit `905a727d85701bf43d18de2d5216b83ab9a2b8bd`; CI `33520371480 / 99897786494`; `334 passed, 1 warning / SUCCESS` | `P12_1_SOURCE_PORTFOLIO_CONTRACT_VALIDATED` | `PASS` — immutable versioned governance, paid-provider separation, origin/independence isolation and exact outbound requirements are persisted without activating collection. |
| P12.2 Adapter Framework v2 | `docs/implementation/P12_2_LIVE_ADAPTER_FRAMEWORK_V2_RESULT.md`; validation commit `cb6866e82d5dc4a26042e0b9d08e9098aae10ecb`; CI `33523574819 / 99908604206`; `346 passed, 1 warning / SUCCESS` | `P12_2_ADAPTER_FRAMEWORK_V2_VALIDATED` | `PASS` — read-only HTTPS, deterministic RSS/Atom/JSON, exact adapter/version/host governance and source-failure isolation are fail-closed. |
| P12.3 Priority Authoritative Source Pack | `docs/implementation/P12_3_PRIORITY_AUTHORITATIVE_SOURCE_PACK_RESULT.md`; anchor `038122e44139d6ff23bc5d79bb50a8dee3c38cde`; x64 `33527433110 / 99921745359`; ARM64 `33527433197 / 99921746285`; controlled-live `33527433106 / 99921745640` | `P12_3_AUTHORITATIVE_SOURCE_PACK_VALIDATED` | `PASS_WITH_EXPLICIT_DEGRADATION` — European Parliament remains governed `DEGRADED`; unattended endpoint returns non-feed/anti-bot content and no bypass/mirror is authorized. |
| P12.4 Local-Language / Media Discovery | `docs/implementation/P12_4_LOCAL_LANGUAGE_MEDIA_DISCOVERY_PACK_RESULT.md`; anchor `595d7f0f0e6316e95aca518bb9309e615f239479`; x64 `33531518780 / 99935566406`; ARM64 `33531518525 / 99935564828`; controlled-live `33531518652 / 99935565895` | `P12_4_LOCAL_LANGUAGE_DISCOVERY_VALIDATED` | `PASS_WITH_SCOPE_LIMITATION` — `uk/ru/pl/tr` is a validated prioritized first slice, explicitly not global language coverage; translation stays derived and media/language count is not independent-origin count. |
| P12.5 Source Health / Freshness / Egress | `docs/implementation/P12_5_SOURCE_HEALTH_EGRESS_INVENTORY_RESULT.md`; anchor `92d0c0516351e2af7ba836d3ae711dd414d22023`; x64 `33533313297 / 99941475948`; ARM64 `33533313313 / 99941475266`; controlled-live `33533313654 / 99941475574`; final closure HEAD `248c38f02724f6e210850df56e96c95a97a14d53`, x64 `33545780300 / 99982787217`, ARM64 `33545780531 / 99982788149` | `P12_5_SOURCE_HEALTH_EGRESS_INVENTORY_VALIDATED` | `PASS_WITH_MEASURED_DEGRADATION` — 10/10 governed paths measured; 8 SUCCESS / 2 FAILED; EP `UNAVAILABLE/PARSER`, Haberturk `UNAVAILABLE/UNKNOWN`, OSCE acquisition healthy with stale observed content; ten HTTPS hosts inventoried without deploying an allowlist. |

## Cross-Cutting Validation Matrix

| Control | Required Phase 12 condition | Evidence / observed state | Candidate result |
|---|---|---|---|
| Canonical consistency | ROADMAP, architecture, security, integrations, source policy and data model agree on current phase/runtime/storage | P12.0 convergence plus P12.5 v4.6 closure state | `PASS` |
| Source governance | Every activated Phase 12 source path is governed; governance is versioned and immutable through service/SQL protections | P12.1 contract; P12.3/P12.4 governed packs; P12.5 baseline governance for controlled runtime | `PASS` |
| Adapter fail-closed behavior | Public anonymous paths require HTTPS, no credentials, exact adapter/version/host, bounded parsing/transport | P12.2 deterministic tests and later source-pack regressions | `PASS` |
| Failure isolation | One source failure cannot erase healthy-source collection or become a false event/coverage conclusion | P12.2 framework, P12.3 EP degradation, P12.5 8-success/2-failure measurement | `PASS` |
| Authoritative-source limitation | Official source status proves publication/statement, not automatically underlying event truth | P12.1-P12.5 permanent boundaries | `PASS` |
| Media provenance | Media publisher identity is not automatically underlying origin; translation/repost/citation do not create independence | P12.4 source policy/result and canonical truth boundaries | `PASS` |
| Language coverage | Initial language discovery must not be labeled global/exhaustive | P12.4 explicitly limits validated slice to `uk/ru/pl/tr` | `PASS_WITH_SCOPE_LIMITATION` |
| Operational health | Health/freshness must be measured separately from truth and governed availability | P12.5 separates portfolio state, acquisition state, measurement freshness and content freshness | `PASS_WITH_MEASURED_DEGRADATION` |
| Known source discrepancy | Governance-vs-observation differences must stay visible rather than be silently normalized | EP governed `DEGRADED` vs measured `UNAVAILABLE/PARSER`; Haberturk governed `ACTIVE` vs measured `UNAVAILABLE/UNKNOWN`; OSCE governed `ACTIVE`, acquisition `HEALTHY`, content `STALE` | `PASS_WITH_RECONCILIATION_ITEMS` |
| Egress inventory | Required outbound destinations/protocols must be known before any restriction decision | ten exact HTTPS hosts inventoried by P12.5 | `PASS` |
| Egress enforcement | P12.5/P12.6 must not pretend the inventory is already a firewall allowlist | broad outbound egress remains explicit owner-approved candidate exception | `PASS_WITH_SECURITY_EXCEPTION` |
| SSH boundary | Existing owner-approved candidate SSH exposure remains explicit | public SSH TCP/22 from `0.0.0.0/0` retained | `PASS_WITH_SECURITY_EXCEPTION` |
| Runtime storage | No implicit mixed/shared canonical storage | `Runtime storage mode: PROJECT_LOCAL_ONLY` | `PASS` |
| Production boundary | Phase 12 must not activate production/live | `Production/live operational status: NOT_OPERATIONAL` | `PASS` |
| Public exposure | No public KGM API/dashboard ingress or backend HTTPS deployment is implied | public ingress not approved/deployed; backend HTTPS not deployed; private GPT Action not connected | `PASS` |
| Paid providers | No paid provider activated by Phase 12 | `NONE_APPROVED` | `PASS` |
| Coverage epistemics | Scope/source counts/health do not prove exhaustive global coverage or raise factual confidence | permanent canonical coverage boundary retained | `PASS` |
| Phase sequencing | Phase 13 must not begin before P12.6 gate is validated/saved | Phase 13 remains `NOT_STARTED` at candidate creation | `PASS` |

## Known Limitations / Reconciliation Items

These items are not hidden by the candidate Phase 12 pass:

- European Parliament unattended RSS acquisition remains degraded/unavailable at the measured endpoint; no bypass or third-party canonical mirror is authorized.
- Haberturk had a P12.5 item URL validation failure (`original_url must be HTTP or HTTPS`) while its immutable governed portfolio state remained `ACTIVE`; this is a source/adapter/governance reconciliation item for subsequent explicit remediation, not a silent P12.5 rewrite.
- OSCE transport/acquisition succeeded while the latest observed publisher timestamp was stale; transport health and content freshness remain distinct.
- Consilium and European Commission produced successful zero-match bounded probes in P12.5; content freshness stayed `UNKNOWN` rather than inferred from collection time.
- The validated local-language slice is only `uk/ru/pl/tr`; important regions/languages and inaccessible, closed, deleted or not-yet-indexed sources remain outside proven coverage.
- Broad outbound egress and public SSH TCP/22 remain explicit owner-approved candidate exceptions. The ten-host inventory is not deployed enforcement.
- Controlled-live observations are point-in-time evidence, not continuous-uptime guarantees.

## Permanent Truth / Coverage Boundaries Verified

P12.6 requires all of the following to remain true:

- publisher/publication is not automatically the underlying origin;
- repost, syndication, translation and citation do not create independent corroboration;
- official-source status establishes institutional publication/statement, not automatically underlying-event truth;
- media/domain/language/adapter/item/host count is not independent-origin count;
- source reputation, portfolio approval, availability, health and freshness are not truth operators;
- graph inference and forecast probability cannot promote factual verification;
- coverage confidence cannot promote factual verification confidence;
- `GLOBAL` is scope, not proof of exhaustive world coverage;
- a failed source does not prove an event did not occur;
- a successful probe does not prove exhaustive coverage.

## Runtime / Security Boundaries Verified

- `Runtime storage mode: PROJECT_LOCAL_ONLY`;
- `Production/live operational status: NOT_OPERATIONAL`;
- shared/mixed canonical runtime storage remains blocked without new architecture approval;
- public KGM API/dashboard ingress remains not approved/deployed;
- backend HTTPS remains not deployed;
- private GPT backend Action remains not connected;
- paid providers remain `NONE_APPROVED`;
- public SSH TCP/22 from `0.0.0.0/0` remains an explicit owner-approved candidate exception;
- broad outbound egress remains an explicit owner-approved candidate exception;
- Start.me remains `PUBLIC_NON_SENSITIVE_ONLY` and non-canonical.

## Candidate Phase Decision

`PASS_WITH_KNOWN_LIMITATIONS`

This candidate decision means the **Phase 12 engineering foundation is internally coherent and validation-ready while retaining explicit external-source and security limitations**. It does not mean all sources are healthy, coverage is global/exhaustive, public/production operation is enabled, or security exceptions are remediated.

The target gate `PHASE_12_INTELLIGENCE_SOURCE_NETWORK_FOUNDATION_VALIDATED` remains `REGRESSION_PENDING` until this P12.6 matrix and deterministic guard pass full x64 and native ARM64 regression on the same candidate commit.

Phase 13 remains `NOT_STARTED` until the P12.6 result/checkpoint and canonical closure are saved and the final closure HEAD is green.
