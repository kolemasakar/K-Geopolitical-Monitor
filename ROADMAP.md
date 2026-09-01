# ROADMAP

Version: 2.9
Status: APPROVED
Project: K-Geopolitical Monitor

## Development principle

Minimal Functional Core First.

The project is developed through validation stages. Implementation does not equal validation.

Implementation milestone labels M0-M13 are engineering work packages and are not identical to ROADMAP phase numbers.

No ROADMAP Phase 12 and no M14 are approved at this checkpoint.

## Phases

## Phase 0 - Project Foundation

Goals:
- establish project governance;
- approve documentation standards;
- preserve approved product concept.

Gate:
PHASE_0_APPROVED

## Phase 1 - Minimal Functional Core Specification

Goals:
- define minimum end-to-end monitoring pipeline;
- define contracts for sources, events, evidence, verification, forecasting and reports.

## Phase 2 - Minimal Functional Core Implementation

Implement source registry, discovery, event normalization, entity resolution, deduplication, verification, storyline linking, importance scoring, forecasting and reporting.

## Phase 3 - Core Validation and Calibration

Validate evidence handling, contradictions, event lifecycle, forecast updates and report quality.

## Phase 4 - Adaptive Learning Foundation

Implement controlled detection of source drift, platform changes, relationship changes and forecast performance changes.

## Phase 5 - Controlled Pilot Monitoring

Validated engineering foundation:
- M5 project-local operational baseline: PASS;
- M6 deterministic controlled pilot baseline: PASS;
- M7 live public-source acquisition pilot: PASS;
- M8 live end-to-end controlled pilot processing: PASS;
- Consilium RSS live smoke: PASS;
- GDELT DOC 2.0 live smoke: PASS;
- source provenance and collection audit: PASS;
- origin-based verification independence: PASS;
- live-source failure isolation: PASS;
- project-local operational finding projection: PASS.

Phase 5 engineering baseline status:
BASELINE_VALIDATED

Phase 5 completion does not approve production/global operation, unattended continuous monitoring, shared runtime storage or automatic VERIFIED status.

## Phase 6 - Strategic Alerts and Continuous Monitoring

Validated engineering foundation:
- persisted watch alert policies: PASS;
- trigger thresholds and traceable finding-to-alert projection: PASS;
- stable deduplication and cross-cycle updates: PASS;
- OPEN/UPDATED/INVALIDATED/RESOLVED lifecycle: PASS;
- restart persistence and priority/cadence separation: PASS;
- project-local runtime storage: PASS.

M9 hardened regression:
- GitHub Actions run 32965387054;
- 82 passed in 1.71s.

Phase 6 engineering baseline status:
BASELINE_VALIDATED

## Phase 7 - Multi-Region Expansion

Validated engineering foundation:
- canonical region/language registries: PASS;
- watch-scoped region/language requirements: PASS;
- raw-item attribution and coverage reporting: PASS;
- cross-watch attribution isolation: PASS;
- translation metadata verification-isolation: PASS;
- project-local runtime storage: PASS.

M10 regression:
- GitHub Actions run 32966128001;
- 88 passed in 2.07s.

Phase 7 engineering baseline status:
BASELINE_VALIDATED

## Phase 8 - Advanced Geopolitical Graph

Validated engineering foundation:
- M4 graph fragments converged into one durable M11 graph contract: PASS;
- migration 010 graph persistence: PASS;
- deterministic node/logical-edge identity: PASS;
- actor/event/claim/finding projection: PASS;
- evidence-backed relationship lifecycle and material history: PASS;
- temporal validity and historical snapshots: PASS;
- bounded cycle-safe causal/influence traversal: PASS;
- advanced explainable IntelligenceQuery facade: PASS;
- M8/M10/M11 truth-isolation: PASS;
- project-local runtime storage: PASS;
- external graph provider dependency: NONE.

M11 final regression:
- GitHub Actions run 32973378757;
- 118 passed in 4.24s.

Phase 8 engineering baseline status:
BASELINE_VALIDATED

