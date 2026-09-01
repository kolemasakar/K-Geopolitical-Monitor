# ROADMAP

Version: 4.0
Status: APPROVED
Project: K-Geopolitical Monitor
Decision: `docs/decisions/POST_E9A_ROADMAP_V4_DECISION_2026-09-01.md`
Development analysis: `docs/analysis/KGM_SYSTEM_DEVELOPMENT_ANALYSIS_2026-09-01.md`

## Development Principle

K-Geopolitical Monitor is developed through explicit implementation and validation gates.

Implementation does not equal validation.
Validation does not equal production/live operation.
Publication does not equal production runtime maturity.

The validated architectural spine is preserved unless a later explicit architecture decision demonstrates a need to replace it.

Current strategic sequence:

`ENGINEERING PLATFORM -> INTELLIGENCE QUALITY -> SOURCE NETWORK -> OWNER OPERATIONALIZATION -> FORECAST CALIBRATION -> DELIVERY / QUALITY FEEDBACK -> OPTIONAL PUBLICATION -> OPTIONAL SHARED RUNTIME`

No M14 engineering label is created by ROADMAP v4.

## Permanent Truth / Epistemic Boundaries

All phases must preserve:
- publisher/publication is not automatically the underlying origin;
- repost/syndication/translation/citation does not create independent corroboration;
- an official statement establishes `actor said X`, not automatically `X happened`;
- source reputation is context and does not automatically determine claim truth;
- graph inference cannot promote factual verification or independent-origin count;
- forecast probability/confidence cannot promote present-tense factual verification;
- coverage confidence cannot promote factual verification confidence;
- GLOBAL is an intended scope key, not proof of exhaustive global coverage;
- missing local-language evidence remains an explicit coverage limitation;
- reconstructed search/tool history must never be labeled exact;
- unavailable persisted backend state must never be replaced by ad hoc public-web research;
- runtime-health instrumentation cannot imply unavailable coverage, source-health, uptime, verification or production facts.

## Storage / Runtime Boundary

Until a new architecture decision explicitly changes it:
- runtime storage remains `PROJECT_LOCAL_ONLY`;
- shared/mixed canonical runtime storage remains blocked;
- no cross-project canonical store may be mutated implicitly;
- the existing owner-only OCI runtime remains the validated runtime line;
- `PRODUCTION_LIVE = NOT_OPERATIONAL` until a separate launch-specific gate.

---

# Validated Historical Development Line

Detailed historical evidence remains canonical in `PROJECT_HISTORY.md`, phase-specific implementation records and checkpoints. ROADMAP v4 retains the phase/gate state without duplicating every historical run record.

## Phase 0 — Project Foundation

State: `APPROVED`

Established governance, documentation standards and product concept.

Gate: `PHASE_0_APPROVED`

## Phase 1 — Minimal Functional Core Specification

State: `BASELINE_VALIDATED`

Defined minimum contracts for sources, events, evidence, verification, forecasting and reports.

## Phase 2 — Minimal Functional Core Implementation

State: `BASELINE_VALIDATED`

Implemented the initial end-to-end functional core.

## Phase 3 — Core Validation and Calibration

State: `BASELINE_VALIDATED`

Validated evidence handling, contradictions, event lifecycle, forecast updates and reporting behavior at the then-current baseline.

## Phase 4 — Adaptive Learning Foundation

State: `BASELINE_VALIDATED`

Established baseline source/platform/relationship/forecast-change detection structures. ROADMAP v4 does not treat those baseline structures as a mature self-learning system.

## Phase 5 — Controlled Pilot Monitoring

State: `BASELINE_VALIDATED`

Validated project-local monitoring, controlled/live acquisition, provenance, source-failure isolation and operational findings.

Key live pilot sources:
- Consilium press-release RSS;
- GDELT DOC 2.0 discovery/index metadata.

Phase 5 did not establish production/global operation or exhaustive coverage.

## Phase 6 — Strategic Alerts and Continuous Monitoring

State: `BASELINE_VALIDATED`

Validated persisted alert policies, trigger thresholds, lifecycle, deduplication, restart persistence and cadence/priority separation.

## Phase 7 — Multi-Region Expansion

State: `BASELINE_VALIDATED`

