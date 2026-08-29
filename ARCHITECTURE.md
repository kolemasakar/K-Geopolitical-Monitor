# ARCHITECTURE
Technical architecture definition for K-Geopolitical Monitor.

Version: 2.5
Status: APPROVED

## Purpose

Define the current system architecture boundaries.

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

## Implemented and Validated Baseline

Validated foundations include:
- persistence, evidence, verification and event intelligence;
- project-local operational monitoring, retry/recovery and ranked findings;
- controlled/live read-only acquisition with provenance and source-failure isolation;
- original-origin M8 evidence independence;
- strategic alert policies/lifecycle and priority/cadence separation;
- watch-scoped region/language attribution and coverage reporting;
- M10 translation-attribution isolation from evidence confidence/source independence;
- E1 durable provider-neutral translation representation with version history and explicit degraded states;
- E2 durable append-only source reputation/status history with review and restoration lineage;
- E2 source reputation remains separate from claim truth and independent-origin counting;
- durable advanced graph identity, projection, lifecycle, history, temporal/causal traversal and explainable queries;
- durable advanced forecasting identity, immutable scenario versions, typed provenance, outcome evaluation, calibration history and explainable queries;
- durable immutable report snapshots, sections and typed references;
- one common report assembler for strategic/global/regional/event/storyline/forecast/outlook reports;
- deterministic structured and Markdown report rendering;
- durable operational coverage contracts, requirements, immutable snapshots and per-requirement results;
- per-source collection attempts and adapter/item identity integrity;
- source-class, source-availability, region/language and freshness convergence;
- historical coverage queries and coverage-aware reporting through the existing M13 report store;
- cross-layer M8/M10/M11/M12/M13 truth-state isolation through Phase 11;
- unattended supervisor recovery-on-start and due-cycle execution;
- cadence-safe failed live-watch attempts that persist monitoring-run state rather than retrying every supervisor poll;
- owner-only private GPT behavior validated across 18 deterministic/real-world truth-boundary scenarios;
- E3 owner-only read-only FastAPI backend state facade with explicit OpenAPI operations;
- E3 bearer authentication and read-only project-local SQLite access;
- E3 no-mutation, no-web-substitution and fail-closed unavailable-state behavior.

These components represent a controlled project-local validated engineering baseline and must not be interpreted as complete global production maturity.

## Runtime and Shared Infrastructure Boundary

The approved Shared Infrastructure ADR requires:
- HYBRID architecture;
- project-specific domain logic and canonical stores remain local;
- runtime storage remains PROJECT_LOCAL_ONLY;
- no implicit mixed storage;
- no shared runtime database;
- no direct cross-project canonical-store mutation;
- any future shared runtime storage requires a new explicit architecture approval.

Production/shared runtime remains NOT_APPROVED.

## External Integration Boundary

Controlled-pilot integrations:
- Consilium press-release RSS: Official sources;
- GDELT DOC 2.0 API: Structured data discovery metadata.

Both are read-only and require no credentials in the current controlled pilot.

GDELT metadata is discovery/index evidence only. Original publishers or primary sources remain the factual Source of Truth for linked content.

Live network checks remain isolated from deterministic CI in manual smoke workflows.

External-source availability is not assumed. A collection may be COMPLETED, PARTIAL or FAILED, and every source failure must remain visible in collection audit/attempt state.

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

E1 is an unnumbered post-Phase-11 workstream and does not create ROADMAP Phase 12 or M14.

Durable model:
- raw_item_translations stores versioned derived translation records;
- raw_items remains the immutable source-text record for translation purposes;
- source_language and target_language are explicit;
- original_text and translated_text are separately inspectable;
- method, provider, provider_version and translation_version are persisted;
- status is explicit: SUCCESS, FAILED, UNAVAILABLE, UNSUPPORTED or AMBIGUOUS;
- uncertainty_note and error_message preserve degraded/ambiguous state;
- underlying_origin_id and origin_kind bind the translation to its source origin.

