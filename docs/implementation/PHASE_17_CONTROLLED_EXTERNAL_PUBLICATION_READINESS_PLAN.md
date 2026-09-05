# Phase 17 — Controlled External Publication Readiness

Date: 2026-09-05
Plan status: `DEFINED / IMPLEMENTATION_NOT_STARTED`
Plan lifecycle: `DEFINED -> VALIDATED_PLAN -> IN_PROGRESS -> COMPLETE / VALIDATED_READY / NOT_ACTIVATED`
Project: K-Geopolitical Monitor
ROADMAP basis: `v4.20`
Strategic phase state: `CONDITIONAL / NOT_ACTIVATED`
Activation gate: `PHASE_17_ACTIVATION_REQUIRES_EXPLICIT_OWNER_DECISION`
Planning gate: `P17_CONTROLLED_PUBLICATION_READINESS_PLAN_VALIDATED`
Base repository control point: `544eda6267fef8c146c155178809154b6c15c2ae`

## Objective

Define the sequential engineering and validation path for a controlled, public-safe publication layer over validated KGM intelligence without activating publication, public ingress, a public GPT Action, shared runtime, owner execution or paid providers.

Phase 17 is a readiness phase. Engineering validation may establish `VALIDATED_READY / NOT_ACTIVATED`, but actual external publication remains a separate owner decision under `PHASE_17_ACTIVATION_REQUIRES_EXPLICIT_OWNER_DECISION`.

## Historical E8 Boundary

Phase 17 does not reinterpret E8 as an already active external/public system.

The validated historical E8 records establish that:

- E8 preflight was `PREFLIGHT_COMPLETE / IMPLEMENTATION_NOT_APPROVED`;
- the later owner decision approved publication-ready owner-only development only;
- `E8_EXTERNAL_SHARING = NOT_ACTIVE`;
- `E8_PUBLIC_ACTION = NOT_APPROVED`;
- `E8_PUBLIC_BACKEND = NOT_DEPLOYED`;
- `E8_PUBLIC_GPT = NOT_PUBLISHED`;
- the existing owner E3 Action API and E5 admin dashboard are not public contracts and must not be exposed directly;
- any future external persisted-state facade must be separately sanitized, allowlisted and isolated from owner/admin credentials and surfaces.

OpenAI publication/workspace constraints recorded in E8 are historical external facts from 2026-08-29, not permanent KGM architecture facts. Any actual launch gate must revalidate then-current platform eligibility and publication requirements.

## Authoritative Baseline

Phase 17 builds on the current validated repository state:

- Phase 13 P13.5/P13.6 remains the canonical factual-verification path;
- Phase 14 remains `VALIDATED_READY / NOT_ACTIVATED` and owner operational activation remains separately gated;
- Phase 15 forecast calibration/performance intelligence is descriptive and non-promotional to factual verification;
- Phase 16 delivery/operator/quality loop is validated, but delivery receipts, feedback and quality metrics are not truth operators;
- E6 reproducibility instrumentation may be used only when exact persisted instrumentation exists; unavailable or uninstrumented history is never reconstructed as exact;
- runtime storage remains `PROJECT_LOCAL_ONLY`;
- mixed/shared canonical runtime remains `BLOCKED`;
- `PRODUCTION_LIVE = NOT_OPERATIONAL`;
- private GPT Action remains `NOT_CONNECTED`;
- backend HTTPS remains `NOT_DEPLOYED`;
- admin dashboard remains `NOT_DEPLOYED`;
- public sharing remains `NOT_ACTIVE`;
- paid providers remain `NONE_APPROVED`.

## Permanent Phase 17 Boundaries

The following rules apply to every P17 subphase:

