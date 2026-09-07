# Phase 18 Architecture Approval Gate

Status: PENDING_OWNER_APPROVAL
Date: 2026-09-07
Project: K-Geopolitical Monitor
Architecture preflight: `docs/implementation/PHASE_18_SHARED_TEAM_RUNTIME_ARCHITECTURE_PREFLIGHT.md`

## Decision Required

Phase 18 requires a new architecture approval before any shared/team runtime implementation or activation.

This record intentionally does **not** approve that architecture.

Current gate state:

- `PHASE_18_ARCHITECTURE_PREFLIGHT = COMPLETE`;
- `PHASE_18_NEW_ARCHITECTURE_APPROVAL = PENDING_OWNER_DECISION`;
- `PHASE_18_IMPLEMENTATION_AUTHORIZED = NO`;
- `PHASE_18_SHARED_RUNTIME_ACTIVE = NO`;
- `PHASE_18_REQUIRES_NEW_ARCHITECTURE_APPROVAL` remains in force;
- migration `033` remains `NOT_CREATED / NOT_PREAUTHORIZED`;
- `PROJECT_LOCAL_ONLY` remains the canonical runtime storage mode;
- mixed/shared canonical runtime remains `BLOCKED`;
- paid providers remain `NONE_APPROVED`;
- production/live remains `NOT_OPERATIONAL`.

## Architecture Proposed for Approval

The preflight recommends:

- preserve the existing owner-only project-local SQLite runtime unchanged as the validated compatibility/rollback profile;
- create a separate shared/team runtime profile rather than converting the current SQLite database in place;
- use a PostgreSQL-compatible transactional relational shared datastore, or a demonstrably equivalent datastore class, with explicit workspace/project tenancy;
- enforce tenant isolation at application/repository/database-policy layers;
- separate standards-based authentication from deny-by-default RBAC;
- retain separate owner-only strategic gates;
- use versioned/idempotent transactional write contracts and auditable security/publication-sensitive mutations;
- prohibit direct cross-project canonical-store mutation;
- require HTTPS, non-public datastore ingress, secrets isolation, threat-model validation, backup/restore and rollback evidence;
- perform staged shadow/canary migration with the current project-local store remaining canonical until explicit cutover approval;
- select no provider and incur no paid-provider commitment as part of this architecture decision alone.

## Owner Approval Must Resolve

An explicit approval should confirm or amend at least these architecture choices:

- separate shared/team runtime profile versus any alternative;
- transactional shared datastore class;
- `workspace_id` / `project_id` tenancy boundary;
- RBAC role model and owner-only permissions;
- identity/authentication approach;
- cross-project sharing contract;
- concurrency/idempotency/audit model;
- migration and rollback approach;
- backup/DR requirements;
- acceptable cost envelope and provider-selection process.

## What Approval Will Not Automatically Authorize

Even an owner approval of this architecture will not by itself mean:

- production/live activation;
- public sharing or Phase 17 publication activation;
- a specific paid provider purchase;
- deployment to a public endpoint;
- migration `033` execution;
- destructive conversion of the current SQLite store;
- bypass of subsequent implementation, security, migration, regression, DR or activation gates.

## Current Decision

`DECISION = PENDING_OWNER_APPROVAL`

Until an explicit owner architecture approval is recorded, Phase 18 implementation is **NO-GO**.