Origin rules:
- live items inherit the normalized host from live_source_provenance.original_url, matching M8 origin semantics;
- non-live raw items without live provenance fall back to source_id;
- conflicting live provenance hosts for one raw item fail closed;
- a translation record exposes no new independent-origin credit.

Truth isolation:
- translation cannot increase M8 independent-origin count;
- translation cannot modify M8 verification state;
- translation cannot become independent graph evidence;
- translation cannot increase forecast factual confidence;
- translation cannot inflate coverage confidence;
- translation cannot strengthen report presentation truth.

Runtime contract:
- TranslationAdapter is provider-neutral;
- TranslationService persists derived records and history;
- DeterministicTranslationAdapter exists only for local deterministic validation;
- no external translation provider is activated or approved.

E1 validation:
- migration 018: VALIDATED;
- GitHub Actions run 33244484173: 241 passed in 37.10s;
- E1 state: BASELINE_VALIDATED.

## E2 Source Reputation Boundary

E2 is an unnumbered post-Phase-11 workstream and does not create ROADMAP Phase 12 or M14.

Durable model:
- source_reputation_history is append-only and versioned per source;
- status, reliability rating, reason, evidence references, policy/version and review timestamps remain explicit;
- restoration preserves adverse history and explicit restoration lineage;
- current-state queries are deterministic while historical state remains inspectable;
- legacy sources.reliability remains separate from E2 assessment history.

Truth isolation:
- COMPROMISED is not automatic FALSE;
- source reputation/status does not modify claim truth;
- source reputation/status does not change M8 independent-origin count;
- a compromised source may still evidence that a claim or narrative exists.

E2 validation:
- migration 019: VALIDATED;
- GitHub Actions run 33244795277: 248 passed in 24.01s;
- E2 state: BASELINE_VALIDATED.

## Advanced Geopolitical Graph Boundary

M11 converges M4 graph fragments into one durable project-local graph contract.
- canonical project objects remain Source of Truth;
- graph inference is not source evidence;
- graph confidence does not modify M8 confidence or independent-origin count;
- graph operations do not automatically assign VERIFIED;
- no external graph service is required or approved.

## Advanced Forecasting Boundary

M12 extends existing forecasting/calibration/history components rather than creating a parallel stack.
- forecast versions and scenario versions are immutable;
- raw probability, calibrated probability and scenario confidence are distinct;
- source evidence, canonical events, graph relationships, findings and analyst assumptions remain typed separately;
- forecasts are analytical outputs, not facts;
- forecasting cannot increase M8 independent-origin count/verification status or mutate M11 graph state;
- heuristic probabilities must remain distinguishable from calibrated probabilities;
- no external forecasting provider is required or approved.

## Full Reporting Environment Boundary

M13 provides one canonical presentation subsystem over existing validated state.
- report_snapshots stores immutable report identity/metadata;
- report_sections stores ordered typed presentation sections;
- report_references stores typed upstream traceability;
- all approved report types use this same model;
- Storyline Report is report-scoped composition and does not create a canonical storyline table;
- observed facts, verification state, analytical context, graph inference, forecast scenarios, assumptions and coverage metadata remain distinguishable;
- reporting cannot modify upstream truth;
- deterministic structured and Markdown representations are rendered from the same persisted snapshot;
- runtime report DB uses the existing project-local storage policy;
- no external publishing/delivery provider is required or approved.

## Global Operational Coverage Boundary

Phase 11 adds one coverage-measurement layer over existing M6/M7/M10 state and M13 presentation.

Durable coverage model:
- operational_coverage_contracts declares explicit scope/window/freshness identity;
- operational_coverage_requirements stores typed required units;
- operational_coverage_snapshots stores immutable aggregate assessments;
- operational_coverage_requirement_results explains every required unit;
- source_collection_attempts preserves per-source acquisition availability state.

Baseline measurable dimensions:
- SOURCE_CLASS;
- SOURCE_ID / SOURCE_AVAILABILITY;
- REGION_LANGUAGE;
- FRESHNESS.

