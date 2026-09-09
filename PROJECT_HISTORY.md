# PROJECT_HISTORY

Chronological record of major approved K-Geopolitical Monitor milestones.

Version: 4.35
Status: ACTIVE / PHASE_18_P18_9_VALIDATED / A1_PREFLIGHT_VALIDATED / PHASE_18_NOT_ACTIVATED
Canonical state contract: `docs/state/CURRENT_PROJECT_STATE.json`

## Validated Historical Baseline

Phases 0–11, owner-only private GPT pilot, E1–E7 and E9A remain validated as recorded in prior checkpoints. E8 remains historical/deferred rather than active public sharing. E9 shared production runtime remains not approved. `PRODUCTION_LIVE = NOT_OPERATIONAL`.

## 2026-09-01 — Phase 12

Phase 12 closed at `PHASE_12_INTELLIGENCE_SOURCE_NETWORK_FOUNDATION_VALIDATED / PASS_WITH_KNOWN_LIMITATIONS` on final closure HEAD `3211994450c11698a553f5249e3ecec94079b5ad`. Known source/parser/freshness and limited-language-slice observations remain explicit historical limitations, not truth operators.

## 2026-09-01–04 — Phase 13 Semantic Verification and Provenance

P13.0–P13.6 were validated sequentially. Phase 13 established structured semantic claims, provenance/origin relations, typed evidence and independence, typed contradictions, versioned verification policy/multidimensional confidence and read-only live compatibility.

Strategic gate: `PHASE_13_SEMANTIC_VERIFICATION_PROVENANCE_VALIDATED`.
Canonical factual-verification authority remains P13.5/P13.6.

## 2026-09-04 — Phase 14 Owner Operational Intelligence Readiness

P14.0–P14.6 validated an owner-facing persisted-state/read-only operational intelligence layer without activation.

Gate: `PHASE_14_OWNER_OPERATIONAL_INTELLIGENCE_READY`.
State: `VALIDATED_READY / NOT_ACTIVATED`.
Operational activation remains owner-gated.

## 2026-09-04 — Phase 15 Forecast Calibration and Performance Intelligence

P15.0–P15.6 validated provenance-bound outcome assessment/resolution, calibration observations, exact-cohort performance/drift intelligence and owner read-only projection.

Gate: `PHASE_15_FORECAST_CALIBRATION_PERFORMANCE_VALIDATED`.
Migrations introduced: `028`, `029`, `030`.

## 2026-09-05 — Phase 16 Delivery, Operator Experience and Quality Feedback

P16.0–P16.7 validated deterministic delivery intents/audit, redaction/data minimization, provider-neutral local/test transport, receipt evidence, owner read model, append-only operator feedback and advisory quality observations.

Gate: `PHASE_16_DELIVERY_OPERATOR_QUALITY_LOOP_VALIDATED`.
Migrations introduced: `031`, `032`.
No real external delivery provider was activated.

## 2026-09-05 — Phase 17 Controlled External Publication Readiness

P17.0–P17.6 validated publication eligibility, strict public-safe projection/redaction, deterministic release manifests/packages, provider-neutral local/test publication target and owner read-only readiness projection.

Readiness gate: `PHASE_17_CONTROLLED_EXTERNAL_PUBLICATION_READINESS_VALIDATED`.
State: `VALIDATED_READY / NOT_ACTIVATED`.
Current account publication capability: `UNAVAILABLE`.
Migration `033`: `NOT_CREATED / NOT_PREAUTHORIZED`.

## 2026-09-07–08 — Phase 18 Shared / Team Runtime Architecture and Readiness

Owner approved the new Phase 18 architecture and authorized implementation. P18.0–P18.9 were then implemented and validated sequentially:

- P18.0 shared-runtime contract foundation;
- P18.1 identity/tenant context;
- P18.2 RBAC/owner-gate enforcement;
- P18.3 shared-datastore schema/migration contract;
- P18.4 tenant repository concurrency/idempotency;
- P18.5 audit/outbox side-effect isolation;
- P18.6 shared-runtime security/secrets controls;
- P18.7 backup/DR/rollback contract;
- P18.8 non-production shadow/canary readiness;
- P18.9 Phase 18 validation matrix and activation readiness.

