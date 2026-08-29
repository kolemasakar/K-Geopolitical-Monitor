# ARCHITECTURE
Technical architecture definition for K-Geopolitical Monitor.

Version: 2.8
Status: APPROVED

## Purpose

Define the current system architecture, truth, storage, deployment and integration boundaries.

## Architecture Principle

Minimal Functional Core before global expansion.

## Logical Layers

Sources -> Live/Controlled Acquisition -> Ingestion -> Translation Representation -> Normalization -> Event Processing -> Verification -> Analysis -> Forecasting -> Reporting -> Operational Monitoring -> Coverage -> Strategic Alerts -> Region/Language Scope -> Advanced Geopolitical Graph -> Advanced Forecasting -> Full Reporting Environment -> Global Operational Coverage -> User Interaction/Orchestration

The private GPT is a user interaction/orchestration surface over validated analytical behavior. It is not the unattended monitoring host, canonical runtime store or source of persisted backend state.

## Core Components

- Source Registry
- Controlled Pilot Source Adapter
- Live Public-Source Adapters
- Source Collection Audit
- Ingestion Layer
- Provider-Neutral Translation Foundation
- Source Reputation and Status History
- Event Processing Layer
- Verification Engine
- Relationship Analysis Layer
- Forecasting Layer
- Reporting Layer
- Operational Monitoring Runtime
- Operational Intelligence Output
- Pilot Coverage Reporting
- Live End-to-End Analysis
- Strategic Alert Layer
- Region/Language Coverage Layer
- Advanced Geopolitical Graph
- Advanced Forecasting
- Full Reporting Environment
- Global Operational Coverage
- Unattended Monitoring Supervisor
- Cadence-Safe Live Operational Cycle
- Private GPT Interaction/Orchestration Surface
- Owner-Only Read-Only Backend Action API Foundation
- Admin Read-Only Dashboard
- Reproducibility Instrumentation
- Forecast Probability Semantic Contract

## Implemented and Validated Baseline

Validated foundations include:
- persistence, evidence, verification and event intelligence;
- project-local operational monitoring, retry/recovery and ranked findings;
- controlled/live read-only acquisition with provenance and source-failure isolation;
- original-origin M8 evidence independence;
- strategic alert policies/lifecycle and priority/cadence separation;
- watch-scoped region/language attribution and coverage reporting;
- durable advanced graph identity, projection, lifecycle, history, temporal/causal traversal and explainable queries;
- durable advanced forecasting identity, immutable scenario versions, typed provenance, outcome evaluation, calibration history and explainable queries;
- durable immutable report snapshots, sections and typed references;
- one common report assembler with deterministic structured and Markdown rendering;
- durable operational coverage contracts, requirements, immutable snapshots and per-requirement results;
- owner-only private GPT behavior validated across 18 truth-boundary scenarios;
- E1 provider-neutral translation persistence and origin isolation;
- E2 append-only source reputation/status history;
- E3 owner-only read-only FastAPI backend state facade with bearer authentication and read-only project-local SQLite;
- E4 owner-only OCI Ubuntu 24.04 ARM64 unattended runtime validated on a real host;
- E5 owner/admin-only read-only dashboard with no parallel database;
- E6 durable reproducibility instrumentation and persisted artifact hashing;
- E7 canonical machine-readable forecast semantic contract across API/dashboard/report surfaces.

These components form a controlled project-local validated engineering baseline. They do not imply public production maturity or universal global coverage.

## Runtime and Shared Infrastructure Boundary

The approved Shared Infrastructure ADR requires:
- HYBRID architecture;
- project-specific domain logic and canonical stores remain local;
- runtime storage remains `PROJECT_LOCAL_ONLY`;
- no implicit mixed storage;
- no shared runtime database;
- no direct cross-project canonical-store mutation;
- any future shared runtime storage requires a new explicit architecture approval.

Production/shared runtime remains NOT_APPROVED.

## External Integration Boundary

