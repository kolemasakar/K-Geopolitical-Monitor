# Phase 16 — Delivery, Operator Experience and Quality Feedback

Date: 2026-09-04
Plan status: `IN_PROGRESS`
Project: K-Geopolitical Monitor
ROADMAP basis: `v4.19`
Strategic phase state: `APPROVED_SEQUENTIAL / NOT_STARTED`
Strategic phase gate: `PHASE_16_DELIVERY_OPERATOR_QUALITY_LOOP_VALIDATED`
Base repository control point: `d66aa42df8d57b93ef3aa2db3185b189a6ed57be`

## Objective

Define the sequential Phase 16 engineering and validation path that turns validated alerts, owner intelligence and forecast-performance evidence into an auditable owner delivery and quality-feedback loop without weakening canonical factual-verification, provenance, runtime, storage, security or activation boundaries.

Phase 16 is an engineering-readiness phase. Completion of this plan, or later completion of Phase 16 engineering, does not by itself activate production/live operation, owner unattended execution, public ingress, shared runtime or any external/paid provider.

## Authoritative Baseline

Phase 16 builds on the validated repository state rather than replacing it:

- Phase 13 P13.5/P13.6 remains the only canonical factual-verification path;
- Phase 14 remains `VALIDATED_READY / NOT_ACTIVATED` with `OWNER_ONLY_OPERATIONAL_ACTIVATION = OWNER_DECISION_REQUIRED`;
- Phase 14 already exposes owner read-only workspace, watch queue, alert-qualification dry run, operational health and briefing projections;
- Phase 15 is closed under `PHASE_15_FORECAST_CALIBRATION_PERFORMANCE_VALIDATED`;
- Phase 15 performance/calibration evidence is descriptive and cannot promote factual verification;
- M9 strategic alert persistence remains the canonical historical alert store;
- runtime storage remains `PROJECT_LOCAL_ONLY`;
- mixed/shared canonical runtime remains `BLOCKED`;
- `PRODUCTION_LIVE = NOT_OPERATIONAL`;
- public KGM API/dashboard ingress remains not approved/deployed;
- paid providers remain `NONE_APPROVED`.

The September 1 system-development analysis identifies the missing delivery loop as priority-based notification policy, dedup/update/resolution handling, delivery audit, failure/retry isolation, quiet-hours/escalation policy where appropriate, and strict redaction/data minimization. It also requires quality loops to use observed correction/error/performance metrics before any self-modifying behavior.

## Permanent Phase 16 Boundaries

The following rules apply to every P16 subphase:

- delivery state is not factual-verification state;
- a delivery receipt, acknowledgement, click, rating or operator action cannot promote a claim to `VERIFIED`;
- operator feedback measures usefulness, correctness perception, workflow quality or required correction; it is not independent event evidence by itself;
- source counts, delivery counts, acknowledgement rates, quality scores and feedback counts are not truth operators;
- forecast calibration/performance metrics remain non-promotional to factual verification;
- delivery must reference existing canonical alert/brief/finding/semantic identifiers rather than create a shadow truth store;
- redaction and data minimization occur before any external-transport boundary;
- secrets, authentication material, private database paths and unnecessary owner/runtime metadata are not valid delivery payload content;
- deduplication and retry must be deterministic and auditable;
- failed delivery must not mutate or downgrade the underlying alert/claim/forecast truth state;
- provider failure is isolated from monitoring and canonical analytical persistence;
- quality analysis is advisory/descriptive until a separate explicit policy-change decision exists;
- no self-modifying verification, alert, source, forecast or delivery policy is authorized in Phase 16;
- no external provider is activated merely by implementing or validating an adapter contract;
- no public route, shared runtime or paid provider is introduced by Phase 16.

## Architecture Separation

Phase 16 keeps these concepts distinct:

`CANONICAL INTELLIGENCE STATE -> DELIVERY INTENT -> REDACTED PAYLOAD -> TRANSPORT ATTEMPT -> DELIVERY RECEIPT -> OPERATOR FEEDBACK -> QUALITY OBSERVATION -> ADVISORY QUALITY SUMMARY`

A downstream state may reference its upstream object, but may not rewrite the upstream truth meaning.

Delivery lifecycle and alert lifecycle remain separate. An alert may be open/updated/resolved regardless of whether a particular delivery attempt succeeds. Likewise, delivery success does not establish alert correctness.

## Planned Phase 16 Sequence

### P16.0 — Delivery / Operator / Quality Architecture Contract

State: `VALIDATED`
Gate: `P16_0_DELIVERY_OPERATOR_QUALITY_ARCHITECTURE_CONTRACT_VALIDATED`
Validation anchor: `bab44c76abdcf5da198b007aeda90e3e30ab4796`

