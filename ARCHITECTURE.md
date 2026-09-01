# ARCHITECTURE
Technical architecture definition for K-Geopolitical Monitor.

Version: 3.0
Status: APPROVED / ROADMAP_V4_SYNCHRONIZED

## Purpose

Define the current system architecture, truth, storage, deployment, security and integration boundaries.

Historical implementation detail remains in `PROJECT_HISTORY.md`, accepted ADR/decision records and phase-specific implementation documents. Historical decisions are not rewritten by this current-state architecture view.

## Current Architecture Principle

Preserve the validated engineering spine while improving intelligence quality and source-network breadth.

ROADMAP v4 strategic sequence:

`ENGINEERING PLATFORM -> INTELLIGENCE QUALITY -> SOURCE NETWORK -> OWNER OPERATIONALIZATION -> FORECAST CALIBRATION -> DELIVERY / QUALITY FEEDBACK -> OPTIONAL PUBLICATION -> OPTIONAL SHARED RUNTIME`

Current numbered engineering phase:

`Phase 12 — Intelligence Quality and Source Network Foundation`

Current sub-gate:

`P12.0_CANONICAL_ARCHITECTURE_SECURITY_INTEGRATION_CONVERGENCE`

No M14 is created.

## Logical Architecture

`Public Sources -> Source Portfolio / Adapters -> Acquisition -> Ingestion -> Translation Representation -> Normalization -> Claims / Evidence / Events -> Verification -> Analysis / Graph -> Forecasting -> Reporting -> Monitoring / Coverage / Alerts -> Owner Interaction`

The private GPT is an interaction/orchestration surface. It is not the unattended monitoring host, the canonical runtime store, or a substitute for persisted backend state.

## Validated Engineering Baseline

Validated foundations include:
- persistence, provenance, evidence, claims/events and verification baseline;
- project-local monitoring watches/runs, retry/recovery, findings and strategic alerts;
- controlled read-only live source acquisition with source-failure isolation;
- underlying-origin-aware evidence independence rules;
- region/language scope and explicit coverage measurement;
- durable geopolitical graph identity/history/query substrate;
- durable forecasting/scenario identity, versions, provenance, outcomes/evaluations and calibration history;
- immutable report snapshots and deterministic structured/Markdown rendering;
- owner-only private GPT truth-boundary pilot: `18/18 PASS`;
- E1 translation foundation;
- E2 append-only source reputation/status history;
- E3 owner-only read-only persisted-state API foundation;
- E4 real OCI Ubuntu 24.04 ARM64 unattended runtime;
- E5 owner/admin read-only dashboard foundation;
- E6 reproducibility instrumentation and persisted artifact hashing;
- E7 forecast probability semantic contract;
- E9A owner-only runtime hardening, backup/DR, runtime health, systemd security and real-host recovery validation.

This baseline is an engineering foundation. It does not establish exhaustive global coverage or production/live operation.

## Runtime / Storage Boundary

The approved architecture remains HYBRID with project-specific canonical truth kept project-local.

Mandatory current rules:
- runtime storage is `PROJECT_LOCAL_ONLY`;
- no implicit mixed storage;
- no shared runtime database;
- no direct cross-project canonical-store mutation;
- cross-project exchange requires an explicit versioned contract/export/API;
- shared/mixed canonical runtime storage requires a new architecture approval.

`E9 Shared Production Runtime = NOT_APPROVED`.

## Owner-Only Runtime Boundary

E9A is complete at the engineering candidate gate:

`OWNER_ONLY_PRODUCTION_CANDIDATE_READY = ESTABLISHED`

Validated real-host properties include:
- dedicated non-login `kgm` runtime identity;
- root-owned code/service definition;
- application write access limited to `/opt/k-geopolitical-monitor/data`;
- hardened systemd sandbox and no service capabilities;
- second-instance fail-closed lease behavior;
- restart and physical reboot recovery;
- interrupted-run recovery and due-watch resumption;
- clean project-local backup/restore drill;
- journal secret-pattern review with zero detected hits in the validated drill;
- no KGM HTTP/HTTPS/database/API public listener;
- rpcbind TCP/UDP port 111 removed and persistent closure validated after reboot.

Remaining explicit owner-approved candidate security exceptions:
- public SSH TCP/22 from `0.0.0.0/0`;
- broad outbound egress.

These are exceptions, not least-privilege production networking.

`PRODUCTION_LIVE = NOT_OPERATIONAL`.

## External Integration Boundary

Validated starting live integration baseline:
- Consilium press-release RSS — public read-only official-source acquisition;
- GDELT DOC 2.0 — public read-only discovery/index metadata.