Validated region/language registries, watch-scoped requirements, attribution, coverage reporting and translation-isolation semantics.

## Phase 8 — Advanced Geopolitical Graph

State: `BASELINE_VALIDATED`

Validated durable project-local graph identity, lifecycle/history, temporal snapshots, bounded traversal and explainable queries.

Graph inference remains analytical context and cannot become independent factual evidence.

## Phase 9 — Advanced Forecasting

State: `BASELINE_VALIDATED`

Validated durable forecast/scenario identity, immutable version history, typed provenance, outcome/evaluation and calibration-history structures.

Forecast probability semantics remain isolated from factual verification.

## Phase 10 — Full Reporting Environment

State: `BASELINE_VALIDATED`

Validated immutable report snapshots, common assembly, structured/Markdown rendering and source/graph/forecast/coverage separation.

## Phase 11 — Global Operational Coverage

State: `BASELINE_VALIDATED`

Validated explicit coverage contracts, source/region/language/freshness dimensions, persisted snapshots/results and distinct `coverage_ratio` / `coverage_confidence` semantics.

GLOBAL remains scope, not proof of complete global monitoring.

---

# Validated Post-Phase-11 Workstreams

## Owner-Only Private GPT Pilot

State: `OWNER_ONLY_PILOT_PASS`

Final truth-boundary matrix: `18/18 PASS`.

The GPT remains a user interaction/orchestration surface; it is not the unattended runtime or canonical persisted-state source.

## E1 — Automatic Translation Foundation

State: `BASELINE_VALIDATED`

Original raw text remains immutable; translations are derived/versioned representations and do not create independent-origin credit.

## E2 — Source Reputation and Status History

State: `BASELINE_VALIDATED`

Append-only reputation/status history is validated. `COMPROMISED` is not an automatic FALSE operator.

## E3 — Private GPT Backend Action API

State: `BASELINE_VALIDATED / NOT_CONNECTED`

Owner-only read-only FastAPI persisted-state facade validated.

Current exposure state:
- backend HTTPS: `NOT_DEPLOYED`;
- private GPT Action connection: `NOT_CONNECTED`;
- public backend/API: `NOT_APPROVED / NOT_DEPLOYED`.

## E4 — Free Unattended Runtime Deployment

State: `REAL_HOST_VALIDATED_WITH_OWNER_SECURITY_EXCEPTIONS`

Real OCI Ubuntu 24.04 ARM64 unattended runtime validated including reboot/recovery and controlled live collection.

## E5 — Admin Read-Only Dashboard

State: `BASELINE_VALIDATED / LOCAL_PROTECTED / READ_ONLY / NOT_DEPLOYED`

No parallel dashboard store is approved.

## E6 — Reproducibility Instrumentation

State: `BASELINE_VALIDATED`

Exact instrumented query/cut-off capture, adapter fingerprints, source-attempt linkage and persisted-artifact hashing validated. Missing history remains `NOT_INSTRUMENTED`, not reconstructed.

## E7 — Forecast Probability Semantics

State: `BASELINE_VALIDATED`

Canonical semantic contract separates raw probability, calibrated probability and scenario confidence; none can promote factual verification.

## E8 — Controlled External Sharing / Public GPT

State: `USER_DEFERRED_UNTIL_SEPARATE_REQUEST`

Earlier publication-readiness design/preflight remains historical preparation. Actual Business migration, public sharing, publication or public Action remains inactive.

ROADMAP v4 maps any future publication work to conditional Phase 17.

## E9A — Owner-Only Production Runtime Hardening

State: `OWNER_ONLY_PRODUCTION_CANDIDATE_READY / COMPLETE`

Validated sub-gates:
- E9A.1 single-instance runtime lease;
- E9A.2 canonical SQLite runtime profile;
- E9A.3 backup/disaster recovery with real-host restore drill;
- E9A.4 owner-only runtime health;
- E9A.5 deployment/security hardening;
- E9A.6 x64/native-ARM64/real-host validation matrix.

Canonical result:
`docs/implementation/E9A_6_VALIDATION_MATRIX_RESULT.md`

Canonical checkpoint:
`docs/checkpoints/PROJECT_CHECKPOINT_2026-09-01_E9A_RUNTIME_HARDENING_CANDIDATE_READY.md`