Validation evidence:

- x64 CI run `33915893936`, job `101162849016`: `594 passed, 2 warnings / SUCCESS`;
- native ARM64 run `33915893917`, job `101162848853`: native `aarch64`, `594 passed, 2 warnings / SUCCESS`;
- ARM64 host bootstrap: PASS;
- ARM64 unattended one-tick: PASS;
- ARM64 systemd contract: PASS.

Validated machine-readable contract: `KGM_DELIVERY_OPERATOR_QUALITY_ARCHITECTURE_V1` in `src/kgeopolitical_monitor/delivery_operator_quality_contract.py`.

Validated architecture boundaries:

- canonical intelligence state, delivery intent, redacted payload, transport attempt, delivery receipt, operator feedback, quality observation and advisory quality summary remain distinct entities;
- delivery and transport lifecycle states are typed delivery evidence and never factual-verification states;
- redaction/data minimization precedes any external transport boundary;
- provider credentials and sensitive owner/runtime metadata are excluded from canonical delivery payload semantics;
- operator feedback is workflow/quality evidence and not independent event evidence by itself;
- a factual correction request must re-enter the existing provenance/verification workflow rather than mutate truth state directly;
- quality metrics are descriptive/advisory only and cannot self-modify source, verification, alert, forecast or provider policy;
- migration `031`: `NONE_FOR_P16_0`;
- no provider, public ingress, owner execution or production/live operation is activated by P16.0.

### P16.1 — Canonical Delivery Intent and Audit Persistence

State: `NOT_STARTED`
Target gate: `P16_1_DELIVERY_INTENT_AUDIT_PERSISTENCE_VALIDATED`

Introduce additive, project-local persistence only if required by the validated P16.0 contract.

Required behavior:

- stable delivery intent identity;
- explicit reference to canonical alert/brief/finding state;
- event type such as initial/update/resolution where applicable;
- deterministic deduplication/idempotency key;
- append-only attempt/audit history;
- explicit states such as pending/suppressed/attempted/delivered/failed without conflating them with alert state;
- no external send as a persistence side effect;
- no rewrite of M9/P13/P15 history.

If a new migration is required, `031` is the next available migration number and must be additive. Its exact schema is not pre-authorized by this plan and must be justified in P16.1.

### P16.2 — Delivery Policy, Redaction and Data-Minimized Payload Projection

State: `NOT_STARTED`
Target gate: `P16_2_DELIVERY_POLICY_REDACTION_VALIDATED`

Implement deterministic policy evaluation and payload projection before transport.

Required policy dimensions:

- alert priority/qualification input from persisted canonical state;
- initial/update/resolution delivery semantics;
- deduplication/suppression;
- quiet-hours handling where configured;
- bounded escalation semantics without automatic production activation;
- strict allowlist-based payload fields;
- redaction/data minimization;
- explicit limitation/provenance labels needed to avoid misleading presentation.

Payload projection must fail closed when required canonical references are unavailable, stale or ambiguous.

### P16.3 — Provider-Neutral Delivery Transport and Retry Isolation

State: `NOT_STARTED`
Target gate: `P16_3_PROVIDER_NEUTRAL_DELIVERY_TRANSPORT_VALIDATED`

Implement a transport interface and deterministic local/test transport for engineering validation.

Required behavior:

- provider-neutral adapter contract;
- local/in-memory/test sink for canonical automated tests;
- bounded retry/backoff state represented audibly and deterministically;
- delivery failure isolation from monitoring/runtime analytical state;
- duplicate sends prevented by persisted idempotency semantics;
- transport receipts stored as delivery evidence only;
- provider credentials never persisted in canonical delivery records;
- no real external provider enabled by default.

Activation of Telegram, email, Slack, SMS, push, webhook or any other external channel is outside this gate unless separately and explicitly approved by the owner. Paid providers remain forbidden unless separately approved.

### P16.4 — Owner Delivery and Operator-Experience Read Model

State: `NOT_STARTED`
Target gate: `P16_4_OWNER_OPERATOR_EXPERIENCE_PROJECTION_VALIDATED`

Extend the existing owner-only read model with a bounded delivery/quality workspace that may expose:

- pending/suppressed/delivered/failed delivery status;
- recent delivery attempts and failure reasons;
- dedup/update/resolution context;
- current configured quiet-hours/escalation policy state;
- operator-visible limitations and redaction state;
- quality-feedback availability/status.

The projection remains project-local and read-only. It does not deploy the existing dashboard, create HTTPS ingress, connect a private GPT Action, enable owner execution or expose public endpoints.

