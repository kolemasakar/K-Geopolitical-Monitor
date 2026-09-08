# Project Checkpoint — Phase 18 Activation A0 Amended / Railway A1 Ready

Date: 2026-09-08
Project: K-Geopolitical Monitor
Canonical base entering amendment: `68b7b0157dcb36e9e8bb1bff4e379b7a52df256c`
Owner decision: `3 — AMEND A0`

## State

`PHASE_18_SHARED_RUNTIME_ACTIVATION_PREFLIGHT_AUTHORIZED = YES`

`A0_AMENDMENT = APPROVED`

`A0_PROVIDER = RAILWAY`

`A0_TARGET = RAILWAY_FREE_OR_FREE_TRIAL_DISPOSABLE_NONPROD`

`PROVIDER_PIVOT = AUTHORIZED_FOR_FREE_DISPOSABLE_NONPROD_PREFLIGHT_ONLY`

`A1_1 = POSTGRES_CANDIDATE_ADAPTER_VALIDATED`

`A1 = READY_TO_RESUME_AFTER_RAILWAY_ACCOUNT_CONNECTION_AND_INVENTORY`

`PHASE_18_SHARED_RUNTIME_NONPROD_CANDIDATE_CREATED = NO`

## Reason for amendment

The validated Render A1 path encountered a real provider quota blocker: the owner-confirmed Render workspace already contains one active free-tier PostgreSQL instance belonging to another project, and a second free instance could not be created.

The owner explicitly selected the A0 amendment path rather than paid Render database capacity or waiting for quota release.

Railway was re-evaluated against the immutable A1/A2 requirements. Its current official documentation supports a disposable managed topology in which PostgreSQL is private by default, same-project traffic uses Railway private networking, and the application can expose HTTPS separately.

## Railway preflight boundary

Authorized only after Railway account/plugin connection and read-only inventory:

- create one dedicated KGM Railway project;
- use Free/Free-Trial only;
- create dedicated PostgreSQL and FastAPI services in the same project/environment;
- leave PostgreSQL without public TCP proxy;
- application connects through private `DATABASE_URL`;
- only app receives public HTTPS domain;
- use synthetic tenant/project data only;
- credentials remain service variables;
- no canonical owner-local data copy;
- no migration `033`;
- no cutover;
- no production claim.

## Provider comparison outcome

- Render free: technically suitable, but blocked by workspace free-DB quota.
- Neon Free: not selected because strict non-public datastore-path evidence is weaker without higher-tier networking controls.
- Supabase Free: viable but operationally less direct for this execution pass; no connected management tool and split-provider topology is unnecessary.
- OCI Always Free: strong zero-cost fallback with full network control, but higher operational/security/DR burden.
- Railway Free/Trial: selected for the amended disposable A1/A2 candidate because app and database can share an isolated private network and PostgreSQL is private by default.

## Render shell

The previously created Render shell remains historical, non-operational and fail-closed.

`RENDER_WEB_SHELL = HISTORICAL_FAIL_CLOSED_NONOPERATIONAL`

It is not authorized to connect to Railway PostgreSQL.

`RENDER_TO_RAILWAY_SPLIT_TOPOLOGY = NOT_AUTHORIZED`

## Next executable gate

`RAILWAY_ACCOUNT_CONNECTION_AND_INVENTORY`

After connection, perform read-only inventory first. Provisioning is allowed only if:

- the account is on Free/Free-Trial or another no-charge state;
- no paid minimum/upgrade is required;
- a dedicated project can be created;
- PostgreSQL private-network behavior can be preserved;
- no unrelated project resource must be reused or mutated.

## Immutable boundaries

`PHASE_18_SHARED_RUNTIME_ACTIVE = NO`

`P18_9_LAUNCH_ELIGIBLE = FALSE`

`PROJECT_LOCAL_ONLY = CANONICAL`

`MIXED_SHARED_CANONICAL_RUNTIME = BLOCKED`

`MIGRATION_033 = NOT_CREATED / NOT_PREAUTHORIZED`

`PAID_PROVIDERS = NONE_APPROVED`

`PRODUCTION_LIVE = NOT_OPERATIONAL`

`A1_TARGET_GATE = NOT_SATISFIED`
