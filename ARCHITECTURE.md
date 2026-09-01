# ARCHITECTURE
Technical architecture definition for K-Geopolitical Monitor.

Version: 3.2
Status: APPROVED / ROADMAP_V4_SYNCHRONIZED / P12_1_VALIDATED

## Architecture Principle

Preserve the validated engineering spine while improving intelligence quality and public-source breadth.

Current numbered phase:
`Phase 12 — Intelligence Quality and Source Network Foundation`

Validated gates:
- `P12_0_CANONICAL_CONVERGENCE_VALIDATED`;
- `P12_1_SOURCE_PORTFOLIO_CONTRACT_VALIDATED`.

Next activity:
`P12.2_LIVE_ADAPTER_FRAMEWORK_V2 / NEXT_NOT_STARTED`.

## Logical Architecture

`Public Sources -> Source Portfolio / Adapters -> Acquisition -> Ingestion -> Translation Representation -> Normalization -> Claims / Evidence / Events -> Verification -> Analysis / Graph -> Forecasting -> Reporting -> Monitoring / Coverage / Alerts -> Owner Interaction`

The private GPT is an interaction/orchestration surface, not the unattended runtime or canonical state store.

## Canonical Source / Portfolio Boundary

- `sources` remains the minimal canonical source-identity table.
- `source_portfolio_versions` is additive immutable governance metadata over source identity.
- Portfolio versions record publisher identity, class/role, region/language, access/cost/authentication, cadence/freshness, adapter identity, outbound host/protocol requirements, fallback, availability, data classification, origin/provenance characteristics, independence constraints, terms and review state.
- portfolio registration/approval does not activate collection;
- portfolio metadata does not establish evidence independence;
- source reputation history remains a separate contextual subsystem;
- collection/provenance/coverage/verification stores remain separate canonical concerns.
- new source activation requires later adapter/integration work.

P12.1 seeded no new external live source.

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

E9A:
`OWNER_ONLY_PRODUCTION_CANDIDATE_READY / COMPLETE`.

Validated properties include owner-only OCI ARM64 operation, hardened systemd, project-local SQLite durability, single-instance leasing, backup/restore, reboot/recovery, runtime-health instrumentation and persistent removal of rpcbind TCP/UDP port 111.

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

P12.2 may modernize adapters but must consume rather than bypass P12.1 governance.

## Truth Boundary

- publisher/publication is not automatically underlying origin;
- repost/syndication/translation/citation does not create independent corroboration;
- official statements prove what was stated, not automatically the underlying event;
- source reputation and portfolio governance do not determine truth;
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
- P12.2: `NEXT / NOT_STARTED`;
- migration 022/source portfolio: `VALIDATED`;
- controlled-live integrations: Consilium RSS + GDELT DOC 2.0;
- paid providers: `NONE_APPROVED`;
- runtime storage: `PROJECT_LOCAL_ONLY`;
- production/live: `NOT_OPERATIONAL`.