## Phase 9 - Advanced Forecasting

Validated engineering foundation:
- durable forecast identity and immutable version history: PASS;
- raw/calibrated probability separation: PASS;
- typed provenance-bound inputs and fail-closed references: PASS;
- immutable scenario lifecycle and signal analysis: PASS;
- durable outcome resolution and exact-version evaluation: PASS;
- PARTIAL/AMBIGUOUS non-scoring: PASS;
- reproducible calibration history and performance breakdowns: PASS;
- advanced forecast query/provenance/history facade: PASS;
- M8/M11 truth-state isolation: PASS;
- project-local runtime storage: PASS;
- external forecasting provider dependency: NONE.

M12 final regression:
- GitHub Actions run 32980859938;
- 154 passed in 8.19s.

Phase 9 engineering baseline status:
BASELINE_VALIDATED

## Phase 10 - Full Reporting Environment

Validated engineering foundation:
- migration 015 common report snapshot/section/reference persistence: PASS;
- deterministic immutable report identities and fail-closed canonical references: PASS;
- one common ReportAssembler with typed provenance: PASS;
- source evidence, graph inference and forecast scenario separation: PASS;
- Strategic Alert report: PASS;
- Global Geopolitical Brief: PASS;
- Regional/Country Brief with explicit region/language coverage metadata: PASS;
- Event Dossier: PASS;
- report-scoped Storyline Report without canonical storyline truth table: PASS;
- version-anchored Forecast Report: PASS;
- scope-only Strategic Outlook: PASS;
- deterministic structured representation: PASS;
- deterministic Markdown rendering: PASS;
- restart rendering reproducibility: PASS;
- M8/M10/M11/M12 read-only isolation: PASS;
- project-local runtime database enforcement: PASS;
- external reporting/publishing provider dependency: NONE.

M13 validation progression:
- M13.1 run 32982639826 - 160 passed in 11.40s;
- M13.2 run 32989895962 - 170 passed in 12.00s;
- M13.3-M13.5 run 32992328055 - 193 passed in 10.98s;
- M13.6 run 32993269910 - 199 passed in 12.10s.

Phase 10 engineering baseline status:
BASELINE_VALIDATED

Phase 10 completion does not approve external publishing/delivery, global operational coverage, shared runtime storage, production dashboards or production/live OPERATIONAL status.

## Phase 11 - Global Operational Coverage

Validated engineering foundation:
- explicit deterministic coverage contracts and typed requirements: PASS;
- migrations 016-017 durable coverage snapshots/results and per-source collection attempts: PASS;
- adapter/item source identity fail-closed integrity: PASS;
- SOURCE_CLASS and SOURCE_ID/SOURCE_AVAILABILITY convergence: PASS;
- REGION_LANGUAGE convergence with watch isolation: PASS;
- explicit persisted freshness evaluation: PASS;
- SATISFIED/GAP/UNAVAILABLE/STALE/UNKNOWN/UNMEASURED status separation: PASS;
- deterministic coverage_ratio and coverage_confidence with distinct semantics: PASS;
- source count cannot inflate coverage units: PASS;
- immutable historical/latest coverage query: PASS;
- M13 Global/Regional coverage reporting integration without a parallel report store: PASS;
- UNKNOWN and UNMEASURED remain visible in structured and Markdown output: PASS;
- M8/M10/M11/M12/M13 isolation: PASS;
- GLOBAL scope does not suppress explicit gaps or imply universal completeness: PASS;
- project-local runtime database enforcement: PASS;
- external coverage provider dependency: NONE.

Phase 11 validation progression:
- P11.1 run 32996565227 - 203 passed in 15.48s;
- P11.2 run 32997440380 - 210 passed in 16.63s;
- P11.3 run 32997961490 - 217 passed in 27.46s;
- P11.4 run 32999092257 - 219 passed in 20.55s;
- P11.5 run 32999835225 - 223 passed in 83.96s;
- P11.6 run 33000478908 - 226 passed in 17.67s.

