# SECURITY_AND_DATA_POLICY

Version: 0.9
Status: APPROVED / P12_5_VALIDATED

## Principles

- Preserve provenance.
- Use least privilege unless an explicit owner-approved exception exists.
- Keep credentials/secrets out of repository state and routine logs.
- Security/operational claims require reproducible evidence.
- Governance, adapter, language, availability or freshness metadata cannot be promoted into truth or production acceptance.

## Canonical Storage

- runtime storage: `PROJECT_LOCAL_ONLY`;
- shared/mixed canonical runtime storage: not approved;
- direct cross-project canonical mutation: prohibited without a new architecture approval.

Runtime storage mode: PROJECT_LOCAL_ONLY

## Secret / Logging Policy

- credentials, tokens and private keys are not stored in repository files;
- credentialed integrations require explicit approval and platform secret handling;
- secret-bearing URLs/commands and authorization headers must not enter routine logs.

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

## P12.3 Retained Security State

European Parliament remains governed `DEGRADED` because its official RSS endpoint returns non-feed/anti-bot content to the unattended runner. No bypass is authorized and no third-party mirror is promoted to canonical status.

## P12.4 Security / Data Result

The local-language/media discovery pack uses public anonymous HTTPS only and introduces no credentials, paid provider or new canonical database schema.

P12.4 validation observed successful bounded acquisition/parser paths for Ukrainska Pravda, Meduza, RMF24 and Haberturk. Original-language public content is preserved. Translation remains a separate derived representation. Language/source count does not change data sensitivity, factual verification or independent-origin count.

## P12.5 Security / Egress Result

Gate: `P12_5_SOURCE_HEALTH_EGRESS_INVENTORY_VALIDATED`.

P12.5 measured all ten governed source paths and inventoried ten exact HTTPS host requirements without deploying any network-policy change.

Controlled-live findings remain visible:
- European Parliament — measured `UNAVAILABLE / PARSER`, governed `DEGRADED` retained;
- Haberturk — measured `UNAVAILABLE / UNKNOWN` from invalid item URL validation, governed `ACTIVE` retained pending review;
- OSCE — acquisition healthy while observed content is stale.

No measured failure or freshness result changes truth, verification, independent-origin credit, coverage confidence or production state.

P12.5 did **not** deploy an outbound allowlist. Broad outbound egress remains the explicit owner-approved candidate exception until a separate validated restriction decision changes it.

Measured HTTPS hosts are documented in `docs/implementation/P12_5_CONTROLLED_LIVE_SOURCE_HEALTH_MATRIX.md`.

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

- P12.0-P12.5: `VALIDATED`;
- P12.6: `NEXT / NOT_STARTED`;
- paid providers: `NONE_APPROVED`;
- runtime storage: `PROJECT_LOCAL_ONLY`;
- broad outbound egress: `OWNER_APPROVED_CANDIDATE_EXCEPTION / NOT_RESTRICTED_BY_P12_5`;
- public API/dashboard: `NOT_APPROVED / NOT_DEPLOYED`;
- production/live: `NOT_OPERATIONAL`.