Owner-approved candidate security exceptions remain explicit:
- public SSH TCP/22 from `0.0.0.0/0`;
- broad outbound egress.

Unnecessary rpcbind TCP/UDP port 111 was removed and absence after physical reboot was validated.

## E9 — Shared Production Runtime

State: `DEFERRED / NOT_APPROVED`

ROADMAP v4 maps any future shared/team runtime work to conditional Phase 18 and requires a new architecture ADR.

---

# ROADMAP v4 Development Line

## Phase 12 — Intelligence Quality and Source Network Foundation

State: `APPROVED / NEXT / ACTIVE_ENGINEERING_PHASE`

Objective:
Build a materially broader, measurable and maintainable public-source network and modernize the source-adapter operating model without weakening current provenance/coverage semantics or claiming exhaustive global monitoring.

### P12.0 — Canonical Architecture / Security / Integration Convergence

State: `NEXT`

Tasks:
- synchronize `ARCHITECTURE.md` to post-E9A / ROADMAP v4 state;
- synchronize `SECURITY_AND_DATA_POLICY.md` to completed E9A.6 evidence;
- synchronize `EXTERNAL_INTEGRATIONS.md` to the current candidate-ready runtime and Phase 12 integration policy;
- review other canonical secondary documents for stale current-state claims;
- preserve historical decision records rather than rewriting accepted ADR/decision history.

Gate:
`P12_0_CANONICAL_CONVERGENCE_VALIDATED`

### P12.1 — Source Portfolio Contract and Governance

State: `PLANNED`

Define a versioned source-portfolio model covering:
- source identity and underlying-origin characteristics;
- source class;
- region/language scope;
- ownership/operator responsibility;
- public/free/credentialed access mode;
- licensing/terms notes where relevant;
- expected freshness/cadence;
- adapter/parser identity;
- fallback/replacement sources;
- availability/degradation state;
- data classification;
- required outbound destination/protocol;
- provenance and independence constraints.

Prefer public/free sources first. No paid provider is approved by this phase definition alone.

Gate:
`P12_1_SOURCE_PORTFOLIO_CONTRACT_VALIDATED`

### P12.2 — Live Adapter Framework v2

State: `PLANNED`

Goals:
- preserve HTTPS/read-only/fail-closed acquisition;
- support reusable configurable RSS/Atom/JSON/HTML-public adapters where appropriate;
- bounded timeouts, payload size, pagination and record limits;
- deterministic adapter/source identity;
- collection-attempt and reproducibility linkage;
- source-specific parsing without cross-source failure propagation;
- deterministic fixture tests independent of live network availability.

Gate:
`P12_2_ADAPTER_FRAMEWORK_V2_VALIDATED`

### P12.3 — Priority Authoritative Source Pack

State: `PLANNED`

Expand authoritative/public source coverage with a prioritized set of international organizations and official government/institutional sources.

Candidate classes include, subject to source-specific review:
- UN system;
- EU institutions;
- NATO;
- OSCE;
- major foreign-affairs/defence/government sources;
- sanctions/regulatory/public legal sources;
- humanitarian/security institutions.

Every source requires an explicit integration record. Source count must not be treated as independent corroboration count.

Gate:
`P12_3_AUTHORITATIVE_SOURCE_PACK_VALIDATED`

### P12.4 — Local-Language and Media Discovery Pack

State: `PLANNED`

Goals:
- materially expand region/language discovery beyond the two-source pilot;
- preserve explicit publisher/underlying-origin distinction;
- retain translation as a derived representation only;
- retain syndication/citation/repost uncertainty when underlying origin is not established;
- expose missing local-language coverage as a gap rather than silently masking it.

Gate:
`P12_4_LOCAL_LANGUAGE_DISCOVERY_VALIDATED`

### P12.5 — Source Health, Freshness and Egress Inventory

State: `PLANNED`

Goals:
- operational source availability/freshness measurements over the expanded portfolio;
- adapter failure-rate and degradation visibility;
- source-drift observations without opaque automatic truth-policy changes;
- explicit required outbound destination/protocol inventory;
- identify safe least-privilege egress candidates only after real source requirements are known.

