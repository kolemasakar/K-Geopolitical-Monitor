# ROADMAP

Version: 4.2
Status: APPROVED
Project: K-Geopolitical Monitor
Strategic roadmap: v4
Decision: `docs/decisions/POST_E9A_ROADMAP_V4_DECISION_2026-09-01.md`
Development analysis: `docs/analysis/KGM_SYSTEM_DEVELOPMENT_ANALYSIS_2026-09-01.md`

## Development Principle

K-Geopolitical Monitor advances through explicit implementation and validation gates.

Implementation does not equal validation.
Validation does not equal production/live operation.
Publication does not equal production runtime maturity.

Strategic sequence:

`ENGINEERING PLATFORM -> INTELLIGENCE QUALITY -> SOURCE NETWORK -> OWNER OPERATIONALIZATION -> FORECAST CALIBRATION -> DELIVERY / QUALITY FEEDBACK -> OPTIONAL PUBLICATION -> OPTIONAL SHARED RUNTIME`

No M14 engineering label is created by ROADMAP v4.

## Permanent Truth / Epistemic Boundaries

All phases preserve:

- publisher/publication is not automatically the underlying origin;
- repost/syndication/translation/citation does not create independent corroboration;
- an official statement establishes `actor said X`, not automatically `X happened`;
- source reputation and source-portfolio metadata are context/governance, not truth operators;
- graph inference cannot promote factual verification or independent-origin count;
- forecast probability/confidence cannot promote factual verification;
- coverage confidence cannot promote factual verification confidence;
- `GLOBAL` is scope, not proof of exhaustive global coverage;
- missing local-language evidence remains explicit;
- reconstructed/uninstrumented tool history is never labeled exact;
- unavailable persisted backend state is never replaced by ad hoc web research;
- runtime-health data cannot imply unavailable coverage/source-health/verification/production facts.

## Storage / Runtime Boundary

Until a new architecture decision explicitly changes it:

- runtime storage remains `PROJECT_LOCAL_ONLY`;
- shared/mixed canonical runtime storage remains blocked;
- no direct cross-project canonical-store mutation is allowed;
- owner-only OCI remains the validated runtime line;
- public KGM API/dashboard ingress remains not approved/deployed;
- `PRODUCTION_LIVE = NOT_OPERATIONAL`.

Production/live operational status: NOT_OPERATIONAL
Runtime storage mode: PROJECT_LOCAL_ONLY

# Validated Historical Development Line

- Phase 0 — Project Foundation: `APPROVED`.
- Phase 1 — Minimal Functional Core Specification: `BASELINE_VALIDATED`.
- Phase 2 — Minimal Functional Core Implementation: `BASELINE_VALIDATED`.
- Phase 3 — Core Validation and Calibration: `BASELINE_VALIDATED`.
- Phase 4 — Adaptive Learning Foundation: `BASELINE_VALIDATED`.
- Phase 5 — Controlled Pilot Monitoring: `BASELINE_VALIDATED`.
- Phase 6 — Strategic Alerts and Continuous Monitoring: `BASELINE_VALIDATED`.
- Phase 7 — Multi-Region Expansion: `BASELINE_VALIDATED`.
- Phase 8 — Advanced Geopolitical Graph: `BASELINE_VALIDATED`.
- Phase 9 — Advanced Forecasting: `BASELINE_VALIDATED`.
- Phase 10 — Full Reporting Environment: `BASELINE_VALIDATED`.
- Phase 11 — Global Operational Coverage: `BASELINE_VALIDATED`.

GLOBAL remains an explicit configured scope key, not proof of complete global monitoring.

# Validated Post-Phase-11 Workstreams