Baseline statuses:
- SATISFIED;
- GAP;
- UNAVAILABLE;
- STALE;
- UNKNOWN;
- UNMEASURED.

Coverage semantics:
- coverage_ratio is satisfied required units / required units;
- coverage_confidence is known assessment states / required units;
- UNKNOWN and UNMEASURED reduce coverage confidence;
- coverage confidence is not factual verification confidence;
- source count, graph degree, forecast count and report count cannot inflate coverage;
- translation attribution does not create source independence;
- GLOBAL is an explicit scope key, not a universal-completeness claim;
- historical coverage state remains immutable and queryable;
- Phase 11 coverage reports use the existing M13 report store;
- no external coverage provider is required or approved.

## Unattended Runtime Boundary

Post-Phase-11 supervisor components are validated locally but not deployed as production service.

Rules:
- UnattendedMonitoringService is a thin supervisor over existing due-cycle execution;
- interrupted-run recovery occurs once per process startup;
- unexpected supervisor exceptions are not silently swallowed;
- external service management such as systemd is responsible for restart/logging after deployment;
- LiveOperationalCycle persists failed monitoring-run state for collection/processing failures;
- failed started_at drives cadence and prevents retry-every-poll loops;
- successful zero-item collection remains a completed monitoring attempt;
- runtime persistence remains under PROJECT_LOCAL_ONLY storage policy.

Cloud unattended runtime state: NOT_DEPLOYED.

## Private GPT and E3 Action API Boundary

The private K-Geopolitical Monitor GPT is currently OWNER_ONLY.

Validated pilot behavior:
- current public-web geopolitical research;
- local and local-language source discovery;
- provenance/origin tracing;
- official-source limitation handling;
- compromised-source handling;
- graph/forecast/report truth separation;
- explicit coverage limitations;
- fail-closed backend/persistent-state behavior;
- reproducibility-oriented research output.

E3 now provides a validated local backend Action API foundation, but the private GPT is not yet connected to it and no HTTPS deployment exists.

E3 API rules:
- initial scope is read-only;
- owner bearer token is injected at runtime and is not persisted in repository state;
- project-local SQLite is opened read-only and query-only;
- missing or invalid bearer credentials fail with HTTP 401 and WWW-Authenticate: Bearer;
- /health is separate from protected owner-state endpoints;
- API GET requests must not mutate project state;
- unavailable persisted state is returned explicitly and is never replaced with current web research;
- last unattended-cycle provenance remains null/NOT_INSTRUMENTED until the runtime persists that distinction;
- direct database exposure is forbidden;
- HTTPS is required before a GPT Action connection is approved.

Therefore:
- the GPT must not claim Action-backed access until an actual Action call returns backend data;
- it must not replace unavailable backend state with a fresh web search;
- public-web search remains user-facing research, not persisted monitoring history;
- E3 local validation is not a deployment or production-readiness claim.

E3 validation:
- GitHub Actions run 33247311921, job 99086917660: SUCCESS;
- pytest: 254 passed in 26.66s;
- E3 state: BASELINE_VALIDATED.

## Approved Post-Pilot Expansion Architecture

The following workstreams are unnumbered post-Phase-11 activities and do not create ROADMAP Phase 12 or M14.

E1 Automatic Translation Foundation:
- BASELINE_VALIDATED;
- provider-neutral local persistence and adapter contract validated;
- external translation provider: NONE_APPROVED.

E2 Source Reputation and Status History:
- BASELINE_VALIDATED;
- append-only history/status model validated locally;
- COMPROMISED is reviewable and reversible with preserved history;
- source reputation remains separate from claim truth.

E3 Private GPT Backend Action API:
- BASELINE_VALIDATED;
- local read-only owner API and OpenAPI contract validated;
- bearer authentication validated;
- no direct database exposure;
- fail-closed no-web-substitution rule validated;
- HTTPS deployment: NOT_DEPLOYED;
- GPT Action connection: NOT_CONNECTED.