Phase 11 engineering baseline status:
BASELINE_VALIDATED

Phase 11 validates the ability to explicitly define, measure, persist, query and report operational coverage. It does not prove complete real-time monitoring of every country, language, actor, storyline or source. Production/live status remains NOT_OPERATIONAL.

## Unnumbered Post-Phase-11 Owner-Only GPT Pilot

This activity is not ROADMAP Phase 12 and does not create M14.

Validated preparation:
- owner-only private K-Geopolitical Monitor GPT configured;
- Web Search enabled;
- Code Interpreter/Data Analysis enabled;
- no Knowledge files required for initial pilot;
- no backend Action/API connected;
- unattended supervisor and cadence-safe live operational cycle implemented and regression-tested;
- GitHub Actions run 33012596904: 236 passed.

Final pilot matrix:
- test_case_count: 18;
- passed_count: 18;
- failed_count: 0;
- blocked_count: 0;
- critical truth-boundary violations: 0;
- hallucinated/untraceable source failures: 0;
- verification-boundary failures: 0;
- coverage-boundary failures: 0;
- backend-access hallucination failures: 0.

Closure validation:
- GPT-18/full matrix closure run 33046581445: SUCCESS;
- owner-only pilot plan closure run 33046621582: SUCCESS;
- post-pilot retrospective/expansion-plan run 33046677596: SUCCESS.

Pilot status:
OWNER_ONLY_PILOT_PASS

The pilot validates user-facing research and truth-boundary behavior for continued owner-only use. It does not approve production/live operation, public sharing, external delivery, shared runtime storage or backend Action access.

## Approved Unnumbered Post-Pilot Expansion Workstreams

These workstreams are post-Phase-11 engineering/planning activities. They are not a new numbered ROADMAP phase.

### E1 - Automatic Translation Foundation

State:
BASELINE_VALIDATED

Validated foundation:
- migration 018 durable raw_item_translations store: PASS;
- original raw-item text remains unchanged: PASS;
- translated text stored separately: PASS;
- source/target language and method/provider/version metadata: PASS;
- SUCCESS/FAILED/UNAVAILABLE/UNSUPPORTED/AMBIGUOUS states: PASS;
- ambiguity/failure remains visible: PASS;
- versioned retranslation history: PASS;
- live translation inherits normalized original publisher host: PASS;
- non-live fallback origin uses source identity: PASS;
- translation never creates new independent-source credit: PASS;
- M8 verification and independent-origin count unchanged: PASS;
- restart persistence: PASS;
- external translation provider dependency: NONE.

E1 canonical regression:
- GitHub Actions run 33244484173;
- 241 passed in 37.10s.

### E2 - Source Reputation and Status History

State:
BASELINE_VALIDATED

Validated foundation:
- migration 019 durable append-only source_reputation_history: PASS;
- explicit status/reliability/reason/evidence/policy/review metadata: PASS;
- deterministic current-state and complete history queries: PASS;
- restoration lineage with preserved adverse history: PASS;
- COMPROMISED is not automatic FALSE: PASS;
- source status does not alter claim truth or independent-origin count: PASS;
- legacy sources.reliability remains separate: PASS.

E2 canonical regression:
- GitHub Actions run 33244795277;
- 248 passed in 24.01s.

### E3 - Private GPT Backend Action API

State:
BASELINE_VALIDATED

Validated foundation:
- FastAPI owner-only read-only backend API: PASS;
- explicit OpenAPI operation IDs for persisted-state reads: PASS;
- bearer-token authentication with runtime token injection: PASS;
- missing/invalid bearer token -> HTTP 401 with WWW-Authenticate: Bearer: PASS;
- valid owner bearer token -> protected endpoint execution: PASS;
- /health remains separately accessible: PASS;
- project-local SQLite opened read-only/query-only: PASS;
- GET endpoint sweep does not mutate canonical project state: PASS;
- no public-web substitution for unavailable persisted backend state: PASS;
- unattended-cycle timestamp fails closed as NOT_INSTRUMENTED when provenance is unavailable: PASS.

