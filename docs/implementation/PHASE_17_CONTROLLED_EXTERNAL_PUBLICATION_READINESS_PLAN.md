# Phase 17 — Controlled External Publication Readiness

Date: 2026-09-05
Plan status: `IN_PROGRESS`
Plan lifecycle: `DEFINED -> VALIDATED_PLAN -> IN_PROGRESS -> COMPLETE / VALIDATED_READY / NOT_ACTIVATED`
Project: K-Geopolitical Monitor
ROADMAP basis: `v4.20`
Strategic phase state: `CONDITIONAL / NOT_ACTIVATED`
Activation gate: `PHASE_17_ACTIVATION_REQUIRES_EXPLICIT_OWNER_DECISION`
Planning gate: `P17_CONTROLLED_PUBLICATION_READINESS_PLAN_VALIDATED`
Base repository control point: `544eda6267fef8c146c155178809154b6c15c2ae`

## Objective

Define and validate a controlled, public-safe publication readiness layer over canonical KGM intelligence without activating publication, public ingress, a public GPT Action, shared runtime, owner execution or paid providers.

Phase 17 is an engineering-readiness phase. Successful engineering may reach `VALIDATED_READY / NOT_ACTIVATED`; actual publication remains a separate explicit owner decision under `PHASE_17_ACTIVATION_REQUIRES_EXPLICIT_OWNER_DECISION`.

## Plan Validation

Plan validation anchor: `fef4055a84f582bf8ca5c5cbfbb61644cc297f10`.

Validation evidence:

- x64 CI run `33931843691`, job `101211866468`: `647 passed, 2 warnings / SUCCESS`;
- native ARM64 run `33931843681`, job `101211866698`: native `aarch64`, `647 passed, 2 warnings / SUCCESS`;
- ARM64 host bootstrap: PASS;
- ARM64 unattended one-tick: PASS;
- ARM64 systemd contract: PASS.

## Historical E8 Boundary

Phase 17 does not reinterpret E8 as an active external/public system.

The validated historical E8 records establish that:

- E8 preflight was `PREFLIGHT_COMPLETE / IMPLEMENTATION_NOT_APPROVED`;
- later owner approval covered publication-ready owner-only development only;
- `E8_EXTERNAL_SHARING = NOT_ACTIVE`;
- `E8_PUBLIC_ACTION = NOT_APPROVED`;
- `E8_PUBLIC_BACKEND = NOT_DEPLOYED`;
- `E8_PUBLIC_GPT = NOT_PUBLISHED`;
- the existing owner E3 Action API and E5 admin dashboard are not public contracts and must not be exposed directly;
- any future external persisted-state facade must be separately sanitized, allowlisted and isolated from owner/admin credentials and surfaces.

OpenAI publication/workspace constraints recorded in E8 are historical external facts from 2026-08-29, not permanent KGM architecture facts. Any actual launch gate must revalidate then-current platform eligibility and publication requirements.

## Authoritative Baseline

- Phase 13 P13.5/P13.6 remains the canonical factual-verification path;
- Phase 14 remains `VALIDATED_READY / NOT_ACTIVATED`, with owner operational activation separately gated;
- Phase 15 forecast calibration/performance intelligence remains descriptive and non-promotional;
- Phase 16 delivery/operator/quality evidence remains non-promotional to factual verification;
- E6 reproducibility evidence is exact only when persisted instrumentation exists;
- runtime storage remains `PROJECT_LOCAL_ONLY`;
- mixed/shared canonical runtime remains `BLOCKED`;
- `PRODUCTION_LIVE = NOT_OPERATIONAL`;
- private GPT Action remains `NOT_CONNECTED`;
- backend HTTPS remains `NOT_DEPLOYED`;
- admin dashboard remains `NOT_DEPLOYED`;
- public sharing remains `NOT_ACTIVE`;
- paid providers remain `NONE_APPROVED`.

## Permanent Phase 17 Boundaries

- publication is a derived presentation layer, not canonical truth state;
- publisher/publication identity is not automatically the underlying origin;
- a publication event, release receipt, view, click, download, reaction or engagement count cannot create independent corroboration or promote factual verification;
- publication lifecycle state is not factual-verification state;
- publication eligibility is not factual-verification status and cannot silently upgrade an unverified or disputed claim;
- public projection references canonical intelligence identifiers and does not create a shadow truth store;
- provenance, verification state, uncertainty, contradiction state and coverage limitations are not silently removed or strengthened by projection;
- public-safe redaction and data minimization occur before any export or publication-target boundary;
- secrets, authentication material, owner/admin tokens, private database paths, raw operator feedback, unnecessary runtime metadata and non-public operational diagnostics are forbidden in public payloads;
- missing, stale, ambiguous or non-public-safe canonical references fail closed;
- exact reproducibility/history claims are emitted only from persisted instrumentation; uninstrumented history remains explicitly unavailable/not instrumented;
- third-party source material is not republished wholesale; publication uses bounded KGM-derived summaries, metadata and provenance/source references as appropriate;
- target failure cannot mutate canonical intelligence, alert, forecast, delivery or feedback truth meaning;
- no real public target, public API ingress, public GPT Action, domain exposure or external credential is activated by Phase 17 engineering validation;
- no self-modifying verification, alert, source, forecast, delivery or publication policy is authorized in Phase 17;
- Phase 18 shared/team runtime is not activated or pre-approved by Phase 17;
- paid providers remain forbidden unless separately approved.

