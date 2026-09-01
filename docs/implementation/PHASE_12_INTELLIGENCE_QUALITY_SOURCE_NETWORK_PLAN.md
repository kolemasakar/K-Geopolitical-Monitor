# Phase 12 — Intelligence Quality and Source Network Foundation Plan

Date: 2026-09-01
Status: `APPROVED_FOR_IMPLEMENTATION / P12_3_VALIDATED`
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
- publisher is not automatically underlying origin;
- translation remains derived;
- source failures/degradation remain isolated and visible;
- deterministic CI must not depend on live networks;
- coverage does not prove universal completeness;
- broad egress remains an explicit exception until P12.5 inventory is validated.

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
Implementation: `docs/implementation/P12_3_PRIORITY_AUTHORITATIVE_SOURCE_PACK.md`
Result: `docs/implementation/P12_3_PRIORITY_AUTHORITATIVE_SOURCE_PACK_RESULT.md`
Controlled-live matrix: `docs/implementation/P12_3_CONTROLLED_LIVE_SOURCE_MATRIX.md`
Checkpoint: `docs/checkpoints/PROJECT_CHECKPOINT_2026-09-01_P12_3_AUTHORITATIVE_SOURCE_PACK_VALIDATED.md`

Validation anchor `038122e44139d6ff23bc5d79bb50a8dee3c38cde`:
- x64 CI `33527433110`, job `99921745359`: `356 passed, 1 warning / SUCCESS`;
- native ARM64 `33527433197`, job `99921746285`: `356 passed, 1 warning / SUCCESS`;
- controlled-live repeat `33527433106`, job `99921745640`: 3 `SUCCESS`, European Parliament `DEGRADED`, failure isolation PASS.

Validated pack states:
- European Commission Press Corner `ACTIVE`;
- European Parliament Press Releases `DEGRADED` for unattended RSS because the official endpoint returns anti-bot HTML;
- UK Government News and Communications `ACTIVE`;
- OSCE Latest News `ACTIVE`.

The official European Parliament endpoint is retained. No anti-bot bypass or third-party canonical mirror substitution is authorized.

## P12.4 — Local-Language and Media Discovery Pack

State: `NEXT / NOT_STARTED`

Expand priority region/language discovery while preserving local-language gaps, translation isolation, discovery-vs-evidence roles and underlying-origin uncertainty.

Requirements:
- explicit prioritized region/language scope;
- public/free-first discovery sources;
- P12.1 portfolio/integration governance for each source;
- P12.2-compatible adapters and deterministic fixtures;
- original-language identity retained; translation remains derived;
- discovery/index/media publisher count never becomes independent-origin count;
- local-language gaps and unavailable sources remain explicit;
- no discovery source may directly promote verification.

Gate:
`P12_4_LOCAL_LANGUAGE_DISCOVERY_VALIDATED`

## P12.5 — Source Health and Egress Inventory
State: `PLANNED`
Gate: `P12_5_SOURCE_HEALTH_EGRESS_INVENTORY_VALIDATED`

## P12.6 — Phase 12 Validation Matrix
State: `PLANNED`
Phase gate: `PHASE_12_INTELLIGENCE_SOURCE_NETWORK_FOUNDATION_VALIDATED`

## Explicit Non-Goals

Phase 12 does not implement Phase 13 semantic verification v2, deploy public API/dashboard, connect public GPT Action, activate public sharing/Business migration, enable shared/team runtime, replace SQLite without measured need, activate a paid provider without separate approval, claim complete global coverage or set `PRODUCTION_LIVE = OPERATIONAL`.

## Start.me Boundary

`START_ME_DATA_POLICY = PUBLIC_NON_SENSITIVE_ONLY`.
Start.me remains non-canonical and may contain only public, non-sensitive navigation/source material.

## Exact Start Point

Next engineering activity:
`P12.4_LOCAL_LANGUAGE_AND_MEDIA_DISCOVERY_PACK`

P12.5 does not begin until P12.4 is validated and saved to canonical state.