E3 canonical regression:
- GitHub Actions run 33247311921;
- job 99086917660;
- 254 passed in 26.66s;
- result SUCCESS.

E3 completion validates the local API foundation only. It does not mean the private GPT is connected to the backend, an HTTPS endpoint is deployed, or production/live operation is approved.

### E4 - Free Unattended Runtime Deployment

State:
BASELINE_VALIDATED_WITH_TEMPORARY_SECURITY_EXCEPTION

Validated foundation:
- real OCI Ubuntu 24.04 ARM64 owner-only VM: PASS;
- immutable deployment and bootstrap: PASS;
- real-host pytest `277 passed, 2 warnings`: PASS;
- project-local database integrity: PASS;
- systemd enable/start and real reboot auto-recovery: PASS;
- interrupted-run recovery and due-watch resumption: PASS;
- controlled live collection success after reboot: PASS;
- OCI Security List evidence captured: PASS;
- inbound TCP 80/443, TCP/UDP 111 and database/API ingress absent: PASS;
- runtime storage remains PROJECT_LOCAL_ONLY: PASS;
- production/live remains NOT_OPERATIONAL.

Temporary owner-approved development exception:
- public SSH TCP/22 remains allowed from `0.0.0.0/0` during active development;
- broad egress to `0.0.0.0/0` remains unchanged during active development;
- SSH/Bastion/private-admin and egress least-privilege hardening are deferred to final project security review.

E4 canonical real-host validation:
- workflow run `33258520620`;
- job `99116323168`;
- deployment SHA `6f8fb938590aa7ddabba96ee3a4c0e108e225d97`;
- result SUCCESS.

### E5 - Admin Read-Only Dashboard

State:
BASELINE_VALIDATED

Supporting state:
`LOCAL_PROTECTED / READ_ONLY / NOT_DEPLOYED`

Validated foundation:
- owner/admin-only read-only FastAPI dashboard app: PASS;
- existing E3 persisted-state reader reused: PASS;
- no parallel dashboard database: PASS;
- PROJECT_LOCAL_ONLY runtime state preserved: PASS;
- watch due/running/failed projection: PASS;
- source reputation and availability projection: PASS;
- coverage GAP/UNAVAILABLE/STALE/UNKNOWN/UNMEASURED visibility: PASS;
- findings/alerts/active forecast projection: PASS;
- source collection attempt visibility: PASS;
- missing uptime instrumentation remains explicit rather than inferred: PASS;
- no coverage-to-verification or forecast-to-fact promotion: PASS;
- static script-free HTML with persisted-value escaping: PASS;
- restrictive browser security headers: PASS;
- dashboard GET requests do not mutate canonical state: PASS;
- dashboard deployment/public exposure: NOT_DEPLOYED.

E5 canonical regression at SHA `4da27ac374c9832cbe189d178cf2e10fa0326bb5`:
- x64 run `33263584520`, job `99129562037`: 282 passed, 1 warning, SUCCESS;
- native ARM64 run `33263584515`, job `99129561992`: SUCCESS;
- native ARM64 confirmation, full regression, bootstrap-shell, one-tick smoke and systemd contract: PASS.

### E6 - Reproducibility Instrumentation

State:
BASELINE_VALIDATED

Validated foundation:
- migration 020 durable additive reproducibility audit projection: PASS;
- exact query snapshot and timezone-aware research cut-off capture: PASS;
- instrumentation version and adapter identity/version fingerprint: PASS;
- canonical source collection/attempt linkage without parallel acquisition state: PASS;
- deterministic SHA-256 persisted-artifact hashing: PASS;
- persisted-artifact hash basis explicitly identified as `KGM_PERSISTED_LIVE_ITEM_V1`: PASS;
- missing request locator remains `NOT_INSTRUMENTED`, not reconstructed: PASS;
- audit status and source collection status remain distinct: PASS;
- source collection failure can coexist with successful audit capture: PASS;
- explicit provenance annotation only when classification exists: PASS;
- no automatic origin/syndication/repost/translation/citation/duplicate inference from URL/domain count: PASS;
- provenance annotations do not modify claim verification or independent-origin count: PASS;
- uninstrumented collection does not fabricate research history: PASS;
- adapter/source-attempt mismatch fails closed: PASS;
- canonical unattended runtime integration: PASS;
- PROJECT_LOCAL_ONLY runtime storage preserved: PASS.

