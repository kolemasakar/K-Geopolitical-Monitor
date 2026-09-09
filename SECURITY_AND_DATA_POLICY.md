# SECURITY_AND_DATA_POLICY

Version: 1.0
Status: APPROVED / ROADMAP_V4_22_SYNCHRONIZED / PHASE_17_BOUNDARIES_CURRENT
Canonical state contract: `docs/state/CURRENT_PROJECT_STATE.json`

## Principles

- Preserve provenance.
- Use least privilege unless an explicit owner-approved exception exists.
- Keep credentials/secrets out of repository state and routine logs.
- Security/operational claims require reproducible evidence.
- Governance, adapter, language, availability, freshness, forecast, delivery or publication metadata cannot be promoted into factual truth or production acceptance.

## Canonical Storage

- runtime storage: `PROJECT_LOCAL_ONLY`;
- shared/mixed canonical runtime storage: `BLOCKED`;
- direct cross-project canonical mutation is prohibited without a new architecture approval;
- Phase 18 shared/team runtime remains `CONDITIONAL / NEW_ARCHITECTURE_APPROVAL_REQUIRED`.

Runtime storage mode: PROJECT_LOCAL_ONLY
Production/live operational status: NOT_OPERATIONAL

## Secret / Logging Policy

- credentials, tokens and private keys are not stored in repository files;
- credentialed integrations require explicit approval and platform secret handling;
- secret-bearing URLs/commands and authorization headers must not enter routine logs;
- Phase 16/17 redaction and data minimization occur before transport/export boundaries.

## Owner-Only Runtime

E9A remains `OWNER_ONLY_PRODUCTION_CANDIDATE_READY / COMPLETE`.

Remaining explicit owner-approved candidate networking exceptions:
- public SSH TCP/22 from `0.0.0.0/0`;
- broad outbound egress.

Phase 14 is `PHASE_14_OWNER_OPERATIONAL_INTELLIGENCE_READY / VALIDATED_READY / NOT_ACTIVATED` and `OWNER_ONLY_OPERATIONAL_ACTIVATION = OWNER_DECISION_REQUIRED`.

## Source / Adapter Security Rules

Historical Phase 12 rules remain mandatory:
- public-anonymous sources cannot require credentials;
- approved sources require governed adapter identity/version and outbound host;
- public-anonymous acquisition is read-only HTTPS GET;
- non-HTTPS URLs, URL credentials and credential-bearing headers fail closed;
- timeout, response-size and record-count bounds apply;
- source failures remain isolated and visible;
- paid provider approval requires separate explicit owner approval.

European Parliament remains a retained historical governed `DEGRADED` source where unattended acquisition was measured `UNAVAILABLE / PARSER`; no anti-bot bypass is authorized. Historical P12.5 observations for Haberturk and OSCE remain explicit and non-promotional to truth.

## Semantic / Forecast / Delivery Security Boundary

- P13.5/P13.6 is the canonical factual-verification authority;
- legacy scalar/count verification metadata cannot bypass it;
- Phase 15 forecast probability/calibration/performance state cannot promote factual verification;
- Phase 16 delivery receipts, acknowledgements and operator feedback cannot promote factual verification;
- real external delivery providers remain `NOT_ACTIVATED` unless separately approved;
- provider failures are isolated from canonical intelligence persistence.

## Phase 17 Public-Safety Boundary

Phase 17 is `PHASE_17_CONTROLLED_EXTERNAL_PUBLICATION_READINESS_VALIDATED / VALIDATED_READY / NOT_ACTIVATED`.

- current account publication capability: `UNAVAILABLE`;
- capability gate: `PHASE_17_EXTERNAL_PUBLICATION_BLOCKED_BY_CURRENT_ACCOUNT_CAPABILITY`;
- activation gate: `PHASE_17_ACTIVATION_REQUIRES_EXPLICIT_OWNER_DECISION`;
- owner approval alone cannot bypass unavailable platform/account capability;
- strict public allowlists, redaction and data minimization precede export;
- owner/admin tokens, credentials, private DB paths, raw operator feedback and non-public diagnostics are forbidden in public payloads;
- release receipts/engagement are not truth operators;
- migration `033` is `NOT_CREATED / NOT_PREAUTHORIZED`;
- external publication targets remain `NOT_ACTIVATED`.

## Public Exposure Boundary

- public KGM HTTP/HTTPS/API/dashboard ingress: `NOT_APPROVED / NOT_DEPLOYED`;
- backend HTTPS: `NOT_DEPLOYED`;
- private GPT Action: `NOT_CONNECTED`;
- public GPT sharing: `NOT_ACTIVE`;
- production/live: `NOT_OPERATIONAL`;
- paid providers: `NONE_APPROVED`.

## Start.me

`START_ME_DATA_POLICY = PUBLIC_NON_SENSITIVE_ONLY`.
Start.me must not store credentials, private endpoints, canonical monitoring/runtime state, private findings/alerts, sensitive information or canonical evidence/provenance/coverage authority.

## Current State

- Phase 12 source/security baseline: `VALIDATED_WITH_KNOWN_LIMITATIONS`;
- Phase 13 semantic verification: `VALIDATED`;
- Phase 14: `VALIDATED_READY / NOT_ACTIVATED / OWNER_DECISION_REQUIRED`;
- Phase 15: `VALIDATED`;
- Phase 16: `VALIDATED`;
- Phase 17: `VALIDATED_READY / NOT_ACTIVATED / EXTERNAL_PUBLICATION_BLOCKED_BY_CURRENT_ACCOUNT_CAPABILITY`;
- Phase 18: `CONDITIONAL / NEW_ARCHITECTURE_APPROVAL_REQUIRED`;
- paid providers: `NONE_APPROVED`;
- runtime storage: `PROJECT_LOCAL_ONLY`;
- production/live: `NOT_OPERATIONAL`.
