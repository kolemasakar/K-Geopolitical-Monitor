# P18.5 — Audit, Transactional Outbox and Side-Effect Isolation Contract

Status: `IMPLEMENTATION_CANDIDATE`
Date: 2026-09-07
Project: K-Geopolitical Monitor
Gate: `P18_5_AUDIT_OUTBOX_SIDE_EFFECT_ISOLATION_VALIDATED`

## Purpose

P18.5 defines the provider-neutral transaction and side-effect boundary required
before any future shared/team runtime can safely emit externally visible
delivery or publication effects.

The implementation remains a contract-only in-memory harness. It does not
provision a shared datastore, select a provider, allocate migration `033`,
activate shared/public ingress, switch canonical storage, or activate the shared
runtime.

## Contract

### Security-sensitive mutation audit

Every successful P18.5 canonical mutation produces one immutable application-
append-only audit record containing:

- authenticated actor kind, stable principal identifier and session identifier;
- `workspace_id` and `project_id`;
- action;
- canonical object type, identifier and resulting version;
- canonical command SHA-256 fingerprint;
- correlation, request and optional causation identifiers;
- timezone-aware occurrence timestamp.

Failed authorization, optimistic-concurrency failure and pre-commit process
failure cannot publish a canonical mutation audit record. Exact idempotent
replay does not create a second mutation record.

### Atomic canonical mutation and outbox handoff

The contract harness commits these artifacts under one transaction boundary:

- canonical object mutation;
- P18.4 tenant-scoped idempotency receipt;
- P18.5 retry identity;
- security mutation audit record;
- optional transactional outbox message.

Every artifact is fully constructed and validated before the harness mutates
transaction state. A simulated ordinary process failure immediately before the
commit therefore leaves all five categories unchanged.

The P18.5 retry identity binds the P18.4 canonical command to the authenticated
actor, audit action and side-effect intent. Reuse of the canonical idempotency
key with a changed actor, action or external side-effect intent fails closed.

### Outbox message

A transactional outbox message contains:

- exact `workspace_id` and `project_id`;
- delivery or publication kind;
- provider-neutral channel and destination reference;
- immutable canonical JSON payload plus SHA-256 payload fingerprint;
- stable delivery idempotency key;
- canonical object type, identifier and resulting version;
- correlation identifier and creation time;
- lifecycle state `PENDING` or `DELIVERED`;
- optional delivery receipt reference only after successful delivery-state
  commit.

Outbox lookup is tenant-scoped. An identifier alone is never an authorization
boundary.

### Idempotent side-effect consumer

Dispatch requires an authenticated principal with explicit
`SERVICE_EXECUTE` authority for the exact tenant context.

A side-effect consumer must durably treat the outbox
`delivery_idempotency_key` as the external-effect retry identity. The contract
harness proves:

- first delivery performs the effect once;
- exact retry returns the original receipt;
- reuse of the same delivery key for different effect content fails closed;
- process loss after the external effect but before local outbox acknowledgement
  can be retried without duplicating the external effect;
- concurrent dispatch attempts using the same stable key produce one external
  effect.

A future real transport/provider adapter must implement equivalent durable
deduplication at or before its externally visible effect boundary.

### Truth separation

Security audit records, outbox messages, delivery receipts and publication
receipts are lifecycle/security evidence only.

They have no factual-verification authority and cannot:

- set or promote semantic verification status;
- increase factual verification confidence;
- establish evidence independence;
- resolve contradictions;
- create underlying-origin corroboration.

Canonical factual verification authority remains P13.5/P13.6.

## Acceptance Evidence Required

`P18_5_AUDIT_OUTBOX_SIDE_EFFECT_ISOLATION_VALIDATED` requires regression
evidence that:

- canonical write/audit/outbox commit cannot diverge through simulated ordinary
  pre-commit process failure;
- audit records are immutable append-only values from the application
  perspective;
- canonical retries do not duplicate audit/outbox artifacts;
- changed actor/action/side-effect intent under the same retry key fails closed;
- outbox and audit reads remain exact-tenant scoped;
- dispatch requires explicit service execution scope;
- failure after effect/before acknowledgement retries through the same stable
  delivery key without duplicating the external effect;
- concurrent delivery attempts remain externally idempotent;
- delivery/publication lifecycle evidence remains truth-neutral;
- full x64 and native ARM64 regressions pass.

## Preserved Boundaries

P18.5 implementation does not change these canonical project boundaries:

- runtime storage: `PROJECT_LOCAL_ONLY`;
- owner-only project-local SQLite remains canonical and independently operable;
- mixed/shared canonical runtime: `BLOCKED`;
- shared runtime activation: `PHASE_18_SHARED_RUNTIME_ACTIVE = NO`;
- migration `033`: `NOT_CREATED / NOT_PREAUTHORIZED`;
- paid providers: `NONE_APPROVED`;
- backend HTTPS: `NOT_DEPLOYED`;
- public/shared ingress: `NOT_ACTIVE`;
- production/live: `NOT_OPERATIONAL`;
- no direct cross-project canonical-store mutation;
- canonical factual-verification authority: P13.5/P13.6.