E6 canonical regression at SHA `af4444098ff4e1541ddaa2323c0fed723eeb3d65`:
- x64 run `33264133429`, job `99131026905`: 290 passed, 1 warning in 27.77s, SUCCESS;
- native ARM64 run `33264133407`, job `99131026851`: 290 passed, 1 warning in 29.53s, SUCCESS;
- native architecture `aarch64`, bootstrap-shell, one-tick smoke and systemd contract: PASS.

### E7 - Forecast Probability Semantics

State:
BASELINE_VALIDATED

Validated foundation:
- M12 persisted raw/calibrated/scenario-confidence separation preserved: PASS;
- canonical semantic contract `KGM_FORECAST_SEMANTICS_V1`: PASS;
- `raw_probability` explicitly analytical pre-calibration probability: PASS;
- `calibrated_probability` explicitly calibrated analytical probability: PASS;
- `scenario_confidence` explicitly scenario-assessment confidence, not probability: PASS;
- owner-only read-only `/v1/forecasts/active` API projection: PASS;
- API omits generic probability/confidence aliases for new E7 forecast surfaces: PASS;
- dashboard renders Raw / Calibrated / Scenario confidence separately: PASS;
- structured reports expose machine-readable forecast semantics: PASS;
- Markdown reports expose explicit forecast semantic boundaries: PASS;
- high forecast probability cannot promote weak claim verification/factual confidence: PASS;
- verification state, factual confidence and independent-origin count remain unchanged: PASS;
- no migration 021 and no parallel forecasting subsystem: PASS;
- PROJECT_LOCAL_ONLY runtime storage preserved: PASS;
- external forecasting provider dependency: NONE.

E7 canonical regression at SHA `72f049b30fcaa3711c7712c8df7d1da1f934f650`:
- x64 run `33265984585`, job `99136020793`: 294 passed, 1 warning in 29.26s, SUCCESS;
- native ARM64 run `33265984622`, job `99136020853`: 294 passed, 1 warning in 28.09s, SUCCESS;
- native architecture `aarch64`, bootstrap-shell, one-tick smoke and systemd contract: PASS.

### E9A - Owner-Only Production Runtime Hardening

State:
APPROVED_FOR_DESIGN_AND_LOCAL_IMPLEMENTATION

Decision:
`docs/decisions/E9A_OWNER_ONLY_PRODUCTION_HARDENING_DECISION_2026-09-01.md`

Plan:
`docs/implementation/E9A_OWNER_ONLY_PRODUCTION_RUNTIME_HARDENING_PLAN.md`

Approved scope:
- single-instance runtime lease;
- explicit SQLite durability/concurrency profile;
- owner-only backup/disaster-recovery hardening;
- owner-only runtime health instrumentation;
- deployment/security hardening review;
- x64, native ARM64 and real-host validation.

Mandatory boundaries:
- runtime storage remains PROJECT_LOCAL_ONLY;
- no shared/mixed runtime database;
- no public API/dashboard/GPT exposure;
- E8 Business/publication remains user-deferred;
- E9 Shared Production Runtime remains NOT_APPROVED;
- production/live remains NOT_OPERATIONAL until a separate explicit launch decision.

### Remaining deferred workstreams

Execution state:
- E6 Reproducibility Instrumentation - P1 - BASELINE_VALIDATED;
- E7 Forecast Probability Semantics - P1 - BASELINE_VALIDATED;
- E8 Controlled External Sharing / Public GPT - USER_DEFERRED_UNTIL_SEPARATE_REQUEST;
- E9A Owner-Only Production Runtime Hardening - CURRENT / APPROVED_FOR_DESIGN_AND_LOCAL_IMPLEMENTATION;
- E9 Shared Production Runtime - DEFERRED - NOT_APPROVED.

