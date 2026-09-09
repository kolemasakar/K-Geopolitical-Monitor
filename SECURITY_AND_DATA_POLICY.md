# SECURITY_AND_DATA_POLICY

Version: 1.1
Status: APPROVED / ROADMAP_V4_34_SYNCHRONIZED / PHASE_18_A1_PREFLIGHT_VALIDATED / NOT_ACTIVATED
Canonical state contract: `docs/state/CURRENT_PROJECT_STATE.json`

## Principles

- Preserve provenance.
- Use least privilege unless an explicit owner-approved exception exists.
- Keep credentials/secrets out of repository state and routine logs.
- Security/operational claims require reproducible evidence.
- Governance, adapter, language, availability, freshness, forecast, delivery, publication or provider metadata cannot be promoted into factual truth or production acceptance.
- `IMPLEMENTED != VALIDATED != ACTIVATED != PRODUCTION_LIVE`.

## Canonical Storage

- runtime storage: `PROJECT_LOCAL_ONLY`;
- shared/mixed canonical runtime storage: `BLOCKED`;
- direct cross-project canonical mutation remains prohibited;
- Phase 18 P18.0–P18.9 are validated architecture/readiness contracts;
- A1 is a disposable non-production infrastructure preflight only;
- `PHASE_18_SHARED_RUNTIME_ACTIVE = NO`;
- migration `033 = NOT_CREATED / NOT_PREAUTHORIZED`;
- no canonical shared-store cutover has occurred.

Runtime storage mode: PROJECT_LOCAL_ONLY
Production/live operational status: NOT_OPERATIONAL

## Secret / Logging Policy

- credentials, tokens and private keys are not stored in repository files;
- credentialed integrations require explicit approval and platform secret handling;
- secret-bearing URLs/commands and authorization headers must not enter routine logs;
- redaction and data minimization occur before transport/export boundaries;
- A1 introduced no new runtime-role password, DSN or secret;
- documented Railway variable names are configuration metadata only; secret values remain excluded.

## Phase 18 A1 Security Evidence

Canonical implementation anchor: `8ac2c92c9351ac1bcea8818e52a819f81868ed92`.

Validated A1 controls:

- runtime execution role: `kgm_preflight_runtime`;
- `NOLOGIN`, `NOSUPERUSER`, `NOBYPASSRLS`, `NOCREATEDB`, `NOCREATEROLE`, `NOINHERIT`;
- minimal schema/table grants;
- tenant operations use transaction-local role switching;
- startup fails closed unless RLS isolation is observed and alternate-tenant visible rows equal zero;
- live accepted result: `rls_isolation_observed=true`, `alternate_tenant_visible_rows=0`;
- Railway deployment `52c39935-9e89-4f12-82e3-82345c606426`: `SUCCESS`;
- application health: HTTP 200;
- PostgreSQL public service domain: none;
- PostgreSQL public TCP proxy: none;
- database network exposure: private-only provider internal network.

Railway's environment name `production` is provider metadata and must not be interpreted as KGM production/live status.

## Owner-Only Runtime

E9A remains the validated owner-only OCI runtime line. Phase 14 remains `VALIDATED_READY / NOT_ACTIVATED` and `OWNER_ONLY_OPERATIONAL_ACTIVATION = OWNER_DECISION_REQUIRED`.

Historical owner-approved candidate networking exceptions remain documented separately and do not authorize new shared/public KGM ingress.

## Source / Adapter Security Rules

Historical Phase 12 rules remain mandatory:

- public-anonymous sources cannot require credentials;
- approved sources require governed adapter identity/version and outbound host;
- public-anonymous acquisition is read-only HTTPS GET;
- non-HTTPS URLs, URL credentials and credential-bearing headers fail closed;
- timeout, response-size and record-count bounds apply;
- source failures remain isolated and visible;
- paid-provider approval requires separate explicit owner approval.

## Semantic / Forecast / Delivery Security Boundary

- P13.5/P13.6 is the canonical factual-verification authority;
- legacy scalar/count verification metadata cannot bypass it;
- forecast probability/calibration/performance cannot promote factual verification;
- delivery receipts, acknowledgements and operator feedback cannot promote factual verification;
- real external delivery/publication providers remain `NOT_ACTIVATED` unless separately approved;
- provider failures are isolated from canonical intelligence persistence.

## Phase 17 Public-Safety Boundary

Phase 17 remains `VALIDATED_READY / NOT_ACTIVATED`.

- current account publication capability: `UNAVAILABLE`;
- owner approval alone cannot bypass unavailable account/platform capability;
- strict public allowlists, redaction and data minimization precede export;
- owner/admin tokens, credentials, private DB paths, raw operator feedback and non-public diagnostics are forbidden in public payloads;
- release receipts/engagement are not truth operators;
- external publication targets remain `NOT_ACTIVATED`.

## Public Exposure Boundary

- production KGM HTTP/HTTPS/API/dashboard ingress: `NOT_APPROVED / NOT_DEPLOYED`;
- disposable A1 API provider-generated HTTPS endpoint is permitted solely as non-production preflight surface;
- A1 PostgreSQL public ingress: none;
- private GPT Action: `NOT_CONNECTED`;
- public GPT sharing: `NOT_ACTIVE`;
- production/live: `NOT_OPERATIONAL`;
- paid providers: `NONE_APPROVED`.

## Start.me

`START_ME_DATA_POLICY = PUBLIC_NON_SENSITIVE_ONLY`.
Start.me must not store credentials, private endpoints, canonical monitoring/runtime state, private findings/alerts, sensitive information or canonical evidence/provenance/coverage authority.

## Current State

- state synchronization: `4.35`;
- Phase 12–18 validated gates remain as recorded in `ROADMAP.md` and `CURRENT_PROJECT_STATE.json`;
- Phase 18 A1 live non-production RLS preflight: `VALIDATED`;
- Phase 18 shared runtime: `NOT_ACTIVATED`;
- paid providers: `NONE_APPROVED`;
- runtime storage: `PROJECT_LOCAL_ONLY`;
- migration `033`: `NOT_CREATED / NOT_PREAUTHORIZED`;
- production/live: `NOT_OPERATIONAL`.

Latest A1 evidence:
`docs/checkpoints/PROJECT_CHECKPOINT_2026-09-09_PHASE_18_ACTIVATION_A1_RAILWAY_RLS_PREFLIGHT_VALIDATED.md`
