# Phase 18 Shared / Team Runtime Architecture Preflight

Status: PREFLIGHT_COMPLETE_AWAITING_OWNER_ARCHITECTURE_APPROVAL
Date: 2026-09-07
Project: K-Geopolitical Monitor
Baseline HEAD: `5745f1364756e2a5c63f7026385f03110b6fba6b`

## 1. Purpose

This document completes the architecture preflight required before any Phase 18 shared/team runtime implementation may begin.

It does **not** activate Phase 18 implementation, shared runtime storage, multi-user access, public ingress, authentication providers, paid providers, production/live operation, public sharing, or migration `033`.

The existing owner-only runtime remains the canonical validated baseline:

- `PROJECT_LOCAL_ONLY` storage;
- project-local SQLite canonical database;
- one unattended runtime instance protected by an OS-backed lease;
- no mixed/shared canonical runtime;
- no direct cross-project canonical-store mutation;
- production/live `NOT_OPERATIONAL`;
- paid providers `NONE_APPROVED`.

## 2. Preflight Decision

Architecture-preflight decision:

`PHASE_18_ARCHITECTURE_PREFLIGHT = GO`

Implementation decision:

`PHASE_18_IMPLEMENTATION = NO_GO_PENDING_EXPLICIT_OWNER_ARCHITECTURE_APPROVAL`

The preflight is complete enough to present an architecture for approval. It is not approval to build or activate that architecture.

## 3. Current Baseline and Why It Cannot Be Extended In Place

The current runtime deliberately uses an owner-only SQLite profile with bounded write contention, `journal_mode=DELETE`, `synchronous=FULL`, and `DEFERRED` transactions. Canonical storage is constrained to the project-local `data/` directory. The unattended supervisor is single-instance by design and uses an OS file lock.

These are appropriate properties for the validated owner-only runtime, but they are not a safe multi-user tenancy, authorization, distributed coordination, or horizontal-concurrency model.

Therefore Phase 18 must **not** be implemented by simply:

- adding a `user_id` column to selected SQLite tables;
- placing the existing SQLite file on a shared/network filesystem;
- allowing multiple application instances to bypass the current runtime lease;
- permitting multiple projects to write into one current canonical SQLite database;
- exposing the existing owner-only backend API directly to multiple users;
- treating shared folders, Start.me, Google Drive, or another convenience surface as the canonical shared runtime store.

The validated local runtime remains a separate compatibility and rollback profile.

## 4. Target Architecture Boundary

If explicitly approved, Phase 18 should introduce a **separate shared/team runtime profile** behind versioned service contracts.

Recommended logical topology:

```text
Authenticated client / approved integration
                |
                v
        HTTPS application/API boundary
                |
      AuthN -> tenant context -> AuthZ
                |
                v
       versioned application services
                |
      +---------+----------+
      |                    |
      v                    v
transactional shared   immutable/audited
canonical datastore   publication/export path
      |
      v
backup / restore / audit / observability
```

The owner-only project-local profile remains independent:

```text
owner-only runtime -> project-local SQLite -> project-local backup
```

No shared runtime component may silently fall back to, mount, mutate, or co-own the owner-only canonical database.

## 5. Canonical Storage and Tenancy

### 5.1 Datastore class

For an approved shared/team runtime, the recommended canonical datastore class is a PostgreSQL-compatible transactional relational database or another datastore that can demonstrate equivalent properties for:

- concurrent multi-user transactions;
- referential integrity;
- durable constraints;
- predictable locking/isolation;
- backup and point-in-time recovery capability;
- tenant-isolation enforcement at more than the UI layer;
- migration tooling and observable transactional failure semantics.

This is an architectural requirement, **not a provider selection**. No managed database vendor or paid service is approved by this preflight.

### 5.2 Tenant model

Every shared canonical object must belong to an explicit security scope. Minimum hierarchy:

- `workspace_id` — authorization / tenancy boundary;
- `project_id` — canonical K-Geopolitical Monitor project boundary inside a workspace where multi-project operation is approved;
- object primary key / version.

A shared schema must not rely on globally unique object IDs alone as an authorization boundary.

Every canonical read/write contract must carry or derive an authenticated workspace/project context. Repository/service methods must fail closed when that context is absent or ambiguous.

### 5.3 Isolation enforcement

Isolation must be enforced in layers:

- application/service authorization;
- query/repository scoping;
- database constraints and, where supported and validated, row-level security or equivalent database policy;
- automated negative tests proving cross-workspace access is denied.

The required invariant is:

`NO_CROSS_TENANT_CANONICAL_ACCESS_WITHOUT_EXPLICIT_AUTHORIZED_CONTRACT`

### 5.4 Cross-project exchange

The existing prohibition on direct cross-project canonical-store mutation remains permanent unless a later explicit architecture decision replaces it.

Cross-project reuse should occur only through versioned, auditable interfaces such as:

- immutable publication/export artifacts;
- explicit shared references with ownership metadata;
- controlled import/copy operations with provenance;
- separately versioned common contracts.

A consumer project must not directly update another project's canonical rows.

## 6. Authentication and RBAC

Authentication and authorization must be separate controls.

### 6.1 Authentication

Preferred architecture is standards-based identity (OIDC/OAuth2-class or equivalent) behind HTTPS. The identity provider is intentionally **not selected** in this preflight.

Requirements before implementation approval:

- verified identity and stable subject identifier;
- short-lived sessions/tokens;
- secure logout/revocation path;
- MFA capability for privileged roles where supported by the selected identity system;
- no shared owner bearer token as the team authentication model;
- service identities separated from human identities.

### 6.2 Minimum RBAC model

Recommended initial roles:

| Role | Minimum intent |
|---|---|
| `OWNER` | Workspace ownership, security-sensitive configuration, role administration, irreversible approvals |
| `ADMIN` | Project/workspace administration except owner-only irreversible gates |
| `ANALYST` | Create/update analytical and monitoring objects within authorized project scope |
| `VIEWER` | Read authorized project state; no canonical mutation |
| `SERVICE` | Narrow machine identity with explicitly enumerated permissions |

Authorization is deny-by-default. Permission checks belong at the application/service boundary, not only in the UI.

Owner-only strategic gates — including activation gates that are explicitly owner decisions in the roadmap — must remain separately enforceable even if an `ADMIN` role exists.

## 7. Write Semantics, Synchronization and Concurrency

A shared runtime must replace local single-process assumptions with explicit transactional semantics.

Minimum write contract:

- server-generated transaction boundary;
- authenticated workspace/project scope;
- idempotency key for externally retried commands where duplicate execution matters;
- object version / optimistic concurrency token for conflicting edits where last-write-wins is unsafe;
- deterministic conflict response;
- durable audit event for security- or publication-sensitive mutations.

Recommended event/integration pattern:

- canonical transaction commits first;
- externally delivered side effects are emitted through a transactional outbox or equivalent durable handoff;
- retries are idempotent;
- delivery state is not treated as canonical analytical truth.

Do not introduce distributed dual-write semantics between SQLite and a shared datastore as a permanent architecture.

## 8. Threat Model Baseline

Phase 18 adds threats that are not present in the current owner-only/no-public-ingress profile.

Minimum threat set to address before implementation approval:

- cross-tenant data disclosure;
- privilege escalation / broken access control;
- token theft and session replay;
- insecure direct object reference;
- injection into search/query/filter surfaces;
- CSRF where browser credential models make it applicable;
- SSRF through source/integration configuration;
- malicious or compromised external content entering analysis pipelines;
- secrets in logs, exports, backups, CI, support artifacts or public surfaces;
- unauthorized publication/export;
- destructive or accidental bulk mutation;
- denial of service / resource exhaustion by one tenant;
- compromised service identity;
- backup disclosure or restore into the wrong tenant/project;
- audit-log tampering.

Mandatory security principles:

- least privilege;
- deny by default;
- explicit tenant context;
- encryption in transit;
- encrypted off-host backups before any off-host backup is authorized;
- secrets outside source code and canonical analytical data;
- security-relevant audit events append-only from the application perspective;
- no credentials/private endpoints/private findings in Start.me or other public/non-sensitive navigation surfaces.

## 9. Deployment Topology and Network Boundary

No deployment topology is activated by this preflight.

An approved implementation must separate at least:

- HTTPS ingress/application boundary;
- application runtime identity;
- canonical datastore network boundary;
- administrative access path;
- backup destination;
- monitoring/logging boundary.

The database must not be publicly reachable. Administrative access must not depend on an unrestricted public SSH exception as the intended steady-state design.

Provider-specific architecture, regions, instance sizes, managed identity services, managed databases, WAF/CDN, backup services and monitoring products require a separate cost/security comparison and owner approval.

## 10. Backup, Disaster Recovery and Rollback

The current `KGM_RUNTIME_BACKUP_V1` owner-only SQLite bundle remains valid only for the local runtime profile.

The future shared profile requires a separate DR contract including:

- encrypted backups;
- tenant-safe restore procedures;
- schema and migration version capture;
- restore verification;
- tested point-in-time or equivalent recovery where the selected datastore supports it;
- clean-environment restore drill;
- documented failure modes;
- measured RPO/RTO before any service-level claim.

Existing RPO `<=24h` and RTO `<=2h` values are planning objectives, not inherited Phase 18 guarantees.

Rollback must support returning from a failed Phase 18 candidate to the still-valid owner-only runtime without corrupting the project-local SQLite source.

## 11. Migration Strategy

No migration `033` is created or preauthorized by this preflight.

If architecture approval is later granted, migration must proceed as staged migration rather than destructive in-place conversion:

1. freeze and version the shared-schema contract;
2. build an isolated shared datastore in a non-production environment;
3. export/copy a controlled dataset from the local source with provenance;
4. validate row counts, invariants, hashes/semantic reconciliation and authorization scope;
5. run read-only shadow comparisons;
6. test concurrency, tenant isolation, backup/restore and rollback;
7. run a controlled canary with explicit owner authorization;
8. only then consider canonical cutover.

Until cutover is explicitly approved, the current project-local store remains canonical. A failed Phase 18 experiment must be disposable without changing owner-only canonical truth.

## 12. Cost and Provider Gate

Current project state remains:

`PAID_PROVIDERS = NONE_APPROVED`

Architecture approval does not itself approve a provider or spending.

Before provider selection, compare at minimum:

- fixed monthly baseline cost;
- variable database/storage/egress cost;
- backup retention cost;
- authentication/identity cost;
- observability/log retention cost;
- operational burden;
- lock-in / export path;
- regional availability and recovery options;
- security controls required to meet this architecture.

A zero-cost or self-hosted option is not automatically lower-risk or lower-total-cost; operational labor and recovery responsibility must be included.

## 13. Required Validation Matrix Before Phase 18 Activation

All of the following must be evidenced on an approved candidate architecture:

### Tenancy / authorization

- cross-workspace reads denied;
- cross-workspace writes denied;
- cross-project mutation denied unless an explicit versioned contract authorizes it;
- viewer mutation denied;
- analyst/admin/owner boundaries tested;
- owner-only roadmap gates remain owner-only;
- service identities cannot exceed their declared scope.

### Data / concurrency

- migration forward and rollback tested;
- referential/tenant constraints tested;
- duplicate command retry is idempotent;
- conflicting update behavior is deterministic;
- concurrent writer tests pass;
- audit trail correlates actor, scope, action and object version.

### Security

- HTTPS enforced;
- datastore has no public ingress;
- secret scan / log review passes;
- auth/session negative tests pass;
- threat-model controls have test/evidence mapping;
- backup confidentiality and restore isolation tested.

### Recovery / operations

- clean-environment restore passes;
- candidate rollback passes;
- monitoring does not expose private tenant data;
- failure of one tenant/workspace does not silently corrupt another;
- RPO/RTO are measured before being claimed.

### Regression

- owner-only project-local runtime remains valid;
- x64 regression passes;
- native ARM64 regression passes where the owner-only deployment profile remains supported;
- historical epistemic/source/forecast/publication contracts remain green.

## 14. Explicit GO / NO-GO Gate

### GO for architecture approval review

The architecture may proceed to owner review when this preflight and its regression guard are green.

### NO-GO for implementation if any condition remains unresolved

Implementation remains blocked if any of the following is true:

- owner architecture approval absent;
- tenant model ambiguous;
- identity/authentication design absent;
- RBAC/owner-only gates undefined;
- datastore isolation strategy unproven;
- migration/rollback strategy absent;
- backup/DR strategy absent;
- threat-model coverage incomplete;
- provider/cost approval required but absent;
- shared runtime would mutate the existing local canonical SQLite store in place;
- migration `033` is assumed authorized merely because this preflight exists.

## 15. Preflight Outcome

`PHASE_18_ARCHITECTURE_PREFLIGHT = COMPLETE`

`PHASE_18_NEW_ARCHITECTURE_APPROVAL = PENDING_OWNER_DECISION`

`PHASE_18_IMPLEMENTATION_AUTHORIZED = NO`

`PHASE_18_SHARED_RUNTIME_ACTIVE = NO`

`MIGRATION_033 = NOT_CREATED / NOT_PREAUTHORIZED`

`PAID_PROVIDERS = NONE_APPROVED`

`PRODUCTION_LIVE = NOT_OPERATIONAL`

The next strategic action is an explicit owner decision on the architecture contract. No Phase 18 implementation should start before that decision is recorded.