Broad egress remains an explicit exception until this inventory is validated and a security change is separately approved.

Gate:
`P12_5_SOURCE_HEALTH_EGRESS_INVENTORY_VALIDATED`

### P12.6 — Phase 12 Validation Matrix

State: `PLANNED`

Required evidence:
- full x64 regression;
- full native ARM64 regression;
- deterministic adapter/source fixtures;
- controlled live source matrix;
- source-failure isolation;
- provenance/origin invariants;
- region/language/coverage invariants;
- reproducibility linkage;
- no shared/mixed canonical storage;
- no public API/dashboard ingress;
- no production/live activation.

Phase gate:
`PHASE_12_INTELLIGENCE_SOURCE_NETWORK_FOUNDATION_VALIDATED`

---

## Phase 13 — Semantic Verification and Provenance Intelligence

State: `APPROVED_SEQUENTIAL / NOT_STARTED`

Objective:
Replace title/domain-level analytical shortcuts with richer structured claim, provenance, evidence-relation and contradiction reasoning while preserving fail-closed truth promotion.

Planned scope:
- typed semantic claim model: actor/proposition/object/scope/time/location/modality/attribution;
- extraction proposal layer distinct from accepted canonical claim state;
- semantic claim identity/merge/split rules;
- explicit citation/syndication/repost/translation/underlying-origin relationships;
- provenance/origin graph with uncertainty state;
- evidence-type and source-proximity classification;
- first-class typed contradictions by disputed dimension;
- contradiction lifecycle/resolution;
- verification engine v2 using evidence type, independence, proximity, freshness, reputation and contradiction dimensions;
- decomposed confidence dimensions rather than one opaque scalar;
- adversarial/historical replay validation;
- model/LLM-assisted extraction may propose objects but cannot directly promote verification state.

Phase gate:
`PHASE_13_SEMANTIC_VERIFICATION_PROVENANCE_VALIDATED`

---

## Phase 14 — Owner Operational Intelligence Activation

State: `APPROVED_SEQUENTIAL / NOT_STARTED`

Objective:
Turn the validated platform into a practical owner-operated intelligence system while maintaining owner-only access and an explicit launch gate.

Planned scope:
- safe owner-only dashboard access path;
- owner-only persisted-state interaction path, including evaluation of a private GPT/backend connection without public owner API exposure;
- daily/priority brief workflow derived from canonical persisted state;
- operator alert-review workflow;
- long-run/soak operational evidence;
- source portfolio operating procedures;
- encrypted off-host backup evaluation/validation;
- SSH/private-admin disposition gate;
- egress least-privilege decision based on Phase 12 inventory;
- operational kill/recovery/runbook consolidation;
- owner-only launch-specific readiness matrix.

Phase completion does **not** automatically set production/live operational status.

Required separate activation decision after validation:
`OWNER_ONLY_OPERATIONAL_ACTIVATION = OWNER_DECISION_REQUIRED`

Phase gate:
`PHASE_14_OWNER_OPERATIONAL_INTELLIGENCE_READY`

---

## Phase 15 — Forecast Calibration and Performance Intelligence

State: `APPROVED_SEQUENTIAL / NOT_STARTED`

Objective:
Turn the existing forecast governance/persistence framework into a measurable forecasting capability without false numerical precision.

Planned scope:
- traceable forecast signal/feature contract;
- reference classes and base-rate inputs where defensible;
- analyst/model/combined probability-generation provenance;
- explicit rationale and assumptions;
- resolved forecast scoring;
- Brier/log-score or other approved calibration metrics;
- calibration by horizon/domain where sample size permits;
- baseline vs analyst vs model vs combined comparison;
- no forecast metric may promote present factual verification;
- performance uncertainty and small-sample limitations remain explicit.

Phase gate:
`PHASE_15_FORECAST_CALIBRATION_PERFORMANCE_VALIDATED`

---

## Phase 16 — Delivery, Operator Experience and Quality Feedback

State: `APPROVED_SEQUENTIAL / NOT_STARTED`

Objective:
Complete the owner intelligence loop from persisted alert/brief generation to useful delivery and measurable quality feedback.

