# EXTERNAL_INTEGRATIONS

Version: 2.1
Status: APPROVED / ROADMAP_V4_34_SYNCHRONIZED / PHASE_18_A1_PREFLIGHT_VALIDATED / NOT_ACTIVATED
Canonical state contract: `docs/state/CURRENT_PROJECT_STATE.json`

## Purpose

Define governance rules for public sources, external services, cross-project resources, delivery/publication targets, shared-runtime candidates and non-canonical operator tools.

## Source Integration Baseline

Phase 12 source-governance and adapter framework remains validated:
- immutable `source_portfolio_versions` govern source identity/access/adapter/outbound requirements;
- portfolio approval does not establish evidence independence or factual truth;
- bounded read-only HTTPS acquisition and deterministic parsing remain the public-anonymous integration default;
- deterministic CI does not depend on live source availability;
- one source failure remains isolated and visible.

Validated source starting integrations include Consilium Press Releases RSS and GDELT DOC 2.0. GDELT indexing/discovery is not independent factual corroboration.

Historical source observations remain visible and truth-neutral, including European Parliament `UNAVAILABLE / PARSER` with governed degradation and other recorded Phase 12 availability/freshness limitations.

## Integration Truth Boundary

- publisher/publication is not automatically the underlying origin;
- repost/syndication/translation/citation does not create independent corroboration;
- official-source status confirms institutional publication/statement, not automatically the underlying event;
- source/domain/adapter/item/language/host counts are not independent-origin count;
- availability/freshness are operational properties, not truth operators;
- P13.5/P13.6 remains canonical factual-verification authority.

## Phase 15 External Data Boundary

Forecast outcome/calibration/performance layers may reference persisted provenance-bound evidence, but probability, calibration and performance metrics are not factual-verification operators. No paid outcome-data provider is activated by Phase 15.

## Phase 16 Delivery Integration Boundary

Phase 16 is `PHASE_16_DELIVERY_OPERATOR_QUALITY_LOOP_VALIDATED`.

- provider-neutral transport contract is validated with deterministic local/in-memory sinks;
- Telegram, email, Slack, SMS, push, webhook and other real external delivery channels remain outside validated activation scope unless separately approved;
- no real external delivery provider is activated;
- credentials are not persisted in canonical delivery records;
- redaction/data minimization precedes transport;
- delivery receipts and operator feedback are not event evidence or truth operators.

## Phase 17 Publication Integration Boundary

Phase 17 is `VALIDATED_READY / NOT_ACTIVATED`.

- validated target remains provider-neutral local/in-memory/test only;
- current account external-publication capability: `UNAVAILABLE`;
- any future real publication requires available platform capability plus explicit owner activation and fresh launch-time validation;
- production public API/dashboard ingress remains not approved/deployed;
- public GPT Action remains not connected/approved;
- public sharing remains `NOT_ACTIVE`.

## Phase 18 Shared-Runtime Integration Boundary

Phase 18 architecture is approved and implementation is authorized. P18.0–P18.9 are validated. This supersedes the former `NEW_ARCHITECTURE_APPROVAL_REQUIRED` wording.

A1 now provides concrete disposable non-production candidate evidence:

- Railway project: `kgm-shared-runtime-preflight`;
- canonical A1 application service: `kgm-preflight-api-v3`;
- PostgreSQL candidate: `kgm-preflight-postgres`;
- exact source pin: `8ac2c92c9351ac1bcea8818e52a819f81868ed92`;
- deployment `52c39935-9e89-4f12-82e3-82345c606426`: `SUCCESS`;
- healthcheck `/health`: HTTP 200;
- live startup RLS isolation: PASS;
- database public service domain: none;
- database public TCP proxy: none;
- database network: provider-private internal network;
- no new runtime-role password/DSN/secret was introduced.

This integration remains a **non-production preflight**. Railway's environment name `production` is provider metadata only and does not change KGM operational state.

The generated A1 API HTTPS endpoint is permitted only as a disposable preflight surface. It is not canonical production KGM API/dashboard ingress.

## Cross-Project Boundary

- historical infrastructure may be hybrid, but canonical runtime storage is `PROJECT_LOCAL_ONLY`;
- no shared canonical runtime database is active;
- no implicit mixed canonical storage;
- no direct writes to another project's canonical store;
- A1 does not authorize canonical data migration or cross-project canonical mutation;
- `PHASE_18_SHARED_RUNTIME_ACTIVE = NO`.

## Credentials / Paid Providers

Credentialed sources/targets require explicit approval and external secret handling.
Paid providers: `NONE_APPROVED`.

A free/free-trial disposable preflight candidate is not equivalent to approval of a paid provider or future shared-runtime provider selection.

## Start.me

`START_ME_DATA_POLICY = PUBLIC_NON_SENSITIVE_ONLY`.
Start.me is non-canonical and limited to public, non-sensitive navigation/source material.

## Current State

- state synchronization: `4.35`;
- Phase 12 source portfolio/adapters: validated with recorded limitations;
- Phase 13 verification/provenance: validated;
- Phase 16 delivery integration architecture: validated, real providers not activated;
- Phase 17 publication readiness: validated, real publication not activated;
- Phase 18 P18.0–P18.9: validated;
- Phase 18 A1 concrete Railway/PostgreSQL RLS preflight: validated;
- Phase 18 shared runtime: `NOT_ACTIVATED`;
- migration `033`: `NOT_CREATED / NOT_PREAUTHORIZED`;
- paid providers: `NONE_APPROVED`;
- production KGM public ingress: `NOT_APPROVED / NOT_DEPLOYED`;
- runtime storage: `PROJECT_LOCAL_ONLY`;
- production/live: `NOT_OPERATIONAL`.

Production/live operational status: NOT_OPERATIONAL
Runtime storage mode: PROJECT_LOCAL_ONLY
