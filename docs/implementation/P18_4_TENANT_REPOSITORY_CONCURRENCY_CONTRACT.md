# P18.4 — Tenant-Scoped Repository, Write, Idempotency and Concurrency Contract

Status: `IMPLEMENTATION_CANDIDATE / AWAITING_FULL_REGRESSION`
Date: 2026-09-07
Project: K-Geopolitical Monitor
Base: `8f4b37186e49523a1502c55295c0a9cf3c58dbc1`
Gate target: `P18_4_TENANT_REPOSITORY_CONCURRENCY_VALIDATED`

## Purpose

P18.4 defines and tests the provider-neutral service/repository semantics required before a real shared canonical datastore adapter may be implemented.

This step does **not** deploy a shared database, choose a provider, allocate a migration, activate shared runtime, or change the current canonical store.

The currently active canonical storage remains project-isolated owner-only SQLite. Its physical location may be the owner-controlled Oracle OCI ARM64 runtime host, but its security/storage mode remains `PROJECT_LOCAL_ONLY`; it is not a shared multi-tenant canonical datastore.

## Repository boundary

Every shared canonical repository method must require all of the following:

- an authenticated `AuthenticatedPrincipal`;
- an explicit `TenantContext` containing `workspace_id` and `project_id`;
- a server-side `RoleBindingResolver`;
- the permission appropriate to the operation.

Canonical reads require `CANONICAL_READ` and canonical writes require `CANONICAL_MUTATE`. Repository methods do not trust a global object identifier as an authorization boundary.

Object storage keys are modeled as:

`(workspace_id, project_id, object_type, object_id)`

This prevents the same object identifier in another workspace/project from becoming an implicit cross-tenant lookup path.

## Idempotency contract

Every retryable canonical write requires a non-empty idempotency key.

The idempotency namespace is tenant-scoped:

`(workspace_id, project_id, idempotency_key)`

A deterministic SHA-256 command fingerprint binds the key to:

- object type;
- object id;
- canonicalized payload;
- expected object version.

Exact retries replay the original successful result without incrementing version or duplicating the mutation. Reuse of the same key for a materially different command fails closed with `IdempotencyConflictError`.

A failed optimistic-concurrency attempt does not publish an idempotency receipt, so a corrected retry can subsequently succeed.

## Optimistic concurrency contract

Every mutation carries `expected_version`.

- `expected_version = 0` means create-if-absent;
- an update must present the last observed positive version;
- success increments the version exactly once;
- stale writers receive deterministic `VersionConflictError(expected_version, current_version)`;
- no silent last-write-wins behavior is permitted.

The in-memory contract harness uses one lock around version check, canonical mutation and idempotency receipt publication to model the required atomic transaction boundary. This is validation scaffolding, not a production persistence implementation.

## Negative isolation matrix

The P18.4 regression suite covers:

- unauthenticated read/write denial;
- read/write RBAC enforcement;
- service identity without implicit canonical-mutate authority;
- cross-workspace authorization denial;
- cross-project object-identifier guessing;
- same object id isolated across workspaces/projects;
- list queries scoped to exact workspace/project/object type;
- duplicate retry replay without duplicate effect;
- idempotency-key collision rejection;
- tenant-scoped idempotency namespaces;
- deterministic stale-writer conflicts;
- two concurrent writers from one version producing one winner and one conflict;
- non-deterministic/non-JSON payload rejection;
- no idempotency receipt after failed version conflict.

## Non-goals and preserved gates

P18.4 does not authorize or perform:

- migration `033` creation or execution;
- any other repository migration allocation;
- provider selection or spending;
- PostgreSQL/Oracle/other shared datastore provisioning;
- public/shared ingress;
- shared-runtime activation;
- canonical cutover;
- production/live transition;
- destructive conversion of the owner-only SQLite store.

Required unchanged boundaries:

- `PHASE_18_SHARED_RUNTIME_ACTIVE = NO`;
- canonical storage mode `PROJECT_LOCAL_ONLY`;
- mixed/shared canonical runtime `BLOCKED`;
- migration `033` `NOT_CREATED / NOT_PREAUTHORIZED`;
- paid providers `NONE_APPROVED`;
- production/live `NOT_OPERATIONAL`.

Formal P18.4 closure and ROADMAP/state synchronization must occur only after implementation PR validation and exact-main x64/native ARM64 acceptance are GREEN.
