# Post-E9A Roadmap v4 Decision

Date: 2026-09-01
Project: K-Geopolitical Monitor
Status: `OWNER_DIRECTION_RECORDED / ROADMAP_V4_APPROVED`
Basis analysis: `docs/analysis/KGM_SYSTEM_DEVELOPMENT_ANALYSIS_2026-09-01.md`
Basis checkpoint: `docs/checkpoints/PROJECT_CHECKPOINT_2026-09-01_PRE_NEXT_ROADMAP_ANALYSIS.md`

## 1. Owner Direction

The owner explicitly directed the project to:
- preserve a state/recovery checkpoint;
- analyze current implementation, development needs and future decisions;
- create the next project roadmap;
- transition continuation to a new chat from the resulting canonical state.

This decision records that direction and authorizes the next roadmap generation.

## 2. Strategic Decision

The next development generation will prioritize **intelligence quality, source-network breadth and owner operational value** rather than public publication or shared runtime first.

Approved strategic sequence:

`ENGINEERING PLATFORM -> INTELLIGENCE QUALITY -> SOURCE NETWORK -> OWNER OPERATIONALIZATION -> FORECAST CALIBRATION -> DELIVERY / QUALITY FEEDBACK -> OPTIONAL PUBLICATION -> OPTIONAL SHARED RUNTIME`

The following principles are approved:
- do not replatform the validated runtime/storage stack without evidence that it is a real constraint;
- do not publish the current product before intelligence depth and source breadth materially improve;
- do not introduce shared/team canonical runtime storage before there is a real multi-user requirement and a new architecture decision;
- preserve the existing truth/provenance/verification/coverage/forecast boundaries;
- prefer additive, auditable, fail-closed improvements over opaque self-modifying behavior;
- model/LLM-assisted extraction may propose structured analytical objects, but canonical truth-state promotion remains policy-controlled, provenance-bound and auditable.

## 3. Roadmap Approval

The following numbered phases are approved as the next sequential development roadmap:

- `Phase 12 — Intelligence Quality and Source Network Foundation`;
- `Phase 13 — Semantic Verification and Provenance Intelligence`;
- `Phase 14 — Owner Operational Intelligence Activation`;
- `Phase 15 — Forecast Calibration and Performance Intelligence`;
- `Phase 16 — Delivery, Operator Experience and Quality Feedback`.

Only **Phase 12** is approved for immediate engineering execution after transition.

Phases 13–16 are roadmap-approved sequential phases, but each begins only after the preceding phase gate is validated and canonical state is synchronized.

No M14 engineering label is created by this decision.

## 4. Conditional Future Phases

The following are roadmap placeholders with explicit activation gates, not current implementation approvals:

### Phase 17 — Controlled External Publication Readiness

State:
`CONDITIONAL / NOT_ACTIVATED`

Requires a separate explicit owner publication decision after owner operational value and intelligence quality are validated.

It may include:
- Business workspace migration/eligibility recheck;
- public-facing GPT instructions/branding/privacy review;
- publication adversarial testing;
- sanitized external read-only facade only if separately approved;
- TLS, abuse/rate controls, field minimization, privacy policy and kill switch if an Action is retained;
- final publication/share gate.

The existing owner/admin API must never be exposed directly as the public contract.

### Phase 18 — Shared / Team Runtime

State:
`CONDITIONAL / NEW_ARCHITECTURE_APPROVAL_REQUIRED`

Requires:
- demonstrated multi-user/team need;
- a new architecture ADR;
- explicit canonical Source-of-Truth, tenancy/RBAC, concurrency, backup/DR, security and migration decisions;
- explicit approval before any shared/mixed runtime storage change.

Current `PROJECT_LOCAL_ONLY` storage remains mandatory until such approval.

## 5. Phase 12 Immediate Scope

Phase 12 starts with:

`P12.0 — Canonical Architecture / Security / Integration Convergence`

This is required because secondary canonical documentation still contains pre-E9A state language.

Then Phase 12 proceeds through:
- source portfolio contract and governance;
- adapter framework v2;
- priority authoritative source pack;
- local-language/media discovery pack;
- source health/freshness/drift and outbound-egress inventory;
- x64/native-ARM64/controlled-live validation matrix.

The objective is not to claim global completeness. It is to build a materially broader, measurable and maintainable source network under the existing coverage semantics.

## 6. Preserved Boundaries

This roadmap approval does not activate:
- `PRODUCTION_LIVE`;
- public GPT publication/sharing;
- ChatGPT Business migration;
- public backend/API/dashboard ingress;
- E9/shared production runtime;
- shared/mixed canonical storage;
- any paid/external provider;
- any new notification provider.

Current states remain:
- `OWNER_ONLY_PRODUCTION_CANDIDATE_READY = ESTABLISHED`;
- `PRODUCTION_LIVE = NOT_OPERATIONAL`;
- `RUNTIME_STORAGE = PROJECT_LOCAL_ONLY`;
- `E8_EXTERNAL_SHARING = DEFERRED`;
- `E9_SHARED_PRODUCTION_RUNTIME = NOT_APPROVED`.

## 7. Security Exceptions

The two current owner-approved candidate exceptions remain explicit:
- public SSH TCP/22 from `0.0.0.0/0`;
- broad outbound egress.

Phase 12 must inventory actual source/network requirements before broad egress is narrowed.
Phase 14 must include a private-admin/SSH disposition gate before any owner operational activation decision.

## 8. Truth / Epistemic Invariants

All future phases must preserve:
- publisher/publication is not automatically the underlying origin;
- repost/syndication/translation/citation does not create independent corroboration;
- official statement proves `actor said X`, not automatically `X happened`;
- source reputation does not automatically determine claim truth;
- graph inference cannot promote factual verification or independent-origin count;
- forecast probability/confidence cannot promote present-tense factual verification;
- coverage confidence cannot promote factual verification confidence;
- GLOBAL is intended scope, not proof of exhaustive world coverage;
- missing local-language evidence remains a visible coverage limitation;
- reconstructed search/tool history must never be labeled exact;
- unavailable persisted backend state must never be replaced by ad hoc public-web research;
- runtime-health instrumentation cannot imply unavailable coverage/source-health/uptime/production facts.

## 9. Immediate Gate

After ROADMAP v4 and transition artifacts are canonicalized:

`CURRENT_ENGINEERING_ACTIVITY = PHASE_12 / P12.0_CANONICAL_CONVERGENCE`

`NEXT_NUMBERED_ROADMAP_PHASE = PHASE_12_APPROVED`

`PRODUCTION_LIVE = NOT_OPERATIONAL`

The next chat must resume with P12.0, not with publication, shared runtime or production activation.