- Owner-only private GPT pilot: `18/18 PASS`.
- E1 Automatic Translation Foundation: `BASELINE_VALIDATED`.
- E2 Source Reputation and Status History: `BASELINE_VALIDATED`.
- E3 Private GPT Backend Action API: `BASELINE_VALIDATED / NOT_CONNECTED`.
- E4 Free Unattended Runtime Deployment: `REAL_HOST_VALIDATED_WITH_OWNER_SECURITY_EXCEPTIONS`.
- E5 Admin Read-Only Dashboard: `BASELINE_VALIDATED / LOCAL_PROTECTED / READ_ONLY / NOT_DEPLOYED`.
- E6 Reproducibility Instrumentation: `BASELINE_VALIDATED`.
- E7 Forecast Probability Semantics: `BASELINE_VALIDATED`.
- E8 Controlled External Sharing / Public GPT: `USER_DEFERRED_UNTIL_SEPARATE_REQUEST`.
- E9A Owner-Only Production Runtime Hardening: `OWNER_ONLY_PRODUCTION_CANDIDATE_READY / COMPLETE`.
- E9 Shared Production Runtime: `DEFERRED / NOT_APPROVED`.

E9A retains explicit owner-approved candidate networking exceptions:

- public SSH TCP/22 from `0.0.0.0/0`;
- broad outbound egress.

# ROADMAP v4 Development Line

## Phase 12 — Intelligence Quality and Source Network Foundation

State: `APPROVED / ACTIVE_ENGINEERING_PHASE`

Objective: materially broaden and govern the public-source network while preserving provenance, verification and coverage isolation.

### P12.0 — Canonical Architecture / Security / Integration Convergence

State: `VALIDATED`

Gate: `P12_0_CANONICAL_CONVERGENCE_VALIDATED`

Result: `docs/implementation/P12_0_CANONICAL_CONVERGENCE_RESULT.md`

Checkpoint: `docs/checkpoints/PROJECT_CHECKPOINT_2026-09-01_P12_0_CANONICAL_CONVERGENCE_VALIDATED.md`

Validation: commit `374beb4664cd92a4f41063cbbe30f6830ee3a831`; CI run `33517021594`, job `99886494759`; `318 passed, 1 warning / SUCCESS`.

### P12.1 — Source Portfolio Contract and Governance

State: `VALIDATED`

Gate: `P12_1_SOURCE_PORTFOLIO_CONTRACT_VALIDATED`

Implementation: `docs/implementation/P12_1_SOURCE_PORTFOLIO_CONTRACT.md`

Result: `docs/implementation/P12_1_SOURCE_PORTFOLIO_CONTRACT_RESULT.md`

Checkpoint: `docs/checkpoints/PROJECT_CHECKPOINT_2026-09-01_P12_1_SOURCE_PORTFOLIO_CONTRACT_VALIDATED.md`

Validation: commit `905a727d85701bf43d18de2d5216b83ab9a2b8bd`; CI run `33520371480`, job `99897786494`; `334 passed, 1 warning / SUCCESS`.

P12.1 establishes:

- additive migration `022_source_portfolio_contract.sql`;
- immutable versioned `source_portfolio_versions`;
- source identity/class/role, region/language, access/cost/authentication, freshness/cadence, adapter identity, outbound host/protocol, fallback, availability, data classification, provenance/independence, terms, owner/reviewer and review state;
- paid-provider approval fail-closed;
- explicit non-activation and truth/verification/coverage isolation.

P12.1 activates no new source and approves no paid provider.

### P12.2 — Live Adapter Framework v2

State: `NEXT / NOT_STARTED`

Goals:

- reusable HTTPS read-only fail-closed transport;
- RSS/Atom/JSON/public-adapter framework;
- bounded timeout, payload, pagination and record limits;
- deterministic source/adapter identity;
- source-portfolio governance linkage;
- collection-attempt/reproducibility linkage;
- source-specific parsing and failure isolation;
- deterministic fixtures independent of live network availability.

Gate: `P12_2_ADAPTER_FRAMEWORK_V2_VALIDATED`

### P12.3 — Priority Authoritative Source Pack

State: `PLANNED`

Expand prioritized official/institutional public-source coverage. Every source requires an explicit portfolio/integration record. Source/domain/adapter count is not independent corroboration count.

Gate: `P12_3_AUTHORITATIVE_SOURCE_PACK_VALIDATED`

### P12.4 — Local-Language and Media Discovery Pack

State: `PLANNED`

Expand priority region/language discovery while retaining publisher/underlying-origin uncertainty, translation isolation and explicit local-language gaps.

Gate: `P12_4_LOCAL_LANGUAGE_DISCOVERY_VALIDATED`

### P12.5 — Source Health, Freshness and Egress Inventory