Approved controlled-pilot integrations:
- Consilium press-release RSS: official source discovery/collection;
- GDELT DOC 2.0 API: structured discovery/index metadata.

Both are read-only. GDELT metadata is discovery/index evidence only; original publishers or primary sources remain the factual Source of Truth for linked content.

External-source failures fail closed at the affected adapter and remain visible in collection audit/attempt state. Deterministic CI does not depend on live network availability.

No external translation, graph, forecasting, reporting/publishing, coverage, notification or production/global provider is approved at this checkpoint.

## Verification Boundary

- adapter identity does not establish evidence independence;
- original publisher/underlying origin is the baseline independence unit;
- same-origin duplicate observations must not increase verification status;
- syndication, reposting and translation do not create new independent origins;
- an official source is authoritative for its own statement but is not automatically independent corroboration of its own substantive claim;
- COMPROMISED source status changes verification burden but is not an automatic FALSE operator;
- graph intelligence, forecast outputs, coverage metrics and report presentation must not increase evidence confidence or independent-origin count;
- user demand for certainty does not create evidentiary certainty;
- public-web research cannot substitute for unavailable persisted backend state.

## E1 Translation Foundation Boundary

E1 is BASELINE_VALIDATED.

- `raw_item_translations` stores versioned derived translations while original raw-item text remains unchanged;
- source/target language, method/provider/version, status, uncertainty/error and origin linkage are explicit;
- translation inherits the same underlying origin and cannot create independent-source credit;
- translation cannot modify M8 verification state, graph evidence, forecast factual confidence, coverage confidence or report truth;
- external translation provider: NONE_APPROVED.

Validation: run `33244484173`, 241 passed.

## E2 Source Reputation Boundary

E2 is BASELINE_VALIDATED.

- `source_reputation_history` is append-only and versioned;
- status, reliability rating, reason, evidence references, policy/version and review/restoration lineage remain explicit;
- COMPROMISED is not automatic FALSE;
- source reputation/status does not modify claim truth or independent-origin count.

Validation: run `33244795277`, 248 passed.

## Advanced Geopolitical Graph Boundary

M11 provides one durable project-local graph contract.
- canonical project objects remain Source of Truth;
- graph inference is not source evidence;
- graph confidence does not modify M8 confidence or independent-origin count;
- graph operations do not automatically assign VERIFIED;
- external graph provider: NONE_APPROVED.

## Advanced Forecasting and E7 Semantic Boundary

M12 extends the existing forecasting/calibration/history stack rather than creating a parallel stack.

Persisted scenario semantics:
- `raw_probability`: analytical scenario probability before calibration;
- `calibrated_probability`: calibrated analytical scenario probability;
- `scenario_confidence`: confidence in the quality/stability of the scenario assessment, not probability.

E7 adds canonical contract `KGM_FORECAST_SEMANTICS_V1` and validates these semantics across API, dashboard, structured reports and Markdown.

Mandatory isolation:
- forecast probabilities are not facts;
- calibrated probability is not verification confidence;
- scenario confidence is not scenario probability;
- forecast metrics cannot modify verification state, factual/evidence confidence or independent-origin count;
- forecasting cannot mutate M11 graph truth;
- external forecasting provider: NONE_APPROVED.

E7 canonical validation at SHA `72f049b30fcaa3711c7712c8df7d1da1f934f650`:
- x64 run `33265984585`: 294 passed;
- native ARM64 run `33265984622`: 294 passed; aarch64/bootstrap/one-tick/systemd PASS.

## Full Reporting Environment Boundary

M13 provides one canonical presentation subsystem over existing validated state.
- report snapshots/sections/references remain immutable and typed;
- observed facts, verification state, analytical context, graph inference, forecast scenarios, assumptions and coverage remain distinguishable;
- rendering cannot modify upstream truth;
- structured and Markdown representations derive from the same persisted report snapshot;
- external reporting/publishing provider: NONE_APPROVED.

## Global Operational Coverage Boundary

Phase 11 provides a coverage-measurement layer, not a verification engine.

