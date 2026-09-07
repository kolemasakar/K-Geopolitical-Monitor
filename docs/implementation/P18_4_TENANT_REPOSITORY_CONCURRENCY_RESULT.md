# P18.4 — Tenant-Scoped Repository, Write, Idempotency and Concurrency Result

Status: `VALIDATED`
Date: 2026-09-07
Project: K-Geopolitical Monitor
Gate: `P18_4_TENANT_REPOSITORY_CONCURRENCY_VALIDATED`
Implementation anchor: `17888993263b1ae7ceda65cd46e7540f1ff17add`

## Exact Implementation Validation

- PR #22 final CI run `34144837471`, job `101814489463`: `895 passed in 144.80s / SUCCESS`; dependency check passed.
- exact-main x64 run `34145082756`, job `101815247999`: `895 passed in 203.00s / SUCCESS`; dependency check passed.
- exact-main native ARM64 run `34145082744`, job `101815247894`: native `aarch64`, `895 passed in 122.97s / SUCCESS`; dependency check, bootstrap shell, unattended one-tick smoke and systemd unit contract passed.
- unattended smoke evidence: `execution_count: 0`, `recovered_runs: 0`.

The implementation commit is signed/verified by GitHub and was the exact checkout for both post-merge implementation validation jobs.

## Validated Contract

P18.4 validates a provider-neutral tenant-scoped repository/concurrency contract with these mandatory properties:

- every shared canonical read/write requires an authenticated principal, explicit `TenantContext`, and server-side role-binding resolution;
- object storage identity includes `workspace_id` + `project_id` + object type + object identifier;
- globally unique object identifiers never substitute for tenant authorization scope;
- retryable writes require tenant-scoped idempotency keys;
- command identity uses deterministic SHA-256 fingerprints;
- command payload is snapshotted to immutable canonical JSON when the command is constructed, so later mutation of the caller's mapping cannot alter the fingerprint or stored payload;
- an exact retry replays the original result and does not duplicate canonical mutation;
- reusing an idempotency key for a different command fails deterministically;
- optimistic concurrency requires an explicit expected version and exposes expected/current versions on stale-writer conflict;
- concurrent writers produce deterministic one-winner/conflict behavior rather than silent last-write-wins;
- cross-workspace/project identifier guessing cannot read or mutate another tenant's canonical object;
- the in-memory harness is contract-only and has no persistence, provider, migration runner, public transport, deployment or activation capability.

## Preserved Boundaries

P18.4 validation does not create or activate a shared datastore.

The following canonical boundaries remain unchanged:

- runtime storage: `PROJECT_LOCAL_ONLY`;
- current owner-only project-local SQLite remains canonical and independently operable;
- mixed/shared canonical runtime: `BLOCKED`;
- shared runtime activation: `PHASE_18_SHARED_RUNTIME_ACTIVE = NO`;
- migration `033`: `NOT_CREATED / NOT_PREAUTHORIZED`;
- paid providers: `NONE_APPROVED`;
- backend HTTPS: `NOT_DEPLOYED`;
- public sharing/shared ingress: `NOT_ACTIVE`;
- production/live: `NOT_OPERATIONAL`;
- no direct cross-project canonical-store mutation is authorized;
- canonical factual verification authority remains P13.5/P13.6.

## Outcome

`P18_4_TENANT_REPOSITORY_CONCURRENCY_VALIDATED`

P18.4 is complete. The next engineering gate is:

`P18_5_AUDIT_OUTBOX_SIDE_EFFECT_ISOLATION_VALIDATED`

P18.5 is `READY_TO_BEGIN` only. This closure does not authorize shared-runtime activation, provider selection, migration `033`, canonical cutover, public/shared ingress or production/live transition.