## Architecture Separation

`CANONICAL INTELLIGENCE STATE -> PUBLICATION ELIGIBILITY -> PUBLIC-SAFE PROJECTION -> RELEASE MANIFEST -> PUBLICATION PACKAGE -> LOCAL/TEST PUBLICATION TARGET -> RELEASE RECEIPT`

A downstream publication object may reference upstream state but cannot rewrite its factual meaning. A release receipt proves only that a publication target accepted or recorded a package. It is publication evidence, not event evidence.

## Planned Phase 17 Sequence

### P17.0 — Controlled Publication Architecture and Safety Contract

State: `VALIDATED`
Gate: `P17_0_CONTROLLED_PUBLICATION_ARCHITECTURE_CONTRACT_VALIDATED`
Validation anchor: `e7281428cc226c4f68223f3b89503a3aa47a92fa`

Validation evidence:

- x64 CI run `33932082220`, job `101212579671`: `658 passed, 2 warnings / SUCCESS`;
- native ARM64 run `33932082188`, job `101212579519`: native `aarch64`, `658 passed, 2 warnings / SUCCESS`;
- ARM64 host bootstrap: PASS;
- ARM64 unattended one-tick: PASS;
- ARM64 systemd contract: PASS.

Validated machine-readable contract: `KGM_CONTROLLED_PUBLICATION_ARCHITECTURE_V1` in `src/kgeopolitical_monitor/controlled_publication_contract.py`.

Validated boundaries:

- publication eligibility, public-safe projection, release manifest/package, target attempt and release receipt remain separate derived entities;
- publisher/publication identity is not underlying-origin proof;
- publication eligibility and target receipts cannot promote factual verification;
- public-safe projection is strict allowlist/fail-closed and precedes any export/target boundary;
- exact reproducibility is never invented for uninstrumented history;
- historical E8 public states remain inactive;
- P17.0 introduces no migration: `NONE_FOR_P17_0`;
- no real publication target, endpoint, provider, public credential or network listener is activated.

### P17.1 — Deterministic Publication Eligibility Policy

State: `VALIDATED`
Gate: `P17_1_PUBLICATION_ELIGIBILITY_POLICY_VALIDATED`
Validation anchor: `3b26863f622b5db3cc07cda156f4ea7b2be9d889`

Validation evidence:

- x64 CI run `33932722553`, job `101214469518`: `673 passed, 2 warnings / SUCCESS`;
- native ARM64 run `33932722586`, job `101214469696`: native `aarch64`, `673 passed, 2 warnings / SUCCESS`;
- ARM64 host bootstrap: PASS;
- ARM64 unattended one-tick: PASS;
- ARM64 systemd contract: PASS.

Validated policy: `KGM_PUBLICATION_ELIGIBILITY_POLICY_V1` in `src/kgeopolitical_monitor/publication_eligibility.py`.

Validated behavior:

- `ELIGIBLE` requires an unambiguous current P13.6 link, current P13.5 `VERIFIED` decision, exact referenced factual-confidence row and explicit public-safety state `ALLOWED`;
- `UNLINKED`, `STALE_LINK`, `AMBIGUOUS_CURRENT_LINKS`, missing current decision or missing exact confidence reference fail closed;
- legacy verification status, scalar confidence, publisher/host/source counts and legacy independent-origin counts cannot bypass the canonical semantic path;
- `LIMITED` or `UNKNOWN` coverage and persisted reproducibility limitations remain explicit limitation labels and do not become hidden truth-promotion rules;
- eligibility cannot promote factual verification or rewrite upstream semantic state;
- candidate identity is deterministic and bound to the canonical semantic decision plus public-safety state;
- migration: `NONE`;
- no public route, target, provider, external credential or network publication is activated.

### P17.2 — Public-Safe Projection and Redaction

State: `VALIDATED`
Gate: `P17_2_PUBLIC_SAFE_PROJECTION_REDACTION_VALIDATED`
Validation anchor: `8f2e920fd727597286ec691d49c74dd600df35bd`

Validation evidence:

- x64 CI run `33935188072`, job `101221628767`: `685 passed, 2 warnings / SUCCESS`;
- native ARM64 run `33935188051`, job `101221628733`: native `aarch64`, `685 passed, 2 warnings / SUCCESS`;
- ARM64 host bootstrap: PASS;
- ARM64 unattended one-tick: PASS with `execution_count=0`, `executions=[]`, `recovered_runs=0`;
- ARM64 systemd contract: PASS.