E4 Free Unattended Runtime Deployment:
- CURRENT;
- approved for validation, not deployment claim;
- ARM64/runtime/systemd/reboot/recovery/storage tests required;
- database ports remain closed;
- Oracle OCI Always Free A1 is the primary candidate, Google Cloud e2-micro fallback.

E5-E7 are planned owner-only engineering workstreams.
E8 public/external sharing and E9 shared production runtime remain NOT_APPROVED.

## Validation State

M5 full test cycle: PASS - 57 tests, run 32953343877.
M6 controlled pilot baseline: PASS - 62 tests, run 32961649091.
M7 deterministic regression: PASS - 68 tests, run 32962379499.
M7 live-source smoke: PASS - run 32962576874.
M8 deterministic regression: PASS - 73 tests, run 32963096313.
M8 live end-to-end controlled pilot: PASS - run 32963354135.
M9 hardened regression: PASS - 82 tests, run 32965387054.
M10 multi-region/language regression: PASS - 88 tests, run 32966128001.
M11 advanced geopolitical graph final regression: PASS - 118 tests, run 32973378757.
M12 advanced forecasting final regression: PASS - 154 tests, run 32980859938.
M13 full reporting environment final implementation regression: PASS - 199 tests, run 32993269910.
Phase 11 global operational coverage final implementation regression: PASS - 226 tests, run 33000478908.
Post-Phase-11 unattended supervisor/cadence-safe live-cycle regression: PASS - 236 tests, run 33012596904.
Private GPT owner-only full matrix: PASS - 18/18.
GPT-18/full matrix closure CI: SUCCESS - run 33046581445.
Owner-only pilot plan closure CI: SUCCESS - run 33046621582.
Post-pilot retrospective/expansion-plan CI: SUCCESS - run 33046677596.
E1 Automatic Translation Foundation: PASS - 241 tests, run 33244484173.
E2 Source Reputation and Status History: PASS - 248 tests, run 33244795277.
E3 Private GPT Backend Action API: PASS - 254 tests, run 33247311921.

## Current State

- Engineering implementation: BASELINE_VALIDATED through ROADMAP Phase 11
- ROADMAP Phase 5: BASELINE_VALIDATED
- ROADMAP Phase 6: BASELINE_VALIDATED
- ROADMAP Phase 7: BASELINE_VALIDATED
- ROADMAP Phase 8: BASELINE_VALIDATED
- ROADMAP Phase 9: BASELINE_VALIDATED
- ROADMAP Phase 10: BASELINE_VALIDATED
- ROADMAP Phase 11: BASELINE_VALIDATED
- Owner-only private GPT pilot: SUCCESSFUL, 18/18 PASS
- E1 Automatic Translation Foundation: BASELINE_VALIDATED
- E2 Source Reputation and Status History: BASELINE_VALIDATED
- E3 Private GPT Backend Action API: BASELINE_VALIDATED
- Runtime storage: PROJECT_LOCAL_ONLY
- Shared Infrastructure ADR: APPROVED
- Controlled-pilot live integrations: VALIDATED
- Unattended supervisor/live-cycle local baseline: VALIDATED
- Backend Action API foundation: VALIDATED_LOCAL_READ_ONLY
- Private GPT backend Action connection: NOT_CONNECTED
- Backend HTTPS deployment: NOT_DEPLOYED
- Unattended cloud runtime: NOT_DEPLOYED
- External graph providers: NONE_APPROVED
- External forecasting providers: NONE_APPROVED
- External reporting/publishing providers: NONE_APPROVED
- External coverage providers: NONE_APPROVED
- External notification providers: NONE_APPROVED
- External translation provider: NONE_APPROVED
- Production/global external integrations: NONE_APPROVED
- Current engineering activity: E4 Free Unattended Runtime Deployment validation
- Next roadmap phase: NONE_APPROVED
- Production/live operational maturity: NOT_OPERATIONAL
