# Phase 12 — Intelligence Quality and Source Network Foundation Plan

Date: 2026-09-01
Status: `APPROVED_FOR_IMPLEMENTATION / P12_5_VALIDATED`
Project: K-Geopolitical Monitor
Roadmap: `ROADMAP.md / v4`

## Objective

Build a materially broader, measurable and maintainable public-source network without weakening provenance/verification/coverage boundaries or claiming exhaustive global monitoring.

Phase 12 does not activate production/live, public publication, shared runtime or paid providers by itself.

## Design Rules

- canonical runtime storage remains `PROJECT_LOCAL_ONLY`;
- prefer public/free sources first;
- every external source requires explicit governance;
- source/domain/adapter/item identity is not evidentiary independence;
- media/domain/language/adapter/item count is not independent-origin count;
- publisher is not automatically underlying origin;
- translation remains derived;
- governed portfolio state and latest measured operational state remain separate;
- source failures/degradation/staleness remain isolated and visible;
- deterministic CI must not depend on live networks;
- coverage does not prove universal completeness;
- measured egress inventory does not itself deploy an outbound restriction.

## P12.0 — Canonical Convergence
State: `VALIDATED`
Gate: `P12_0_CANONICAL_CONVERGENCE_VALIDATED`

## P12.1 — Source Portfolio Contract and Governance
State: `VALIDATED`
Gate: `P12_1_SOURCE_PORTFOLIO_CONTRACT_VALIDATED`

## P12.2 — Live Adapter Framework v2
State: `VALIDATED`
Gate: `P12_2_ADAPTER_FRAMEWORK_V2_VALIDATED`

## P12.3 — Priority Authoritative Source Pack
State: `VALIDATED_WITH_EXPLICIT_DEGRADATION`
Gate: `P12_3_AUTHORITATIVE_SOURCE_PACK_VALIDATED`

European Parliament remains explicitly governed `DEGRADED`; no anti-bot bypass or third-party canonical mirror substitution is authorized.

## P12.4 — Local-Language and Media Discovery Pack

State: `VALIDATED`
Gate: `P12_4_LOCAL_LANGUAGE_DISCOVERY_VALIDATED`
Implementation: `docs/implementation/P12_4_LOCAL_LANGUAGE_MEDIA_DISCOVERY_PACK.md`
Result: `docs/implementation/P12_4_LOCAL_LANGUAGE_MEDIA_DISCOVERY_PACK_RESULT.md`
Controlled-live matrix: `docs/implementation/P12_4_CONTROLLED_LIVE_LANGUAGE_SOURCE_MATRIX.md`
Checkpoint: `docs/checkpoints/PROJECT_CHECKPOINT_2026-09-01_P12_4_LOCAL_LANGUAGE_DISCOVERY_VALIDATED.md`

Validation anchor `595d7f0f0e6316e95aca518bb9309e615f239479`:
- x64 CI `33531518780`, job `99935566406`: `370 passed, 1 warning / SUCCESS`;
- native ARM64 `33531518525`, job `99935564828`: real `aarch64`, `370 passed, 1 warning / SUCCESS`, bootstrap/unattended/systemd PASS;
- controlled-live `33531518652`, job `99935565895`: `4 SUCCESS / 0 FAILED`.

Governed initial slice:
- `uk` / Ukrainska Pravda / `ACTIVE`;
- `ru` / Meduza / `ACTIVE`;
- `pl` / RMF24 / `ACTIVE`;
- `tr` / Haberturk / `ACTIVE`.

Validated P12.4 requirements:
- explicit prioritized region/language scope;
- public/free-first media discovery sources;
- P12.1 governance for every source;
- P12.2-compatible adapters and deterministic fixtures;
- original-language identity retained;
- translation remains a separate derived representation;
- media/language/source count never becomes independent-origin count;
- local-language gaps remain explicit;
- discovery sources cannot directly promote verification;
- source-specific failures remain isolated.

The `uk/ru/pl/tr` slice is a prioritized starting slice only and is not global language coverage.

## P12.5 — Source Health and Egress Inventory

