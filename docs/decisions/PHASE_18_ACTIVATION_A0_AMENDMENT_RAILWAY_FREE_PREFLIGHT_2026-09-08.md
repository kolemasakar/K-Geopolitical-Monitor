# Phase 18 Activation A0 Amendment — Railway Free Disposable Preflight

Date: 2026-09-08
Project: K-Geopolitical Monitor
Owner choice: `3 — AMEND A0`
Supersedes only the active A0 provider selection in `PHASE_18_ACTIVATION_A0_RENDER_DISPOSABLE_PROVIDER_DECISION_2026-09-08.md`.
Historical Render evidence remains factual and is not deleted or rewritten.

## Decision

`A0_AMENDMENT = APPROVED`

`A0_PROVIDER = RAILWAY`

`A0_TARGET = RAILWAY_FREE_OR_FREE_TRIAL_DISPOSABLE_NONPROD`

`PROVIDER_PIVOT = AUTHORIZED_FOR_FREE_DISPOSABLE_NONPROD_PREFLIGHT_ONLY`

`PAID_PROVIDERS = NONE_APPROVED`

`RAILWAY_PAID_UPGRADE = NOT_AUTHORIZED`

`A1 = READY_TO_RESUME_AFTER_RAILWAY_ACCOUNT_CONNECTION_AND_INVENTORY`

The amendment authorizes creation of a new, dedicated KGM Railway project only when the Railway account/plugin connection is available and the project can remain inside the no-cost Free/Free-Trial boundary. It does not authorize paid Railway usage, durable provider selection, production activation, canonical cutover, or reuse of another project's resources.

## Why Railway is selected for the amended disposable preflight

Official Railway documentation checked on 2026-09-08 establishes the following relevant characteristics:

- Railway Free is `$0/month` and provides a small monthly free usage credit after the initial free trial;
- the initial free trial provides a one-time credit and permits code and database deployment;
- PostgreSQL services are private by default and require an explicit TCP proxy/public-network action before external database exposure;
- services in the same Railway project/environment can communicate over Railway private networking using internal DNS;
- private-network service traffic is encrypted and does not traverse the public internet;
- public web services can use Railway-managed HTTPS/SSL domains;
- project service variables can hold credentials/secrets outside source code;
- resource usage is metered, so the Free/Trial candidate is suitable only for disposable validation and must not be represented as a durable zero-cost production recommendation.

Primary official references used for this amendment:

- `https://railway.com/pricing`
- `https://docs.railway.com/pricing/free-trial`
- `https://docs.railway.com/networking/private-networking`
- `https://docs.railway.com/databases/postgresql`
- `https://docs.railway.com/networking/public-networking`

## Rejected alternatives for this amended preflight

### Neon Free

Not selected because private networking and IP allow-list controls are associated with higher Neon capability tiers. A public database endpoint would weaken the approved non-public datastore-path boundary.

### Supabase Free

Not selected for the first automated candidate because the split-provider app/database topology increases operational complexity. Network restrictions may reduce public exposure, but the current execution environment has no connected Supabase management capability and no advantage over Railway's same-project private networking for this disposable test.

### OCI Always Free

Retained as a cost-optimized fallback. It can satisfy the private PostgreSQL topology and remain free within Always Free allowances, but requires materially more host, firewall, TLS, PostgreSQL, patching, backup and recovery operations. It is therefore not the preferred fast A1/A2 validation path while Railway offers a managed private-network candidate.

### Render

The original free Render candidate remains historically valid, but A1 cannot continue there without either reusing another project's database, waiting for the free DB quota to be released, or authorizing paid database capacity. None of those actions is implied by this amendment.

## Railway A1 topology contract

Target topology:

`Internet client -> Railway HTTPS service -> Railway private network -> dedicated KGM PostgreSQL`

Required controls:

- one new Railway project dedicated to KGM preflight;
- application and PostgreSQL in the same project/environment;
- PostgreSQL remains private by default;
- no TCP proxy / no database public endpoint;
- application uses private `DATABASE_URL`, never `DATABASE_PUBLIC_URL`;
- only the FastAPI preflight service receives a public HTTPS domain;
- credentials and bearer secret are Railway service variables, never committed;
- synthetic tenant/project identifiers only;
- schema remains `kgm_preflight`;
- no canonical owner-local SQLite access;
- no migration `033`;
- no private/sensitive canonical data copy;
- no auto-promotion or cutover;
- hard/free usage boundary must be checked before provisioning and monitored during A1/A2.

## Cost boundary

`SPEND_APPROVAL = NOT_GRANTED`

The candidate must remain within Railway Free/Free-Trial credits. Any requirement to enter a paid Railway plan, add a paid minimum commitment, or continue after free credits are exhausted is a new owner spend gate.

The free candidate is disposable evidence infrastructure only. It is not a production cost recommendation.

## Render shell disposition

The previously created Render web-service shell `kgm-shared-runtime-preflight` remains non-operational and fail-closed. This amendment does not authorize attaching it to Railway PostgreSQL or turning it into a split-provider candidate.

`RENDER_WEB_SHELL = HISTORICAL_FAIL_CLOSED_NONOPERATIONAL`

`RENDER_TO_RAILWAY_SPLIT_TOPOLOGY = NOT_AUTHORIZED`

## Immutable boundaries preserved

`PHASE_18_SHARED_RUNTIME_ACTIVE = NO`

`P18_9_LAUNCH_ELIGIBLE = FALSE`

`PROJECT_LOCAL_ONLY = CANONICAL`

`MIXED_SHARED_CANONICAL_RUNTIME = BLOCKED`

`MIGRATION_033 = NOT_CREATED / NOT_PREAUTHORIZED`

`PAID_PROVIDERS = NONE_APPROVED`

`PRODUCTION_LIVE = NOT_OPERATIONAL`

`PHASE_18_SHARED_RUNTIME_NONPROD_CANDIDATE_CREATED = NO`

No A2 security/network/recovery gate may be claimed until the dedicated Railway application and PostgreSQL candidate exist and are directly observed.