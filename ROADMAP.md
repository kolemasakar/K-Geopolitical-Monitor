# ROADMAP

Version: 4.1
Status: APPROVED
Project: K-Geopolitical Monitor
Decision: `docs/decisions/POST_E9A_ROADMAP_V4_DECISION_2026-09-01.md`
Development analysis: `docs/analysis/KGM_SYSTEM_DEVELOPMENT_ANALYSIS_2026-09-01.md`

## Development Principle

K-Geopolitical Monitor is developed through explicit implementation and validation gates.

Implementation does not equal validation. Validation does not equal production/live operation. Publication does not equal production runtime maturity.

The validated architectural spine is preserved unless a later explicit architecture decision demonstrates a need to replace it.

Strategic sequence:
`ENGINEERING PLATFORM -> INTELLIGENCE QUALITY -> SOURCE NETWORK -> OWNER OPERATIONALIZATION -> FORECAST CALIBRATION -> DELIVERY / QUALITY FEEDBACK -> OPTIONAL PUBLICATION -> OPTIONAL SHARED RUNTIME`

No M14 engineering label is created by ROADMAP v4.

## Permanent Truth / Epistemic Boundaries

All phases preserve:
- publisher/publication is not automatically the underlying origin;
- repost/syndication/translation/citation does not create independent corroboration;
- official statements establish `actor said X`, not automatically `X happened`;
- source reputation is context and does not automatically determine claim truth;
- graph inference cannot promote factual verification or independent-origin count;
- forecast probability/confidence cannot promote factual verification;
- coverage confidence cannot promote factual verification confidence;
- `GLOBAL` is intended scope, not proof of exhaustive global coverage;
- missing local-language evidence remains explicit;
- reconstructed search/tool history is never labeled exact;
- unavailable persisted backend state is never replaced by ad hoc public-web research;
- runtime-health instrumentation cannot imply unavailable coverage/source-health/uptime/verification/production facts.

## Storage / Runtime Boundary

Until a new architecture decision changes it:
- runtime storage remains `PROJECT_LOCAL_ONLY`;
- shared/mixed canonical runtime storage remains blocked;
- no cross-project canonical store may be mutated implicitly;
- the owner-only OCI runtime remains the validated runtime line;
- `PRODUCTION_LIVE = NOT_OPERATIONAL` until a separate launch-specific gate.

# Validated Historical Development Line

## Phase 0 — Project Foundation
State: `APPROVED`

## Phase 1 — Minimal Functional Core Specification
State: `BASELINE_VALIDATED`

## Phase 2 — Minimal Functional Core Implementation
State: `BASELINE_VALIDATED`

## Phase 3 — Core Validation and Calibration
State: `BASELINE_VALIDATED`

## Phase 4 — Adaptive Learning Foundation
State: `BASELINE_VALIDATED`

## Phase 5 — Controlled Pilot Monitoring
State: `BASELINE_VALIDATED`

Validated project-local monitoring, controlled/live acquisition, provenance, source-failure isolation and operational findings. Starting live sources: Consilium RSS and GDELT DOC 2.0. This did not establish exhaustive global coverage.

## Phase 6 — Strategic Alerts and Continuous Monitoring
State: `BASELINE_VALIDATED`

## Phase 7 — Multi-Region Expansion
State: `BASELINE_VALIDATED`

## Phase 8 — Advanced Geopolitical Graph
State: `BASELINE_VALIDATED`
Graph inference remains analytical context, not independent factual evidence.

## Phase 9 — Advanced Forecasting
State: `BASELINE_VALIDATED`
Forecast semantics remain isolated from factual verification.

## Phase 10 — Full Reporting Environment
State: `BASELINE_VALIDATED`
Presentation cannot strengthen upstream truth.

## Phase 11 — Global Operational Coverage
State: `BASELINE_VALIDATED`
`GLOBAL` remains scope, not proof of complete global monitoring.

# Validated Post-Phase-11 Workstreams

## Owner-Only Private GPT Pilot
State: `OWNER_ONLY_PILOT_PASS / 18_OF_18`
The GPT is an interaction/orchestration surface, not the unattended runtime or canonical persisted-state source.

## E1 — Automatic Translation Foundation
State: `BASELINE_VALIDATED`
Translations are derived/versioned representations and do not create independent-origin credit.

## E2 — Source Reputation and Status History
State: `BASELINE_VALIDATED`
Reputation/status history is context, not an automatic FALSE/truth operator.

## E3 — Private GPT Backend Action API
State: `BASELINE_VALIDATED / NOT_CONNECTED`
Backend HTTPS: `NOT_DEPLOYED`; public backend/API: `NOT_APPROVED / NOT_DEPLOYED`.

## E4 — Free Unattended Runtime Deployment
State: `REAL_HOST_VALIDATED_WITH_OWNER_SECURITY_EXCEPTIONS`
Real OCI Ubuntu 24.04 ARM64 runtime validated including reboot/recovery and controlled live collection.

