# SECURITY_AND_DATA_POLICY

Version: 0.7
Status: APPROVED / P12_3_VALIDATED

## Principles

- Preserve provenance.
- Use least privilege unless an explicit owner-approved exception exists.
- Keep credentials/secrets out of repository state and routine logs.
- Security/operational claims require reproducible evidence.
- Governance, adapter or availability metadata cannot be promoted into truth or production acceptance.

## Canonical Storage

- runtime storage: `PROJECT_LOCAL_ONLY`;
- shared/mixed canonical runtime storage: not approved;
- direct cross-project canonical mutation: prohibited without a new architecture approval.

Runtime storage mode: PROJECT_LOCAL_ONLY

## Secret / Logging Policy

- credentials, tokens and private keys are not stored in repository files;
- credentialed integrations require explicit approval and environment/platform secret handling;
- secret-bearing URLs/commands and authorization headers must not enter routine logs;
- keyword scans are supporting evidence, not proof of exhaustive secret absence.

## Owner-Only Runtime

E9A remains `OWNER_ONLY_PRODUCTION_CANDIDATE_READY / COMPLETE`.

Remaining explicit owner-approved candidate networking exceptions:
- public SSH TCP/22 from `0.0.0.0/0`;
- broad outbound egress.

Production/live operational status: NOT_OPERATIONAL

## Source / Adapter Security Rules

P12.1/P12.2 rules remain mandatory:
- public-anonymous sources cannot require credentials;
- operational sources require approved governance;
- approved sources require exact adapter identity/version and outbound host;
- public-anonymous acquisition is read-only HTTPS GET;
- non-HTTPS URLs, URL credentials and credential-bearing headers fail closed;
- timeout, response-size and record-count bounds apply;
- source failures remain isolated and visible;
- paid provider approval requires separate explicit owner approval.

## P12.3 Security Result

The priority authoritative pack uses public anonymous HTTPS only and introduces no credentials or paid provider.

Validated operational states:
- European Commission — `ACTIVE`;
- European Parliament — `DEGRADED` because the official endpoint returns anti-bot HTML to the unattended runner;
- GOV.UK — `ACTIVE`;
- OSCE — `ACTIVE`.

No attempt is authorized to bypass European Parliament anti-bot controls. No third-party mirror is promoted to canonical source status as a workaround.

P12.5 owns measured egress inventory and any later egress-restriction proposal.

## Public Exposure Boundary

- public KGM HTTP/HTTPS/API/dashboard ingress: not approved/deployed;
- backend HTTPS: not deployed;
- private GPT Action: not connected;
- public GPT sharing: user-deferred;
- shared/team runtime: not approved;
- production/live: `NOT_OPERATIONAL`.

## Start.me

`START_ME_DATA_POLICY = PUBLIC_NON_SENSITIVE_ONLY`.
Start.me must not store credentials, private endpoints, canonical monitoring/runtime state, private findings/alerts, sensitive information or canonical evidence/provenance/coverage authority.

## Current State

- P12.0-P12.3: `VALIDATED`;
- P12.3 controlled-live state: 3 `ACTIVE`, European Parliament `DEGRADED`;
- P12.4: `NEXT / NOT_STARTED`;
- paid providers: `NONE_APPROVED`;
- runtime storage: `PROJECT_LOCAL_ONLY`;
- public API/dashboard: `NOT_APPROVED / NOT_DEPLOYED`;
- production/live: `NOT_OPERATIONAL`.