Post-pilot invariants:
- runtime storage remains PROJECT_LOCAL_ONLY;
- no shared runtime database;
- no implicit mixed storage;
- no translation-based source independence;
- no graph-based source independence;
- no forecast-to-fact promotion;
- no coverage-to-verification promotion;
- no report-presentation truth inflation;
- no public-web substitution for persisted backend state;
- no external provider activation without explicit approval.

## Current implementation checkpoint

- Product Concept: APPROVED
- Roadmap: APPROVED / v2.9
- Engineering implementation: BASELINE_VALIDATED through ROADMAP Phase 11
- ROADMAP Phase 5 Controlled Pilot Monitoring: BASELINE_VALIDATED
- ROADMAP Phase 6 Strategic Alerts and Continuous Monitoring: BASELINE_VALIDATED
- ROADMAP Phase 7 Multi-Region Expansion: BASELINE_VALIDATED
- ROADMAP Phase 8 Advanced Geopolitical Graph: BASELINE_VALIDATED
- ROADMAP Phase 9 Advanced Forecasting: BASELINE_VALIDATED
- ROADMAP Phase 10 Full Reporting Environment: BASELINE_VALIDATED
- ROADMAP Phase 11 Global Operational Coverage: BASELINE_VALIDATED
- Owner-only private GPT pilot: SUCCESSFUL, 18/18 PASS
- E1 Automatic Translation Foundation: BASELINE_VALIDATED
- E2 Source Reputation and Status History: BASELINE_VALIDATED
- E3 Private GPT Backend Action API: BASELINE_VALIDATED
- E4 Free Unattended Runtime Deployment: BASELINE_VALIDATED_WITH_TEMPORARY_SECURITY_EXCEPTION
- E5 Admin Read-Only Dashboard: BASELINE_VALIDATED / LOCAL_PROTECTED / NOT_DEPLOYED
- E6 Reproducibility Instrumentation: BASELINE_VALIDATED
- E7 Forecast Probability Semantics: BASELINE_VALIDATED
- E8 Controlled External Sharing / Public GPT: USER_DEFERRED_UNTIL_SEPARATE_REQUEST
- E9A Owner-Only Production Runtime Hardening: CURRENT / APPROVED_FOR_DESIGN_AND_LOCAL_IMPLEMENTATION
- E9 Shared Production Runtime: DEFERRED / NOT_APPROVED
- Shared Infrastructure Architecture Review: COMPLETE; HYBRID adopted
- Shared Infrastructure ADR: APPROVED
- Runtime storage mode: PROJECT_LOCAL_ONLY
- Mixed/shared runtime storage: BLOCKED pending new explicit architecture approval
- Controlled-pilot external integrations: 2
- External graph providers: NONE_APPROVED
- External forecasting providers: NONE_APPROVED
- External reporting/publishing providers: NONE_APPROVED
- External coverage providers: NONE_APPROVED
- External notification providers: NONE_APPROVED
- External translation provider: NONE_APPROVED
- Production/global external integrations: NONE_APPROVED
- Backend Action API foundation: VALIDATED_LOCAL_READ_ONLY
- Private GPT backend Action connection: NOT_CONNECTED
- Backend HTTPS deployment: NOT_DEPLOYED
- Unattended cloud runtime: DEPLOYED_OWNER_ONLY_REAL_HOST_VALIDATED / NOT_PRODUCTION
- Admin dashboard deployment: NOT_DEPLOYED
- Public sharing: USER_DEFERRED_UNTIL_SEPARATE_REQUEST
- Shared production runtime: NOT_APPROVED
- Current engineering activity: E9A_OWNER_ONLY_PRODUCTION_RUNTIME_HARDENING / E9A.1_SINGLE_INSTANCE_RUNTIME_LEASE
- Next roadmap phase: NONE_APPROVED
- Production/live operational status: NOT_OPERATIONAL