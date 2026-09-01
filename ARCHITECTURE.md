# ARCHITECTURE
Technical architecture definition for K-Geopolitical Monitor.

Version: 3.1
Status: APPROVED / ROADMAP_V4_SYNCHRONIZED / P12_0_VALIDATED

## Purpose

Define the current system architecture, truth, storage, deployment, security and integration boundaries. Historical detail remains in `PROJECT_HISTORY.md`, accepted ADR/decision records and phase-specific implementation documents.

## Architecture Principle

Preserve the validated engineering spine while improving intelligence quality and source-network breadth.

Strategic sequence:
`ENGINEERING PLATFORM -> INTELLIGENCE QUALITY -> SOURCE NETWORK -> OWNER OPERATIONALIZATION -> FORECAST CALIBRATION -> DELIVERY / QUALITY FEEDBACK -> OPTIONAL PUBLICATION -> OPTIONAL SHARED RUNTIME`

Current numbered phase:
`Phase 12 — Intelligence Quality and Source Network Foundation`

P12.0 gate:
`P12_0_CANONICAL_CONVERGENCE_VALIDATED`

Next activity:
`P12.1_SOURCE_PORTFOLIO_CONTRACT_AND_GOVERNANCE / NEXT_NOT_STARTED`

No M14 is created.

## Logical Architecture

`Public Sources -> Source Portfolio / Adapters -> Acquisition -> Ingestion -> Translation Representation -> Normalization -> Claims / Evidence / Events -> Verification -> Analysis / Graph -> Forecasting -> Reporting -> Monitoring / Coverage / Alerts -> Owner Interaction`

The private GPT is an interaction/orchestration surface. It is not the unattended monitoring host, canonical runtime store, or substitute for persisted backend state.

## Validated Engineering Baseline

Validated foundations include persistence/provenance, claims/evidence/events, verification baseline, project-local monitoring, controlled read-only live acquisition, underlying-origin-aware evidence rules, region/language coverage, geopolitical graph, forecasting/scenario persistence, immutable reporting, owner-only private GPT truth-boundary pilot, E1 translation, E2 source reputation history, E3 read-only persisted-state API foundation, E4 real OCI ARM64 runtime, E5 read-only admin dashboard foundation, E6 reproducibility instrumentation, E7 forecast semantics and E9A owner-only runtime hardening.

This is an engineering foundation, not proof of exhaustive global coverage or production/live operation.

## Runtime / Storage Boundary

The approved architecture remains HYBRID with project-specific canonical truth kept project-local.

Mandatory rules:
- runtime storage is `PROJECT_LOCAL_ONLY`;
- no implicit mixed storage;
- no shared runtime database;
- no direct cross-project canonical-store mutation;
- cross-project exchange requires an explicit versioned contract/export/API;
- shared/mixed canonical runtime storage requires a new architecture approval.

`E9 Shared Production Runtime = NOT_APPROVED`.

## Owner-Only Runtime Boundary

E9A state:
`OWNER_ONLY_PRODUCTION_CANDIDATE_READY / COMPLETE`.

Validated properties include dedicated non-login `kgm`, root-owned code/service definition, application write access limited to `/opt/k-geopolitical-monitor/data`, hardened systemd sandbox/no capabilities, fail-closed second-instance lease, restart/reboot recovery, interrupted-run recovery, due-watch resumption, clean project-local backup/restore drill, journal secret-pattern review, no KGM public HTTP/HTTPS/database/API listener, and persistent removal of rpcbind TCP/UDP port 111.

Remaining explicit owner-approved candidate networking exceptions:
- public SSH TCP/22 from `0.0.0.0/0`;
- broad outbound egress.

These are not final least-privilege production networking.

`PRODUCTION_LIVE = NOT_OPERATIONAL`.

## External Integration Boundary

Validated starting live integrations:
- Consilium press-release RSS — public read-only official-source acquisition;
- GDELT DOC 2.0 — public read-only discovery/index metadata.

GDELT discovery does not itself provide independent factual corroboration of linked publisher claims.

Phase 12 rules:
- prefer public/free sources first;
- every source/integration requires an explicit record;
- adapter/domain count does not establish underlying-origin independence;
- transport remains read-only/fail-closed;
- one source failure must not corrupt/block another source;
- deterministic CI must not depend on live network availability;
- required outbound domains/protocols are inventoried before egress restriction;
- no paid provider is activated by Phase 12 alone.

P12.0 activated no new sources. P12.1 is the next, not-yet-started source-portfolio contract gate.

No public backend/API/dashboard, notification provider, public GPT Action or external canonical store is approved by Phase 12.

## Verification / Truth Boundary

Permanent rules:
- publisher/publication is not automatically the underlying origin;
- repost, syndication, translation and citation do not create independent corroboration;
- an official statement establishes that an actor said something, not automatically that the asserted event occurred;
- source reputation/status is context, not an automatic truth/falsehood operator;
- graph inference cannot promote factual verification or independent-origin count;
- forecast probability/confidence cannot promote factual verification;
- coverage confidence cannot promote factual verification confidence;
- report rendering cannot strengthen upstream evidence;
- `GLOBAL` is scope, not proof of exhaustive global coverage;
- missing local-language evidence remains explicit;
- reconstructed/uninstrumented history must not be labeled exact;
- unavailable persisted backend state must not be replaced by ad hoc public-web research;
- runtime-health instrumentation cannot imply unavailable coverage/source-health/uptime/verification/production facts.

The richer semantic verification/provenance system remains planned for Phase 13 and is not back-claimed here.

## Forecast / Coverage Boundary

`raw_probability`, `calibrated_probability` and `scenario_confidence` remain distinct forecast semantics. Forecasts are analytical assessments, not facts.

`coverage_ratio` measures satisfied configured requirements; `coverage_confidence` measures how much required scope has a known assessment state. Neither proves universal completeness or strengthens factual verification.

## Backend / Dashboard / GPT Boundary

- E3 read-only backend API foundation: `BASELINE_VALIDATED / NOT_DEPLOYED_HTTPS`;
- private GPT backend Action: `NOT_CONNECTED`;
- E5 admin dashboard: `LOCAL_PROTECTED / READ_ONLY / NOT_DEPLOYED`;
- public Action/API/dashboard ingress: `NOT_APPROVED / NOT_DEPLOYED`;
- GPT public sharing: `USER_DEFERRED_UNTIL_SEPARATE_REQUEST`.

## Start.me Boundary

`START_ME_DATA_POLICY = PUBLIC_NON_SENSITIVE_ONLY`.

Start.me is non-canonical and may hold only public, non-sensitive navigation material. It cannot hold credentials, private endpoints, canonical runtime/monitoring state, private findings/alerts, sensitive data or canonical evidence/provenance/coverage authority.

## Current State

- ROADMAP: `APPROVED / v4.0`;
- Phase 0-11 engineering line: validated baseline;
- E1-E7: validated baselines;
- E8: user-deferred;
- E9A: `OWNER_ONLY_PRODUCTION_CANDIDATE_READY / COMPLETE`;
- E9: `NOT_APPROVED`;
- runtime storage: `PROJECT_LOCAL_ONLY`;
- mixed/shared canonical storage: blocked pending new architecture approval;
- controlled-live starting integrations: Consilium RSS + GDELT DOC 2.0;
- P12.0: `VALIDATED`;
- current/next engineering activity: `PHASE_12 / P12.1_SOURCE_PORTFOLIO_CONTRACT_AND_GOVERNANCE / NEXT_NOT_STARTED`;
- production/live: `NOT_OPERATIONAL`.