Validated projection: `KGM_PUBLIC_SAFE_PROJECTION_V1` in `src/kgeopolitical_monitor/public_safe_projection.py`.

Validated behavior:

- strict public field allowlist rather than owner/admin response pass-through;
- redaction/data minimization occurs before any export boundary;
- exact P17.1 `ELIGIBLE`, public-safety `ALLOWED` and canonical P13.5 `VERIFIED` are required and fail closed otherwise;
- canonical semantic, verification, factual-confidence, coverage and reproducibility references/limitations are preserved without truth promotion;
- publication, publisher and underlying-origin provenance roles remain distinct;
- raw item content/identifiers, internal source IDs, provenance metadata JSON, owner/admin/watch state, exact query snapshots, delivery internals, raw operator feedback, private paths and credentials are omitted;
- bounded public semantic text redacts authentication material, secret values and private filesystem paths;
- projection identity is deterministic and content-sensitive;
- migration: `NONE`;
- no public HTTP route is required or authorized by this gate;
- no public HTTP route, target, provider, external credential or network publication is activated.

### P17.3 — Release Manifest, Provenance and Reproducibility

State: `NOT_STARTED`
Target gate: `P17_3_RELEASE_MANIFEST_PROVENANCE_VALIDATED`

Candidate manifest fields may include stable package/release identity, schema/contract version, canonical intelligence references, content hash/digest, generation timestamp, publication policy version, provenance/verification/coverage limitations and persisted reproducibility identifiers only when instrumented.

If persistence is later justified, `033` is the next available migration number after Phase 16 migrations `031` and `032`. Migration `033` is not pre-authorized by this plan; exact necessity and schema require P17.3 review. No reconstructed exact tool/query history is permitted.

### P17.4 — Provider-Neutral Local/Test Publication Target

State: `NOT_STARTED`
Target gate: `P17_4_PROVIDER_NEUTRAL_PUBLICATION_TARGET_VALIDATED`

Implement a provider-neutral publication-target interface and deterministic local/in-memory/test sink only.

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

Provide a project-local read-only owner preview of candidate eligibility/blockers, public-safe projection, redaction status, manifest/package identity and digest, provenance/verification/coverage limitations, local/test target status and unresolved activation prerequisites.

The projection does not publish, expose a public route, deploy backend HTTPS, connect a GPT Action, enable owner execution or open public ingress.

### P17.6 — Phase 17 Validation Matrix / Strategic Readiness Closure

State: `NOT_STARTED`
Readiness gate: `PHASE_17_CONTROLLED_EXTERNAL_PUBLICATION_READINESS_VALIDATED`
Activation gate remains: `PHASE_17_ACTIVATION_REQUIRES_EXPLICIT_OWNER_DECISION`

Closure must confirm:

- publication/truth lifecycle separation;
- publisher/publication is not underlying-origin proof;
- publication receipts/engagement are not truth operators;
- eligibility cannot promote factual verification;
- redaction/data minimization occurs before export/target boundary;
- owner/admin surfaces and credentials are not reused as public surfaces/credentials;
- public-safe projection preserves provenance, uncertainty and limitations;
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

Successful P17.6 may advance Phase 17 to `VALIDATED_READY / NOT_ACTIVATED`. It must not set publication/sharing to active. Actual publication requires a later explicit owner decision plus then-current platform, security, privacy, exposure and rollback validation.

## Validation Strategy Per Gate

Each gate requires deterministic unit/contract tests and regression guards. Persistence, if introduced later, requires additive migration/idempotency/history tests. Publication-target tests use only a deterministic local/in-memory/test sink unless a later explicit owner decision separately authorizes a real target test.

No P17 subphase is promoted from implemented to validated solely because code exists. Validation evidence must reference the exact repository commit tested.

The Phase 17 strategic readiness closure requires both exact-head x64 and native ARM64 validation.

## Non-Goals

Phase 17 engineering readiness does not authorize actual external publication or public sharing, GPT Store publication, a public GPT Action, public backend/API/dashboard ingress, backend HTTPS production deployment, reuse of owner/admin API or credentials for external access, production/live activation, owner unattended activation, Phase 18/shared-team canonical runtime, cross-project canonical-store mutation, paid providers, autonomous/self-modifying policy, or replacement of P13.5/P13.6 factual verification.

## Current Decision

Plan decision: `IN_PROGRESS`.

P17.0, P17.1 and P17.2 are validated on exact implementation anchors with matching successful x64 and native ARM64 regressions. Strategic Phase 17 remains `CONDITIONAL / NOT_ACTIVATED`; no publication activation is implied.

Next sequential engineering task: P17.3 — Release Manifest, Provenance and Reproducibility.