## E5 — Admin Read-Only Dashboard
State: `BASELINE_VALIDATED / LOCAL_PROTECTED / READ_ONLY / NOT_DEPLOYED`

## E6 — Reproducibility Instrumentation
State: `BASELINE_VALIDATED`
Missing history remains `NOT_INSTRUMENTED`, not reconstructed.

## E7 — Forecast Probability Semantics
State: `BASELINE_VALIDATED`
Raw probability, calibrated probability and scenario confidence remain separate and cannot promote factual verification.

## E8 — Controlled External Sharing / Public GPT
State: `USER_DEFERRED_UNTIL_SEPARATE_REQUEST`
Future publication work maps to conditional Phase 17.

## E9A — Owner-Only Production Runtime Hardening
State: `OWNER_ONLY_PRODUCTION_CANDIDATE_READY / COMPLETE`

Validated: single-instance lease, canonical SQLite runtime profile, backup/DR real-host drill, owner-only runtime health, systemd/security hardening and x64/native-ARM64/real-host validation matrix.

Canonical result: `docs/implementation/E9A_6_VALIDATION_MATRIX_RESULT.md`
Canonical checkpoint: `docs/checkpoints/PROJECT_CHECKPOINT_2026-09-01_E9A_RUNTIME_HARDENING_CANDIDATE_READY.md`

Owner-approved candidate exceptions remain public SSH TCP/22 from `0.0.0.0/0` and broad outbound egress. rpcbind TCP/UDP port 111 was removed and persistent absence after reboot validated.

## E9 — Shared Production Runtime
State: `DEFERRED / NOT_APPROVED`
Future shared/team runtime work maps to conditional Phase 18 and requires a new architecture ADR.

# ROADMAP v4 Development Line

## Phase 12 — Intelligence Quality and Source Network Foundation

State: `APPROVED / ACTIVE_ENGINEERING_PHASE`

Objective: build a materially broader, measurable and maintainable public-source network and modernize the source-adapter operating model without weakening provenance/coverage semantics or claiming exhaustive global monitoring.

### P12.0 — Canonical Architecture / Security / Integration Convergence

State: `VALIDATED`
Gate: `P12_0_CANONICAL_CONVERGENCE_VALIDATED`
Result: `docs/implementation/P12_0_CANONICAL_CONVERGENCE_RESULT.md`
Checkpoint: `docs/checkpoints/PROJECT_CHECKPOINT_2026-09-01_P12_0_CANONICAL_CONVERGENCE_VALIDATED.md`
Validation commit: `374beb4664cd92a4f41063cbbe30f6830ee3a831`
Validation CI: run `33517021594`, job `99886494759`, `318 passed, 1 warning / SUCCESS`.

### P12.1 — Source Portfolio Contract and Governance

State: `NEXT / NOT_STARTED`

Define a versioned source-portfolio model covering source identity and underlying-origin characteristics, source class/role, region/language scope, ownership/operator responsibility, public/free/credentialed access, licensing/terms notes, freshness/cadence, adapter/parser identity, fallback/replacement, availability/degradation, data classification, required outbound destination/protocol, provenance/independence constraints and review status.

Prefer public/free sources first. No paid provider is approved by this phase alone.

Gate: `P12_1_SOURCE_PORTFOLIO_CONTRACT_VALIDATED`

### P12.2 — Live Adapter Framework v2
State: `PLANNED`
Goals: reusable read-only fail-closed transport, RSS/Atom/JSON/public-adapter support, bounded resource limits, deterministic adapter/source identity, collection/reproducibility linkage, failure isolation and deterministic fixtures.
Gate: `P12_2_ADAPTER_FRAMEWORK_V2_VALIDATED`

### P12.3 — Priority Authoritative Source Pack
State: `PLANNED`
Expand authoritative public coverage across prioritized international organizations and official government/institutional sources. Every source requires an explicit integration record; source count is not independent corroboration count.
Gate: `P12_3_AUTHORITATIVE_SOURCE_PACK_VALIDATED`

### P12.4 — Local-Language and Media Discovery Pack
State: `PLANNED`
Expand priority region/language discovery while retaining underlying-origin uncertainty, translation isolation and explicit local-language gaps.
Gate: `P12_4_LOCAL_LANGUAGE_DISCOVERY_VALIDATED`

### P12.5 — Source Health, Freshness and Egress Inventory
State: `PLANNED`
Measure availability/freshness/degradation and build the real source/service outbound domain/protocol inventory before any egress restriction decision.
Gate: `P12_5_SOURCE_HEALTH_EGRESS_INVENTORY_VALIDATED`

### P12.6 — Phase 12 Validation Matrix
State: `PLANNED`
Required evidence includes x64/native ARM64 regression, deterministic source/adapter fixtures, controlled-live source matrix, provenance/origin and coverage invariants, failure isolation, reproducibility linkage, `PROJECT_LOCAL_ONLY`, no public ingress and no production/live activation.
Phase gate: `PHASE_12_INTELLIGENCE_SOURCE_NETWORK_FOUNDATION_VALIDATED`