GDELT discovery does not itself provide independent factual corroboration of linked publisher claims.

Phase 12 expands the public-source network under these rules:
- public/free sources are preferred first;
- every new source/integration requires an explicit integration/source record;
- adapter identity and domain count do not establish underlying-origin independence;
- transport remains read-only and fail-closed;
- one source failure must not corrupt/block another source;
- deterministic CI must not depend on live network availability;
- actual required outbound domains/protocols are inventoried before egress restriction is proposed;
- no paid provider is activated by ROADMAP v4 or Phase 12 alone.

No public backend/API/dashboard, notification provider, public GPT Action or external canonical store is approved by Phase 12.

## Verification / Truth Boundary

Permanent rules:
- publisher/publication is not automatically the underlying origin;
- repost, syndication, translation and citation do not create independent corroboration;
- an official statement establishes that an actor said something, not automatically that the asserted event occurred;
- source reputation/status is context, not an automatic truth/falsehood operator;
- graph inference cannot promote factual verification or independent-origin count;
- forecast probability/confidence cannot promote present-tense factual verification;
- coverage confidence cannot promote factual verification confidence;
- report rendering cannot strengthen upstream evidence;
- `GLOBAL` is an intended scope key, not proof of exhaustive global coverage;
- missing local-language evidence remains an explicit coverage limitation;
- reconstructed/uninstrumented search or tool history must not be labeled exact;
- unavailable persisted backend state must not be replaced by ad hoc public-web research;
- runtime-health instrumentation cannot imply unavailable coverage, source-health, uptime, verification or production facts.

The current executable live verification/claim layer remains a baseline and is intentionally not represented as the richer semantic verification system planned for Phase 13.

## Forecast Boundary

Canonical semantic separation remains:
- `raw_probability` — pre-calibration analytical scenario probability;
- `calibrated_probability` — calibrated analytical scenario probability;
- `scenario_confidence` — confidence in assessment quality/stability, not probability.

Forecasts are analytical assessments, not facts. Forecast metrics cannot alter factual verification state or evidence independence.

## Coverage Boundary

Phase 11 coverage dimensions remain explicit and project-defined. `coverage_ratio` measures satisfied configured requirements; `coverage_confidence` measures how much of the required scope has a known assessment state. Neither proves universal completeness or strengthens factual verification.

## Backend / Dashboard / GPT Boundary

- E3 read-only backend Action API foundation: `BASELINE_VALIDATED / NOT_DEPLOYED_HTTPS`;
- private GPT backend Action connection: `NOT_CONNECTED`;
- E5 admin dashboard: `LOCAL_PROTECTED / READ_ONLY / NOT_DEPLOYED`;
- public Action/API/dashboard ingress: `NOT_APPROVED / NOT_DEPLOYED`;
- GPT publication/public sharing: `USER_DEFERRED_UNTIL_SEPARATE_REQUEST`.

## Start.me Boundary

`START_ME_DATA_POLICY = PUBLIC_NON_SENSITIVE_ONLY`.

Start.me may be used only as a non-canonical navigation/operator surface for public URLs, RSS feeds, public source names/classes and public analytical resources. It cannot hold credentials, private endpoints, canonical runtime/monitoring state, private findings/alerts, sensitive data, or canonical evidence/provenance/coverage authority.

## ROADMAP v4 Boundary

Approved sequential phases:
- Phase 12 — Intelligence Quality and Source Network Foundation;
- Phase 13 — Semantic Verification and Provenance Intelligence;
- Phase 14 — Owner Operational Intelligence Activation;
- Phase 15 — Forecast Calibration and Performance Intelligence;
- Phase 16 — Delivery, Operator Experience and Quality Feedback.

Conditional only:
- Phase 17 external publication readiness — not activated;
- Phase 18 shared/team runtime — new architecture approval required.

Phase 12 does not activate production/live, public publication, Business migration, public ingress, shared runtime/storage, paid providers or external notification providers.

## Current State

- ROADMAP: `APPROVED / v4.0`;
- Phase 0-11 engineering line: validated baseline;
- E1-E7: validated baselines;
- E8: user-deferred;
- E9A: `OWNER_ONLY_PRODUCTION_CANDIDATE_READY / COMPLETE`;
- E9: `NOT_APPROVED`;
- runtime storage: `PROJECT_LOCAL_ONLY`;
- mixed/shared canonical storage: blocked pending new architecture approval;
- controlled live starting integrations: Consilium RSS + GDELT DOC 2.0;
- current engineering activity: `PHASE_12 / P12.0_CANONICAL_ARCHITECTURE_SECURITY_INTEGRATION_CONVERGENCE`;
- production/live: `NOT_OPERATIONAL`.