Baseline dimensions:
- SOURCE_CLASS;
- SOURCE_ID / SOURCE_AVAILABILITY;
- REGION_LANGUAGE;
- FRESHNESS.

Statuses:
- SATISFIED;
- GAP;
- UNAVAILABLE;
- STALE;
- UNKNOWN;
- UNMEASURED.

Semantics:
- `coverage_ratio` measures satisfied required units / required units;
- `coverage_confidence` measures known assessment states / required units;
- coverage confidence is not factual verification confidence;
- GLOBAL is an explicit scope key, not a universal-completeness claim;
- external coverage provider: NONE_APPROVED.

## E3 Private GPT Backend Action API Boundary

E3 is BASELINE_VALIDATED as a local owner-only read-only API foundation.

Rules:
- bearer token is injected at runtime and not persisted in repository state;
- project-local SQLite is opened read-only/query-only;
- invalid/missing bearer credentials fail with HTTP 401;
- `/health` remains separately accessible;
- GET endpoints must not mutate canonical project state;
- unavailable persisted state is returned explicitly and never replaced with current web research;
- direct database exposure is forbidden;
- HTTPS is required before a GPT Action connection is approved.

Current state:
- Backend Action API foundation: VALIDATED_LOCAL_READ_ONLY;
- HTTPS deployment: NOT_DEPLOYED;
- private GPT Action connection: NOT_CONNECTED.

Validation: run `33247311921`, 254 passed.

## E4 Unattended Runtime Boundary

E4 is `BASELINE_VALIDATED_WITH_TEMPORARY_SECURITY_EXCEPTION`.

Validated real-host state:
- Oracle OCI Ubuntu 24.04 ARM64 owner-only VM;
- immutable deployment/bootstrap and project-local DB integrity;
- systemd enable/start and real reboot auto-recovery;
- interrupted-run recovery and due-watch resumption;
- controlled live collection success after reboot;
- inbound TCP 80/443, TCP/UDP 111 and database/API ingress absent;
- runtime storage remains `PROJECT_LOCAL_ONLY`.

Canonical validation:
- run `33258520620`, SUCCESS;
- deployment SHA `6f8fb938590aa7ddabba96ee3a4c0e108e225d97`.

Temporary owner-approved development security exception:
- public SSH TCP/22 from `0.0.0.0/0` remains temporarily allowed;
- broad egress to `0.0.0.0/0` remains temporarily unchanged;
- SSH/Bastion/private-admin and egress least-privilege hardening are deferred to final security review.

The runtime is `DEPLOYED_OWNER_ONLY_REAL_HOST_VALIDATED / NOT_PRODUCTION`.

## E5 Admin Dashboard Boundary

E5 is BASELINE_VALIDATED with state `LOCAL_PROTECTED / READ_ONLY / NOT_DEPLOYED`.

- reuses the E3 persisted-state reader;
- no parallel dashboard database;
- no coverage-to-verification or forecast-to-fact promotion;
- static script-free HTML and restrictive browser security headers;
- dashboard GET requests do not mutate canonical state;
- public/dashboard deployment is not approved.

Canonical validation:
- x64 run `33263584520`: 282 passed;
- native ARM64 run `33263584515`: SUCCESS.

## E6 Reproducibility Boundary

E6 is BASELINE_VALIDATED.

- migration 020 provides additive project-local reproducibility audit projection;
- exact query snapshot and timezone-aware research cut-off are persisted for instrumented live collection;
- instrumentation version, adapter fingerprint and canonical source-attempt linkage remain explicit;
- deterministic SHA-256 hashing uses basis `KGM_PERSISTED_LIVE_ITEM_V1`;
- missing locators remain `NOT_INSTRUMENTED` rather than reconstructed;
- provenance annotations do not modify verification state, confidence or independent-origin count;
- no parallel acquisition truth store is created.

Canonical validation:
- x64 run `33264133429`: 290 passed;
- native ARM64 run `33264133407`: 290 passed; aarch64/bootstrap/one-tick/systemd PASS.