## Phase 13 — Semantic Verification and Provenance Intelligence
State: `APPROVED_SEQUENTIAL / NOT_STARTED`
Objective: richer structured claim/provenance/evidence-relation/contradiction reasoning with fail-closed truth promotion. Planned scope includes typed claims, proposal-vs-accepted state, semantic identity, provenance/origin relations, evidence type/proximity, typed contradictions, verification v2, decomposed confidence and adversarial replay. Model/LLM assistance may propose but cannot directly promote verification.
Gate: `PHASE_13_SEMANTIC_VERIFICATION_PROVENANCE_VALIDATED`

## Phase 14 — Owner Operational Intelligence Activation
State: `APPROVED_SEQUENTIAL / NOT_STARTED`
Objective: practical owner-operated intelligence with owner-only access. Planned scope includes safe dashboard/private persisted-state access, brief/alert review workflows, soak evidence, source operations, off-host backup evaluation, SSH/private-admin and egress decisions, runbooks and launch-specific readiness.
Phase completion does not automatically set production/live operational status.
Required separate activation decision: `OWNER_ONLY_OPERATIONAL_ACTIVATION = OWNER_DECISION_REQUIRED`.
Gate: `PHASE_14_OWNER_OPERATIONAL_INTELLIGENCE_READY`

## Phase 15 — Forecast Calibration and Performance Intelligence
State: `APPROVED_SEQUENTIAL / NOT_STARTED`
Objective: measurable forecast calibration without false precision. Planned scope includes traceable signals/features, base rates where defensible, probability-generation provenance, rationale/assumptions, resolved scoring, calibration metrics and baseline/analyst/model comparisons. Forecast metrics cannot promote factual verification.
Gate: `PHASE_15_FORECAST_CALIBRATION_PERFORMANCE_VALIDATED`

## Phase 16 — Delivery, Operator Experience and Quality Feedback
State: `APPROVED_SEQUENTIAL / NOT_STARTED`
Objective: complete the owner intelligence loop with provider-neutral delivery, one owner-approved initial channel, delivery audit/retry/failure isolation, redaction/minimization, operator feedback and quality metrics. No opaque self-modifying truth policy. Start.me remains public/non-sensitive and non-canonical if used.
Gate: `PHASE_16_DELIVERY_OPERATOR_QUALITY_LOOP_VALIDATED`

# Conditional / Owner-Gated Future Phases

## Phase 17 — Controlled External Publication Readiness
State: `CONDITIONAL / NOT_ACTIVATED`
Activation requires a separate explicit owner publication decision after owner-value evidence is reviewed. The existing E3 owner/admin API must not become the public API contract.
Activation gate: `PHASE_17_ACTIVATION_REQUIRES_EXPLICIT_OWNER_DECISION`

## Phase 18 — Shared / Team Runtime
State: `CONDITIONAL / NEW_ARCHITECTURE_APPROVAL_REQUIRED`
Activation requires explicit owner request, new architecture ADR, Source-of-Truth decision, tenancy/RBAC, concurrency/transaction model, measured storage evaluation, backup/DR/security/migration strategy and no silent mixed storage.
Activation gate: `PHASE_18_REQUIRES_NEW_ARCHITECTURE_APPROVAL`

# Current Implementation Checkpoint

- Product Concept: `APPROVED`
- Roadmap: `APPROVED / v4.1 state synchronization; strategic ROADMAP remains v4`
- Engineering baseline: validated through ROADMAP Phase 11 plus E1-E7 and E9A
- Owner-only private GPT pilot: `SUCCESSFUL / 18 of 18 PASS`
- E8: `USER_DEFERRED`
- E9A: `OWNER_ONLY_PRODUCTION_CANDIDATE_READY / COMPLETE`
- E9: `NOT_APPROVED`
- Runtime storage: `PROJECT_LOCAL_ONLY`
- Mixed/shared runtime storage: `BLOCKED pending new explicit architecture approval`
- Owner-only OCI runtime: `REAL_HOST_VALIDATED / OWNER_ONLY_PRODUCTION_CANDIDATE_READY / NOT_PRODUCTION`
- Private GPT backend Action: `NOT_CONNECTED`
- Backend HTTPS: `NOT_DEPLOYED`
- Admin dashboard: `NOT_DEPLOYED`
- Public sharing: `NOT_ACTIVE`
- Production/live operational status: `NOT_OPERATIONAL`
- P12.0: `P12_0_CANONICAL_CONVERGENCE_VALIDATED`

Current/next engineering activity:
`PHASE_12 / P12.1_SOURCE_PORTFOLIO_CONTRACT_AND_GOVERNANCE / NEXT_NOT_STARTED`

Next gate:
`P12_1_SOURCE_PORTFOLIO_CONTRACT_VALIDATED`

Conditional publication:
`PHASE_17_NOT_ACTIVATED`

Conditional shared/team runtime:
`PHASE_18_NEW_ARCHITECTURE_APPROVAL_REQUIRED`