P18.9 gate: `PHASE_18_SHARED_TEAM_RUNTIME_ACTIVATION_READINESS_VALIDATED`.
P18.9 closure remained deliberately fail-closed for concrete infrastructure observation and launch eligibility: `launch_eligible = false`, `activation_state = NOT_AUTHORIZED`.

This historical P18.9 state is preserved; later A1 evidence does not rewrite the P18.9 closure decision.

## 2026-09-08 — Activation A0 Railway Free/Trial Preflight Amendment

Owner authorized a bounded disposable Railway candidate for infrastructure preflight only. This did not select Railway as the future shared-runtime provider, authorize paid use, activate production/live, create migration `033`, migrate canonical data or permit public database ingress.

A0 checkpoint established the concrete path for A1 live PostgreSQL/RLS validation while preserving all activation boundaries.

## 2026-09-09 — Phase 18 Activation A1 Railway/PostgreSQL RLS Preflight

A1 repaired the concrete PostgreSQL RLS execution boundary by introducing restricted runtime role `kgm_preflight_runtime` and using transaction-local role switching for tenant operations.

Canonical implementation anchor after PR #45 merge:
`8ac2c92c9351ac1bcea8818e52a819f81868ed92`.

Validation evidence:

- PR #45 CI: `1149 passed / SUCCESS`;
- exact-SHA native ARM64 run `34357091433`, job `102484414159`: native `aarch64`, `1149 passed in 100.03s / SUCCESS`, bootstrap/unattended/systemd PASS;
- independent exact-SHA x64 run `34358136924`, job `102487942139`: exact canonical SHA, `1149 passed in 202.48s / SUCCESS`.

Railway candidate `kgm-preflight-api-v3` was repinned to the exact canonical implementation SHA. Deployment `52c39935-9e89-4f12-82e3-82345c606426` completed `SUCCESS`, application startup completed and `/health` returned HTTP 200.

The startup self-check is fail-closed unless RLS isolation is observed and alternate-tenant visible rows equal zero. Accepted A1 result:

- `rls_isolation_observed = true`;
- `alternate_tenant_visible_rows = 0`;
- `A1_LIVE_RLS_PREFLIGHT = PASS`.

PostgreSQL remained private-only with no public service domain and no public TCP proxy. No new runtime-role password/DSN/secret was introduced.

Gate recorded:
`PHASE_18_ACTIVATION_A1_RAILWAY_RLS_PREFLIGHT_VALIDATED`.

Checkpoint:
`docs/checkpoints/PROJECT_CHECKPOINT_2026-09-09_PHASE_18_ACTIVATION_A1_RAILWAY_RLS_PREFLIGHT_VALIDATED.md`.

The Railway environment is provider-labeled `production`, but this candidate remains KGM **non-production preflight** by architecture/governance contract.

## Current Strategic Position

- strategic ROADMAP: `APPROVED / v4`, roadmap document `4.34`;
- state synchronization: `4.35`;
- Phase 12: validated with known limitations;
- Phase 13: validated;
- Phase 14: `VALIDATED_READY / NOT_ACTIVATED`;
- Phase 15: validated;
- Phase 16: validated;
- Phase 17: `VALIDATED_READY / NOT_ACTIVATED`;
- Phase 18 P18.0–P18.9: `VALIDATED`;
- Phase 18 A1 concrete non-production infrastructure/RLS preflight: `VALIDATED`;
- current position: `PHASE_18_ACTIVATION_A1_VALIDATED_OWNER_ACTIVATION_GATE`;
- `PHASE_18_SHARED_RUNTIME_ACTIVE = NO`;
- migration `033 = NOT_CREATED / NOT_PREAUTHORIZED`;
- paid providers: `NONE_APPROVED`;
- runtime storage: `PROJECT_LOCAL_ONLY`;
- mixed/shared canonical runtime: `BLOCKED`;
- production public KGM API/dashboard ingress: `NOT_APPROVED / NOT_DEPLOYED`;
- private GPT Action: `NOT_CONNECTED`;
- public sharing: `NOT_ACTIVE`;
- production/live: `NOT_OPERATIONAL`.

Production/live operational status: NOT_OPERATIONAL
Runtime storage mode: PROJECT_LOCAL_ONLY

Any transition beyond A1 requires a separate explicit owner decision plus fresh launch-time validation. A1 does not auto-authorize shared-runtime activation, canonical data cutover, migration `033`, provider spend or production/live operation.