Planned scope:
- provider-neutral notification/delivery abstraction;
- exactly one owner-approved delivery channel for first validation;
- priority/dedup/update/resolution delivery policy;
- delivery audit/retry/failure isolation;
- redaction/data-minimization rules;
- operator feedback and usefulness/correction capture;
- source/adapter/extraction/verification quality metrics;
- forecast quality feedback integration;
- source drift and reliability-review workflow;
- periodic quality review and calibration loop;
- no opaque self-modifying truth policy;
- Start.me, if used, remains `PUBLIC_NON_SENSITIVE_ONLY` and non-canonical.

Phase gate:
`PHASE_16_DELIVERY_OPERATOR_QUALITY_LOOP_VALIDATED`

---

# Conditional / Owner-Gated Future Phases

## Phase 17 — Controlled External Publication Readiness

State: `CONDITIONAL / NOT_ACTIVATED`

This phase is **not approved for implementation by roadmap sequencing alone**.

Activation requires a separate explicit owner publication decision after Phase 14–16 owner-value evidence is reviewed.

Potential scope only after activation:
- current ChatGPT Business/workspace eligibility and publishing-rule recheck;
- public GPT name/description/instructions/category/conversation starters;
- privacy/disclosure and capability review;
- public adversarial truth/safety matrix;
- sanitized external read-only facade only if separately approved;
- separate external credential;
- HTTPS/TLS, trusted-host, rate/abuse/request controls;
- public Privacy Policy if an Action is used;
- rollback/unpublish/credential-revocation kill switch;
- final owner publication gate.

Forbidden shortcut:
The existing E3 owner/admin API must not become the public API contract.

Activation gate:
`PHASE_17_ACTIVATION_REQUIRES_EXPLICIT_OWNER_DECISION`

## Phase 18 — Shared / Team Runtime

State: `CONDITIONAL / NEW_ARCHITECTURE_APPROVAL_REQUIRED`

This phase is not approved for implementation until a demonstrated multi-user/team requirement exists.

Required before activation:
- explicit owner request;
- new architecture ADR;
- canonical Source-of-Truth decision;
- tenancy/RBAC model;
- concurrency/transaction model;
- storage technology evaluation based on measured need;
- backup/DR/security/migration strategy;
- no silent mixed storage during transition.

Current SQLite/project-local canonical runtime remains valid until evidence shows it is insufficient.

Activation gate:
`PHASE_18_REQUIRES_NEW_ARCHITECTURE_APPROVAL`

---

# Current Implementation Checkpoint

- Product Concept: `APPROVED`
- Roadmap: `APPROVED / v4.0`
- Engineering baseline: validated through ROADMAP Phase 11 plus E1–E7 and E9A
- Owner-only private GPT pilot: `SUCCESSFUL / 18 of 18 PASS`
- E8 Controlled External Sharing / Public GPT: `USER_DEFERRED`
- E9A Owner-Only Production Runtime Hardening: `OWNER_ONLY_PRODUCTION_CANDIDATE_READY / COMPLETE`
- E9 Shared Production Runtime: `NOT_APPROVED`
- Runtime storage: `PROJECT_LOCAL_ONLY`
- Mixed/shared runtime storage: `BLOCKED pending new explicit architecture approval`
- Owner-only OCI runtime: `REAL_HOST_VALIDATED / OWNER_ONLY_PRODUCTION_CANDIDATE_READY / NOT_PRODUCTION`
- Private GPT backend Action connection: `NOT_CONNECTED`
- Backend HTTPS deployment: `NOT_DEPLOYED`
- Admin dashboard deployment: `NOT_DEPLOYED`
- Public sharing: `NOT_ACTIVE`
- Production/live operational status: `NOT_OPERATIONAL`

Current engineering activity:
`PHASE_12 / P12.0_CANONICAL_ARCHITECTURE_SECURITY_INTEGRATION_CONVERGENCE`

Next gate:
`P12_0_CANONICAL_CONVERGENCE_VALIDATED`

Next numbered roadmap phase:
`PHASE_12_APPROVED / ACTIVE_ENGINEERING_PHASE`

Conditional future publication:
`PHASE_17_NOT_ACTIVATED`

Conditional shared/team runtime:
`PHASE_18_NEW_ARCHITECTURE_APPROVAL_REQUIRED`