- publication is a derived presentation layer, not canonical truth state;
- publisher/publication identity is not automatically the underlying origin;
- a publication event, release receipt, view, click, download, reaction or engagement count cannot create independent corroboration or promote factual verification;
- publication lifecycle state is not factual-verification state;
- publication eligibility is not factual-verification status and cannot silently upgrade an unverified or disputed claim;
- public projection must reference existing canonical intelligence identifiers rather than create a shadow truth store;
- canonical provenance, verification state, uncertainty, contradiction state and coverage limitations must not be silently removed or strengthened by publication projection;
- public-safe redaction and data minimization occur before any export or publication-target boundary;
- secrets, authentication material, owner/admin tokens, private database paths, raw operator feedback, unnecessary runtime metadata and non-public operational diagnostics are forbidden in public payloads;
- missing, stale, ambiguous or non-public-safe canonical references fail closed;
- exact reproducibility/history claims are emitted only from persisted instrumentation; uninstrumented history remains explicitly unavailable/not instrumented;
- third-party copyrighted source material is not republished wholesale; public packages use bounded KGM-derived summaries, metadata and source/provenance references as appropriate;
- publication-target failure must not mutate canonical intelligence, alert, forecast, delivery or feedback truth meaning;
- no real public target, public API ingress, public GPT Action, domain exposure or external credential is activated merely by implementing or validating Phase 17;
- no self-modifying verification, alert, source, forecast, delivery or publication policy is authorized in Phase 17;
- Phase 18 shared/team runtime is not activated or pre-approved by Phase 17;
- paid providers remain forbidden unless separately approved.

## Architecture Separation

Phase 17 keeps the publication path distinct from canonical analysis:

`CANONICAL INTELLIGENCE STATE -> PUBLICATION ELIGIBILITY -> PUBLIC-SAFE PROJECTION -> RELEASE MANIFEST -> PUBLICATION PACKAGE -> LOCAL/TEST PUBLICATION TARGET -> RELEASE RECEIPT`

A downstream publication object may reference upstream canonical state but may not rewrite its factual meaning.

A release receipt proves only that a publication target accepted or recorded a package. It is publication evidence, not event evidence.

## Planned Phase 17 Sequence

### P17.0 — Controlled Publication Architecture and Safety Contract

State: `NOT_STARTED`
Target gate: `P17_0_CONTROLLED_PUBLICATION_ARCHITECTURE_CONTRACT_VALIDATED`

Define a machine-readable architecture contract for:

- publication eligibility;
- public-safe projection;
- release manifest;
- publication package;
- publication target attempt/receipt semantics;
- safety/redaction boundary;
- activation separation;
- non-promotional truth rules;
- runtime/storage/provider boundaries.

P17.0 introduces no migration: `NONE_FOR_P17_0`.

No endpoint, provider, public credential, network listener or external publication action is created by this gate.

### P17.1 — Deterministic Publication Eligibility Policy

State: `NOT_STARTED`
Target gate: `P17_1_PUBLICATION_ELIGIBILITY_POLICY_VALIDATED`

Implement deterministic eligibility evaluation from canonical persisted state.

Required behavior:

- explicit candidate identity and canonical references;
- typed eligible/blocked reasons;
- fail-closed handling of missing, stale or ambiguous canonical state;
- explicit handling of verification, contradiction, provenance, uncertainty and coverage limitations;
- publication eligibility cannot promote factual verification;
- no policy decision may rewrite upstream semantic state;
- publication policy version must be exposed in derived output.

### P17.2 — Public-Safe Projection and Redaction

State: `NOT_STARTED`
Target gate: `P17_2_PUBLIC_SAFE_PROJECTION_REDACTION_VALIDATED`

Create a strict allowlist-based projection suitable for later publication packaging.

Required behavior:

- public field allowlist rather than owner/admin response pass-through;
- redaction/data minimization before export;
- no watch queries/cadence, internal retry/error diagnostics, private DB paths, credentials or owner-only metadata;
- raw operator feedback remains non-public;
- provenance, verification/uncertainty labels and known limitations remain explicit where required to prevent misleading presentation;
- third-party source content is summarized/referenced rather than copied wholesale;
- no public HTTP route is required or authorized by this gate.

### P17.3 — Release Manifest, Provenance and Reproducibility

State: `NOT_STARTED`
Target gate: `P17_3_RELEASE_MANIFEST_PROVENANCE_VALIDATED`

Build a deterministic publication manifest over the public-safe projection.

Candidate manifest fields may include:

- stable package/release identity;
- schema/contract version;
- canonical intelligence references;
- content hash/digest;
- generation timestamp;
- publication policy version;
- provenance/verification/coverage limitation labels;
- persisted reproducibility identifiers only when actually instrumented.

If persistence is justified later, `033` is the next available migration number after Phase 16 migrations `031` and `032`. Migration `033` is not pre-authorized by this plan; exact schema and necessity must be reviewed in P17.3 before implementation.

No reconstructed exact tool/query history is permitted.

### P17.4 — Provider-Neutral Local/Test Publication Target

State: `NOT_STARTED`
Target gate: `P17_4_PROVIDER_NEUTRAL_PUBLICATION_TARGET_VALIDATED`

