# Project Checkpoint — Phase 18 Activation A0 Validated / A1 Adapter In Progress

Date: 2026-09-08
Project: K-Geopolitical Monitor
Canonical base before this workstream increment: `517199afee3542cea918afc0bd78c4622ddb47c4`

## State

`PHASE_18_SHARED_RUNTIME_ACTIVATION_PREFLIGHT_AUTHORIZED = YES`

`A0 = VALIDATED_FOR_FREE_DISPOSABLE_NONPRODUCTION_PREFLIGHT_ONLY`

`A0_PROVIDER = RENDER`

`A0_REGION = FRANKFURT`

`A0_WORKSPACE = OWNER_CONFIRMED_MY_WORKSPACE`

`A1 = IN_PROGRESS`

`A1_1 = POSTGRES_CANDIDATE_ADAPTER_IN_PROGRESS`

`A1_RESOURCE_CREATION = BLOCKED_UNTIL_GREEN_EXACT_HEAD_ADAPTER_CI`

## Observed Render Inventory

The owner-confirmed workspace was inspected before mutation.

- existing services belong to other projects;
- the existing PostgreSQL database belongs to another project;
- no existing resource is authorized for KGM reuse or mutation;
- no KGM Render service exists yet;
- no KGM Render PostgreSQL instance exists yet.

## Repository Gap Found

P18.3 and P18.4 are validated provider-neutral contracts but do not implement a concrete PostgreSQL connection or persistent repository adapter. The existing FastAPI backend/dashboard surfaces read owner-local SQLite and are not suitable as shared-runtime launch candidates.

A1.1 therefore implements a separate disposable PostgreSQL candidate adapter and preflight API before any Render KGM resource is created.

## A1.1 Safety Contract

- isolated schema `kgm_preflight` only;
- synthetic/non-sensitive probe data only;
- raw probe payload is hashed before persistence;
- PostgreSQL RLS enabled and forced;
- transaction-local workspace/project context;
- parameterized SQL;
- bearer-protected probe endpoints;
- public health endpoint exposes no DSN/token/tenant IDs;
- database errors are redacted;
- no owner-local SQLite access;
- no migration `033`;
- no canonical cutover or activation logic.

## Immutable Boundaries

`PHASE_18_SHARED_RUNTIME_ACTIVE = NO`

`P18_9_LAUNCH_ELIGIBLE = FALSE`

`PROJECT_LOCAL_ONLY = CANONICAL`

`MIXED_SHARED_CANONICAL_RUNTIME = BLOCKED`

`MIGRATION_033 = NOT_CREATED / NOT_PREAUTHORIZED`

`PAID_PROVIDERS = NONE_APPROVED`

`PRODUCTION_LIVE = NOT_OPERATIONAL`

No KGM Render resource may be created until the exact A1.1 branch head is green.