State: `PLANNED`

Measure source availability/freshness/degradation and build the real outbound host/protocol inventory before any egress restriction decision.

Gate: `P12_5_SOURCE_HEALTH_EGRESS_INVENTORY_VALIDATED`

### P12.6 — Phase 12 Validation Matrix

State: `PLANNED`

Required evidence includes full x64/native ARM64 regression, deterministic adapter/source fixtures, controlled-live source matrix, provenance/origin invariants, region/language/coverage isolation, reproducibility linkage, failure isolation, `PROJECT_LOCAL_ONLY`, no public ingress and no production/live activation.

Phase gate: `PHASE_12_INTELLIGENCE_SOURCE_NETWORK_FOUNDATION_VALIDATED`

## Phase 13 — Semantic Verification and Provenance Intelligence

State: `APPROVED_SEQUENTIAL / NOT_STARTED`

Objective: richer structured claim/provenance/evidence-relation/contradiction reasoning with fail-closed truth promotion.

Gate: `PHASE_13_SEMANTIC_VERIFICATION_PROVENANCE_VALIDATED`

## Phase 14 — Owner Operational Intelligence Activation

State: `APPROVED_SEQUENTIAL / NOT_STARTED`

Objective: practical owner-operated intelligence with owner-only access, operational workflows, soak evidence, source operations, backup/admin/egress decisions and a separate launch-specific gate.

Required separate activation decision:
`OWNER_ONLY_OPERATIONAL_ACTIVATION = OWNER_DECISION_REQUIRED`

Gate: `PHASE_14_OWNER_OPERATIONAL_INTELLIGENCE_READY`

## Phase 15 — Forecast Calibration and Performance Intelligence

State: `APPROVED_SEQUENTIAL / NOT_STARTED`

Objective: measurable forecast calibration without false numerical precision.

Gate: `PHASE_15_FORECAST_CALIBRATION_PERFORMANCE_VALIDATED`

## Phase 16 — Delivery, Operator Experience and Quality Feedback

State: `APPROVED_SEQUENTIAL / NOT_STARTED`

Objective: provider-neutral owner delivery, audit/retry/failure isolation, redaction/minimization, operator feedback and quality metrics. Start.me remains public/non-sensitive and non-canonical if used.

Gate: `PHASE_16_DELIVERY_OPERATOR_QUALITY_LOOP_VALIDATED`

# Conditional / Owner-Gated Future Phases

## Phase 17 — Controlled External Publication Readiness

State: `CONDITIONAL / NOT_ACTIVATED`

Activation requires a separate explicit owner publication decision.

Gate: `PHASE_17_ACTIVATION_REQUIRES_EXPLICIT_OWNER_DECISION`

## Phase 18 — Shared / Team Runtime

State: `CONDITIONAL / NEW_ARCHITECTURE_APPROVAL_REQUIRED`

Activation requires explicit owner request, new architecture ADR, Source-of-Truth/tenancy/concurrency/storage/backup/security/migration decisions and no silent mixed storage.

Gate: `PHASE_18_REQUIRES_NEW_ARCHITECTURE_APPROVAL`

# Current Implementation Checkpoint

- Product Concept: `APPROVED`
- Strategic ROADMAP: `APPROVED / v4`
- State synchronization: `v4.2`
- Engineering baseline: validated through Phase 11 + E1-E7 + E9A
- Phase 12 P12.0: `VALIDATED`
- Phase 12 P12.1: `P12_1_SOURCE_PORTFOLIO_CONTRACT_VALIDATED`
- Current/next engineering activity: `P12.2_LIVE_ADAPTER_FRAMEWORK_V2 / NEXT_NOT_STARTED`
- Runtime storage: `PROJECT_LOCAL_ONLY`
- Mixed/shared runtime storage: `BLOCKED`
- Production/live operational status: `NOT_OPERATIONAL`
- Private GPT Action: `NOT_CONNECTED`
- Backend HTTPS: `NOT_DEPLOYED`
- Admin dashboard: `NOT_DEPLOYED`
- Public sharing: `NOT_ACTIVE`
- Paid providers: `NONE_APPROVED`

Next gate:
`P12_2_ADAPTER_FRAMEWORK_V2_VALIDATED`