Implement a provider-neutral publication-target interface and deterministic local/in-memory/test sink only.

Required behavior:

- canonical automated tests perform no real network publication;
- no GitHub Pages, public object bucket, CMS, social account, email list, webhook, public website or GPT Store target is enabled by default;
- target failure is isolated from monitoring and canonical analytical persistence;
- deterministic idempotency prevents duplicate release effects in the test target;
- target receipts are publication evidence only;
- public/external credentials are absent from canonical publication records;
- any real target/provider requires a separate explicit owner activation decision and fresh security/platform validation.

### P17.5 — Owner Publication Readiness Projection and Approval Gate

State: `NOT_STARTED`
Target gate: `P17_5_OWNER_PUBLICATION_READINESS_PROJECTION_VALIDATED`

Extend the owner-only read model with a bounded publication-readiness preview that may expose:

- candidate eligible/blocked status and reasons;
- public-safe projection preview;
- redaction status;
- manifest/package identity and digest;
- provenance/verification/coverage limitations;
- local/test target validation status;
- activation prerequisites and unresolved blockers.

The projection remains project-local and read-only. It does not publish, expose a public route, deploy backend HTTPS, connect a GPT Action, enable owner execution or open public ingress.

### P17.6 — Phase 17 Validation Matrix / Strategic Readiness Closure

State: `NOT_STARTED`
Readiness gate: `PHASE_17_CONTROLLED_EXTERNAL_PUBLICATION_READINESS_VALIDATED`
Activation gate remains: `PHASE_17_ACTIVATION_REQUIRES_EXPLICIT_OWNER_DECISION`

Strategic readiness closure requires P17.0–P17.5 to be validated and a dedicated matrix to confirm:

- publication/truth lifecycle separation;
- publisher/publication is not underlying-origin proof;
- publication receipts/engagement are not truth operators;
- eligibility cannot promote factual verification;
- redaction/data minimization occurs before export/target boundary;
- owner/admin surfaces and credentials are not reused as public surfaces/credentials;
- public-safe projection preserves necessary provenance, uncertainty and limitations;
- exact reproducibility is never reconstructed when not instrumented;
- local/test target is deterministic and no real publication occurs in validation;
- target failure cannot mutate canonical intelligence meaning;
- no unexpected migration or shadow truth store exists;
- `PROJECT_LOCAL_ONLY` remains unchanged;
- mixed/shared canonical runtime remains `BLOCKED`;
- `PRODUCTION_LIVE = NOT_OPERATIONAL` remains unchanged;
- owner operational activation remains separately gated;
- backend HTTPS/public API ingress remain not deployed;
- public GPT Action remains not connected/approved;
- public sharing remains inactive;
- paid providers remain `NONE_APPROVED`;
- Phase 18 remains not activated;
- full x64 repository regression passes on the exact readiness closure anchor;
- full native ARM64 regression passes on the same exact readiness closure anchor;
- ARM64 host bootstrap, unattended one-tick smoke and systemd contract remain PASS.

Successful P17.6 engineering validation may advance Phase 17 to `VALIDATED_READY / NOT_ACTIVATED`. It must not set publication/sharing to active. Actual publication requires a later explicit owner decision plus then-current platform, security, privacy, exposure and rollback validation.

## Validation Strategy Per Gate

Each implementation gate must include deterministic unit/contract tests and regression guards for its own boundary. Any persistence gate must include additive migration/idempotency/history tests. Publication-target tests must use only a deterministic local/in-memory/test sink unless a later explicit owner decision separately authorizes a real target test.

No P17 subphase is promoted from implemented to validated solely because code exists. Validation evidence must reference the exact repository commit tested.

The Phase 17 strategic readiness closure requires both exact-head x64 and native ARM64 validation.

## Non-Goals

Phase 17 engineering readiness does not authorize:

- actual external publication or public sharing;
- GPT Store publication;
- a public GPT Action;
- public backend/API/dashboard ingress;
- backend HTTPS production deployment;
- reuse of the owner/admin API as a public facade;
- reuse of owner/admin credentials for external access;
- production/live activation;
- owner unattended operational activation;
- shared/team canonical runtime or Phase 18 activation;
- direct cross-project canonical-store mutation;
- paid provider use;
- autonomous/self-modifying intelligence or publication policy;
- replacement of P13.5/P13.6 factual verification.

## Next Sequential Engineering Task

After exact-head validation of this plan, the next task is P17.0 — Controlled Publication Architecture and Safety Contract.
