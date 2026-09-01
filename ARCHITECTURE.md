# ARCHITECTURE
Technical architecture definition for K-Geopolitical Monitor.

Version: 3.3
Status: APPROVED / ROADMAP_V4_SYNCHRONIZED / P12_2_VALIDATED

## Architecture Principle

Preserve the validated engineering spine while improving intelligence quality and public-source breadth.

Current numbered phase:
`Phase 12 — Intelligence Quality and Source Network Foundation`

Validated gates:
- `P12_0_CANONICAL_CONVERGENCE_VALIDATED`;
- `P12_1_SOURCE_PORTFOLIO_CONTRACT_VALIDATED`;
- `P12_2_ADAPTER_FRAMEWORK_V2_VALIDATED`.

Next activity:
`P12.3_PRIORITY_AUTHORITATIVE_SOURCE_PACK / NEXT_NOT_STARTED`.

## Logical Architecture

`Public Sources -> Source Portfolio -> Governed Adapter Framework -> Acquisition -> Ingestion -> Translation Representation -> Normalization -> Claims / Evidence / Events -> Verification -> Analysis / Graph -> Forecasting -> Reporting -> Monitoring / Coverage / Alerts -> Owner Interaction`

The private GPT is an interaction/orchestration surface, not the unattended runtime or canonical state store.

## Canonical Source / Portfolio Boundary

- `sources` remains the minimal canonical source-identity table;
- `source_portfolio_versions` is immutable governance metadata over source identity;
- portfolio registration/approval does not activate collection;
- portfolio metadata does not establish evidence independence;
- source reputation history remains separate contextual state;
- collection/provenance/coverage/verification stores remain separate canonical concerns.

## P12.2 Adapter Framework Boundary

`src/kgeopolitical_monitor/adapter_framework.py` is an additive facade over the validated M7 `LiveSourceCollector`, not a parallel ingestion system.

Framework properties:

- public-anonymous acquisition uses bounded read-only HTTPS GET;
- non-HTTPS URLs, URL-embedded credentials and credential-bearing headers fail closed;
- RSS and Atom share deterministic feed parsing;
- JSON-list adapters use bounded record parsing;
- source ID, adapter ID/version and stable item identity are explicit;
- collection requires a current P12.1 portfolio record matching canonical source identity, approval state, public access, adapter version and outbound hostname;
- governance is rechecked at collection time to detect drift;
- canonical source-collection attempts, raw items and live-source provenance remain the persistence path;
- E6 reproducibility remains the audit path for exact query, adapter identity/version and persisted artifact hashes;
- uninstrumented exact request locators remain `NOT_INSTRUMENTED` rather than reconstructed;
- one adapter failure remains isolated from other adapters by the underlying validated collector.

P12.2 seeded no new external live source and made no automatic runtime switch to v2 adapter definitions.

## Runtime / Storage Boundary

Mandatory rules:

- runtime storage: `PROJECT_LOCAL_ONLY`;
- no implicit mixed storage;
- no shared runtime database;
- no direct cross-project canonical-store mutation;
- shared/mixed canonical runtime storage requires a new architecture approval.

Runtime storage mode: PROJECT_LOCAL_ONLY
E9 Shared Production Runtime: `NOT_APPROVED`.

## Owner-Only Runtime Boundary

E9A remains `OWNER_ONLY_PRODUCTION_CANDIDATE_READY / COMPLETE`.

Remaining explicit owner-approved candidate networking exceptions:

- public SSH TCP/22 from `0.0.0.0/0`;
- broad outbound egress.

Production/live operational status: NOT_OPERATIONAL

## External Integration Boundary

Validated starting live integrations remain:

- Consilium press-release RSS — official public read-only source;
- GDELT DOC 2.0 — public discovery/index metadata.

GDELT discovery is not independent factual corroboration.

Phase 12 source-network rules:

- public/free first;
- explicit source-portfolio/integration governance;
- exact source/adapter identity;
- read-only/fail-closed acquisition;
- deterministic fixture testing independent of live networks;
- isolated source failures;
- explicit outbound host/protocol inventory;
- no paid provider approval by Phase 12 alone.

P12.3 must onboard each authoritative source through P12.1 governance and a P12.2-compatible adapter path rather than bypassing either layer.

## Truth Boundary

- publisher/publication is not automatically underlying origin;
- repost/syndication/translation/citation does not create independent corroboration;
- official statements prove what was stated, not automatically the underlying event;
- source reputation, portfolio approval and adapter availability do not determine truth;
- graph inference cannot promote verification;
- forecast probability/confidence cannot promote factual verification;
- coverage metrics cannot promote factual confidence;
- report rendering cannot strengthen evidence;
- `GLOBAL` is scope, not proof of exhaustive world coverage;
- unavailable persisted backend state cannot be substituted with ad hoc web research.

## Backend / Dashboard / GPT Boundary

- E3 backend API foundation: `BASELINE_VALIDATED / HTTPS_NOT_DEPLOYED`;
- private GPT backend Action: `NOT_CONNECTED`;
- E5 dashboard: `LOCAL_PROTECTED / READ_ONLY / NOT_DEPLOYED`;
- public Action/API/dashboard ingress: `NOT_APPROVED / NOT_DEPLOYED`;
- public GPT sharing: `USER_DEFERRED`.

## Start.me Boundary

`START_ME_DATA_POLICY = PUBLIC_NON_SENSITIVE_ONLY`.

Start.me is non-canonical and cannot hold credentials, private endpoints, canonical runtime state, sensitive findings or canonical evidence/provenance/coverage authority.

## Current State

- ROADMAP: `APPROVED / v4`;
- P12.0: `VALIDATED`;
- P12.1: `VALIDATED`;
- P12.2: `VALIDATED`;
- P12.3: `NEXT / NOT_STARTED`;
- controlled-live integrations: Consilium RSS + GDELT DOC 2.0;
- additional external sources activated by P12.2: `NONE`;
- paid providers: `NONE_APPROVED`;
- runtime storage: `PROJECT_LOCAL_ONLY`;
- production/live: `NOT_OPERATIONAL`.