### P16.5 — Operator Quality Feedback Persistence

State: `NOT_STARTED`
Target gate: `P16_5_OPERATOR_QUALITY_FEEDBACK_PERSISTENCE_VALIDATED`

Introduce append-only operator-feedback persistence only after the feedback semantics are fixed by P16.0.

Initial feedback dimensions may include typed values such as:

- useful/not useful;
- timely/late;
- duplicate/noisy;
- missing context;
- incorrect prioritization;
- factual correction requested;
- delivery-format issue;
- free-text note with bounded/sanitized storage policy.

Mandatory rules:

- feedback references the exact delivered/intelligence object being reviewed;
- a factual-correction request does not itself change factual verification;
- corrections that may affect canonical truth must re-enter the existing provenance/verification workflow as separate evidence/review work;
- feedback history is append-only and auditable;
- feedback mutation interfaces remain unexposed to public ingress and are not operationally activated by validation.

If a second Phase 16 migration is required, `032` is the expected next additive number after an implemented `031`; exact schema remains subject to P16.5 review.

### P16.6 — Deterministic Quality Metrics and Advisory Feedback Loop

State: `NOT_STARTED`
Target gate: `P16_6_ADVISORY_QUALITY_FEEDBACK_LOOP_VALIDATED`

Build deterministic quality observations from persisted evidence, for example:

- delivery success/failure/retry rates;
- duplicate/suppression counts;
- usefulness/timeliness/noise feedback;
- correction-request categories;
- alert-policy outcome distributions;
- source/extraction/forecast performance evidence where already canonically available and semantically compatible.

Required safeguards:

- metrics expose sample size and cohort definition;
- quality metrics remain descriptive/advisory;
- no automatic source reputation rewrite;
- no automatic verification-policy change;
- no automatic alert-threshold change;
- no automatic forecast probability/calibration change;
- no automatic transport/provider activation;
- recommendations, if produced, must be explicit proposals requiring a separate implementation/policy decision.

### P16.7 — Phase 16 Validation Matrix / Strategic Closure

State: `NOT_STARTED`
Target gate: `PHASE_16_DELIVERY_OPERATOR_QUALITY_LOOP_VALIDATED`

Closure requires all earlier P16 gates to be validated and a dedicated validation matrix to confirm:

- delivery/alert/truth lifecycles remain separate;
- redaction/data minimization is enforced before transport;
- deterministic deduplication and idempotency pass;
- retry/failure isolation passes;
- operator read model remains non-deploying/read-only;
- feedback cannot directly mutate factual verification;
- advisory quality metrics cannot self-modify policies;
- no unexpected migration or shadow truth store exists;
- `PROJECT_LOCAL_ONLY` remains unchanged;
- mixed/shared canonical runtime remains blocked;
- `PRODUCTION_LIVE = NOT_OPERATIONAL` remains unchanged;
- owner execution remains disabled and separately gated;
- public ingress remains not deployed;
- paid providers remain `NONE_APPROVED`;
- full x64 repository regression passes on the exact closure anchor;
- full native ARM64 regression passes on the same exact closure anchor;
- ARM64 host bootstrap, unattended one-tick smoke and systemd contract remain PASS.

## Validation Strategy Per Gate

Each implementation gate must include deterministic unit/contract tests and regression guards for its specific boundary. Persistence gates additionally require migration/idempotency/history tests. Transport tests must use a deterministic local/test sink unless a later explicit owner decision authorizes a real provider test.

No P16 subphase is promoted from implemented to validated solely because code exists. Validation evidence must reference the exact repository commit tested.

## Non-Goals

Phase 16 does not authorize:

- production/live activation;
- owner unattended operational activation;
- public dashboard/API exposure;
- backend HTTPS production deployment;
- private GPT Action activation;
- team/shared canonical storage;
- direct cross-project canonical-store mutation;
- paid provider use;
- autonomous/self-modifying intelligence policy;
- replacement of P13.5/P13.6 factual verification;
- publication readiness or Phase 17 activation.

## Plan Validation Result

P16.0 is validated on exact implementation anchor `bab44c76abdcf5da198b007aeda90e3e30ab4796` with matching successful x64 and native ARM64 regressions.

Plan decision: `IN_PROGRESS`.

The strategic ROADMAP Phase 16 entry remains `APPROVED_SEQUENTIAL / NOT_STARTED` pending later canonical roadmap synchronization; this does not invalidate the validated P16.0 implementation gate.

Next sequential engineering task: P16.1 — Canonical Delivery Intent and Audit Persistence.