## Post-Pilot Workstream Decision Boundary

The post-Phase-11 workstreams remain unnumbered and do not create ROADMAP Phase 12 or M14.

State:
- E1 Automatic Translation Foundation: BASELINE_VALIDATED;
- E2 Source Reputation and Status History: BASELINE_VALIDATED;
- E3 Private GPT Backend Action API: BASELINE_VALIDATED;
- E4 Free Unattended Runtime Deployment: BASELINE_VALIDATED_WITH_TEMPORARY_SECURITY_EXCEPTION;
- E5 Admin Read-Only Dashboard: BASELINE_VALIDATED;
- E6 Reproducibility Instrumentation: BASELINE_VALIDATED;
- E7 Forecast Probability Semantics: BASELINE_VALIDATED;
- E8 Controlled External Sharing / Public GPT: PREFLIGHT ASSESSMENT APPROVED; IMPLEMENTATION DEFERRED / NOT_APPROVED;
- E9 Shared Production Runtime: DEFERRED / NOT_APPROVED.

E8 preflight may inspect architecture, deployment, authentication, exposure, rate limiting, data minimization, endpoint scope, abuse controls, secret handling, rollback and publication gates. It may define a minimum implementation delta, but it must not activate public sharing or production exposure without a new explicit owner/architecture approval.

E9 requires a separate new architecture decision because current storage remains `PROJECT_LOCAL_ONLY` and shared/mixed runtime truth storage is blocked.

## Validation State

- M5: 57 passed, run `32953343877`
- M6: 62 passed, run `32961649091`
- M7 deterministic: 68 passed, run `32962379499`; live smoke `32962576874`
- M8 deterministic: 73 passed, run `32963096313`; live E2E `32963354135`
- M9: 82 passed, run `32965387054`
- M10: 88 passed, run `32966128001`
- M11: 118 passed, run `32973378757`
- M12: 154 passed, run `32980859938`
- M13: 199 passed, run `32993269910`
- Phase 11: 226 passed, run `33000478908`
- Post-Phase-11 unattended supervisor: 236 passed, run `33012596904`
- Private GPT pilot: 18/18 PASS
- E1: 241 passed, run `33244484173`
- E2: 248 passed, run `33244795277`
- E3: 254 passed, run `33247311921`
- E4 real host: run `33258520620`, SUCCESS
- E5: x64 282 passed run `33263584520`; native ARM64 run `33263584515`, SUCCESS
- E6: x64 290 passed run `33264133429`; native ARM64 run `33264133407`, SUCCESS
- E7: x64 294 passed run `33265984585`; native ARM64 run `33265984622`, SUCCESS

## Current State

- Engineering implementation: BASELINE_VALIDATED through ROADMAP Phase 11
- Owner-only private GPT pilot: SUCCESSFUL, 18/18 PASS
- E1-E7: BASELINE_VALIDATED, with E4 retaining the temporary development security exception
- Shared Infrastructure ADR: APPROVED / HYBRID
- Runtime storage: `PROJECT_LOCAL_ONLY`
- Mixed/shared runtime storage: BLOCKED pending new explicit architecture approval
- Controlled-pilot live integrations: VALIDATED
- Owner-only unattended cloud runtime: `DEPLOYED_OWNER_ONLY_REAL_HOST_VALIDATED / NOT_PRODUCTION`
- Backend Action API foundation: VALIDATED_LOCAL_READ_ONLY
- Private GPT backend Action connection: NOT_CONNECTED
- Backend HTTPS deployment: NOT_DEPLOYED
- Admin dashboard deployment: NOT_DEPLOYED
- Public sharing: DEFERRED / NOT_APPROVED
- Shared production runtime: NOT_APPROVED
- Current engineering activity: D0 documentation convergence + E8 read-only preflight/delta audit
- Next numbered ROADMAP phase: NONE_APPROVED
- Production/live operational maturity: NOT_OPERATIONAL
