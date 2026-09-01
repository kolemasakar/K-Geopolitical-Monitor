# SECURITY_AND_DATA_POLICY

Version: 0.5
Status: APPROVED / P12_1_VALIDATED

## Principles

- Preserve provenance.
- Use least privilege unless an explicit owner-approved exception exists.
- Keep credentials/secrets out of repository state and routine logs.
- Security/operational claims require reproducible evidence.
- Governance metadata cannot be promoted into truth or production acceptance.

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

Validated controls include dedicated service identity, restricted writable path, hardened systemd, no KGM public API/database/dashboard listener, single-instance lease, recovery, backup/restore and persistent port-111 closure.

Remaining explicit owner-approved candidate networking exceptions:

- public SSH TCP/22 from `0.0.0.0/0`;
- broad outbound egress.

Production/live operational status: NOT_OPERATIONAL

## P12.1 Source-Portfolio Security Rules

The versioned portfolio records access mode, cost mode, authentication mode, data classification and exact required outbound HTTPS hostnames.

Fail-closed rules include:

- public-anonymous sources cannot require credentials;
- credentialed/restricted sources require explicit authentication mode;
- restricted/sensitive data cannot be public-anonymous;
- operational availability requires approved review state;
- approved sources require assigned adapter identity/version;
- paid source approval requires separate explicit paid-provider approval;
- a P12.1 portfolio record does not activate collection;
- P12.1 itself approves no paid provider.

P12.5, not P12.1, owns measured egress inventory and any later egress-restriction proposal.

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

- P12.0: `VALIDATED`;
- P12.1: `P12_1_SOURCE_PORTFOLIO_CONTRACT_VALIDATED`;
- P12.2: `NEXT / NOT_STARTED`;
- paid providers: `NONE_APPROVED`;
- runtime storage: `PROJECT_LOCAL_ONLY`;
- public API/dashboard: `NOT_APPROVED / NOT_DEPLOYED`;
- production/live: `NOT_OPERATIONAL`.