State: `VALIDATED_WITH_MEASURED_DEGRADATION`
Gate: `P12_5_SOURCE_HEALTH_EGRESS_INVENTORY_VALIDATED`
Implementation: `docs/implementation/P12_5_SOURCE_HEALTH_EGRESS_INVENTORY.md`
Result: `docs/implementation/P12_5_SOURCE_HEALTH_EGRESS_INVENTORY_RESULT.md`
Controlled-live matrix: `docs/implementation/P12_5_CONTROLLED_LIVE_SOURCE_HEALTH_MATRIX.md`
Checkpoint: `docs/checkpoints/PROJECT_CHECKPOINT_2026-09-01_P12_5_SOURCE_HEALTH_EGRESS_VALIDATED.md`
Validation anchor: `92d0c0516351e2af7ba836d3ae711dd414d22023`.

Validation evidence:
- x64 CI `33533313297`, job `99941475948`: `382 passed, 1 warning / SUCCESS`;
- native ARM64 `33533313313`, job `99941475266`: real `aarch64`, `382 passed, 1 warning / SUCCESS`, bootstrap/unattended/systemd PASS;
- controlled-live `33533313654`, job `99941475574`: workflow `SUCCESS`, all `10/10` governed paths measured, `8 SUCCESS / 2 FAILED`, ten HTTPS egress entries.

Validated P12.5 requirements:
- source-by-source health state grounded in persisted controlled observations;
- measurement freshness tied to portfolio cadence/freshness expectations;
- observed publisher-content freshness kept separate from transport health;
- parser/transport/governance/unknown errors kept distinct;
- actual outbound hostname/protocol inventory produced for all measured adapters;
- no health claim for unmeasured sources (`0` unmeasured in validation);
- degradation/unavailable/stale state does not promote or demote factual verification;
- inventory precedes any egress-restriction decision.

Measured findings retained for P12.6:
- European Parliament — latest measured state `UNAVAILABLE / PARSER`, governed state `DEGRADED`;
- Haberturk — latest measured state `UNAVAILABLE / UNKNOWN`, governed state `ACTIVE`; discrepancy requires explicit review rather than automatic portfolio mutation;
- OSCE — acquisition `HEALTHY`, observed content `STALE`;
- Consilium and European Commission — successful zero-match collection, content freshness `UNKNOWN` rather than inferred.

P12.5 did not deploy a firewall allowlist or otherwise restrict broad outbound egress.

## P12.6 — Phase 12 Validation Matrix
State: `NEXT / NOT_STARTED`
Current activity: `P12.6_PHASE_12_VALIDATION_MATRIX`
Phase gate: `PHASE_12_INTELLIGENCE_SOURCE_NETWORK_FOUNDATION_VALIDATED`

P12.6 must validate the complete P12.0-P12.5 chain and explicitly reconcile:
- canonical architecture/security/integration consistency;
- P12.1 immutable source governance;
- P12.2 fail-closed adapter behavior;
- P12.3 retained authoritative-source degradation;
- P12.4 language/media scope and explicit non-global coverage gap;
- P12.5 measured health/freshness/egress facts, including portfolio-vs-observation discrepancies;
- runtime/storage/public-exposure/paid-provider boundaries;
- truth/provenance/independence/coverage boundaries.

P12.6 must not declare Phase 12 validated if these facts are hidden, silently normalized away or promoted into stronger truth/production claims.

## Explicit Non-Goals

Phase 12 does not implement Phase 13 semantic verification v2, deploy public API/dashboard, connect public GPT Action, activate public sharing/Business migration, enable shared/team runtime, replace SQLite without measured need, activate a paid provider without separate approval, claim complete global coverage or set `PRODUCTION_LIVE = OPERATIONAL`.

## Start.me Boundary

`START_ME_DATA_POLICY = PUBLIC_NON_SENSITIVE_ONLY`.
Start.me remains non-canonical and may contain only public, non-sensitive navigation/source material.

## Exact Start Point

Next engineering activity:
`P12.6_PHASE_12_VALIDATION_MATRIX`

P12.6 starts only after the P12.5 closure commit has passed final x64 and native ARM64 regression validation.
