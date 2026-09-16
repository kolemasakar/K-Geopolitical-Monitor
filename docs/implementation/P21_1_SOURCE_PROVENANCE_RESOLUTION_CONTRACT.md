# P21.1 — Existing Portfolio Provenance Resolution Contract

Date: 2026-09-16
Status: `IMPLEMENTED / VALIDATION_PENDING`
Gate: `P21_1_SOURCE_PROVENANCE_RESOLUTION_VALIDATED`

## Purpose

P21.1 resolves as much source-level provenance as the current 10-source governed portfolio can support without converting publisher identity into underlying-origin identity and without awarding claim-level independence from source counts.

## Canonical inputs

- `docs/evidence/P20_0_EXISTING_COVERAGE_BASELINE_2026-09-16.json`
- `docs/evidence/P20_1_SOURCE_TAXONOMY_RECONCILIATION_2026-09-16.json`
- `docs/evidence/P20_3_CURRENT_SOURCE_INDEPENDENCE_BASELINE_2026-09-16.json`
- `docs/evidence/P21_0_TARGET_COVERAGE_POLICY_APPROVAL_2026-09-16.json`

P20 historical evidence is immutable and is not rewritten.

## Resolution layers

For each governed source, P21.1 keeps four concepts separate:

1. **publisher identity** — who operates/publishes the source surface;
2. **stream origin state** — whether the governed stream itself supports a single source-level origin, is mixed, is derived from many origins, or remains unknown;
3. **syndication/copy/derivation relation** — whether the stream is original, copied/syndicated, derived or unresolved;
4. **independence credit state** — whether source-level origin grouping is supported or item-level provenance remains mandatory.

Schema:
`docs/contracts/p21_1_source_provenance_resolution.schema.json`

Evidence:
`docs/evidence/P21_1_SOURCE_PROVENANCE_RESOLUTION_2026-09-16.json`

## Source-level origin semantics

`EXPLICIT_SINGLE_ORIGIN` is permitted only where the governed stream is an official direct publication surface of one institutional origin at the source-network level and evidence supports that classification.

This establishes a source-network origin group only. It does **not** establish that:

- every factual claim in the publication is independently true;
- two institutional publishers independently corroborate the same real-world event;
- a claim may be marked verified without P13.5/P13.6 evidence;
- cited/quoted third-party information inherits the publisher's origin group.

`MIXED_ORIGIN` is used when one source surface can contain material from multiple departments, actors, reporters, citations, agencies or other upstream origins. No single `origin_group_id` is assigned.

`DERIVED_MULTI_ORIGIN` is used for discovery/index/aggregation systems whose content is explicitly constructed from many upstream sources. Such a stream receives no independent-origin credit itself.

`UNKNOWN_ORIGIN` remains available and must be used when neither single nor mixed/derived classification is supported.

## Resolution result for the current 10-source portfolio

```text
REVIEWED_SOURCES = 10
PUBLISHER_IDENTITY_EXPLICIT = 10
EXPLICIT_SINGLE_ORIGIN_STREAMS = 3
MIXED_ORIGIN_STREAMS = 6
DERIVED_MULTI_ORIGIN_STREAMS = 1
UNKNOWN_ORIGIN_STATE_STREAMS = 0
CONFIRMED_SOURCE_LEVEL_ORIGIN_GROUPS = 3
PRECISE_PORTFOLIO_INDEPENDENT_ORIGIN_COUNT = UNKNOWN
```

Confirmed source-level origin groups:

- `official:european-commission`;
- `official:european-parliament`;
- `official:osce`.

The remaining seven streams do not receive a single origin group. GDELT is explicitly `DERIVED_MULTI_ORIGIN / DERIVED / NO_INDEPENDENCE_CREDIT`; the other six require item-level provenance for any independence claim.

## Important lower-bound rule

The presence of three confirmed source-level origin groups does **not** mean `independent_origin_count = 3` for the entire portfolio or for arbitrary claims.

A precise portfolio-wide independent-origin count remains `UNKNOWN` because mixed-origin streams have unresolved upstream composition and source-level organizational separation is not a substitute for claim-level independent corroboration.

P21.3 may use confirmed origin groups only for the exact cells/sources to which they apply and must keep unknown/mixed components explicit.

## Plugin-first boundary

Future ChatGPT delivery is Plugin-first, but provenance is deployment-wrapper neutral.

```text
PLUGIN_ROUTE_CREATES_PROVENANCE = NO
PLUGIN_ROUTE_CREATES_INDEPENDENCE = NO
CONNECTOR_ROUTE_CREATES_INDEPENDENCE = NO
CUSTOM_MCP_ROUTE_CREATES_INDEPENDENCE = NO
```

A source accessed through an App, Connector, custom MCP server or any later Plugin skill retains the same publisher/origin/derivation semantics.

## Factual-verification boundary

P13.5/P13.6 remain the only canonical factual-verification authority.

Official-source classification proves the institutional publication/statement origin where applicable; it does not prove the underlying event asserted by the institution.

## Safety boundary

P21.1 is repository/evidence work only.

```text
LIVE_SOURCE_EXPANSION = NO
LIVE_INGEST_CHANGE = NO
RUNTIME_DEPLOYMENT = NO
SERVICE_RESTART = NO
PAID_PROVIDERS = NONE_APPROVED
SHARED_RUNTIME_ACTIVE = NO
MIGRATION_033 = NOT_CREATED / NOT_PREAUTHORIZED
PRODUCTION_LIVE = NOT_OPERATIONAL
PLUGIN_BUILD = NOT_STARTED
PLUGIN_PUBLICATION = NOT_ACTIVATED
```

## Gate criteria

P21.1 is valid only if:

- all 10 governed source paths are reviewed;
- publisher identity is evidence-backed or explicitly unknown;
- single/mixed/derived/unknown origin states are deterministic;
- no mixed/derived stream receives a single origin group;
- GDELT receives no independence credit;
- publisher/domain/language counts cannot produce independence;
- P20 historical evidence remains unchanged;
- P13 factual-verification authority remains unchanged;
- Plugin/App/Connector/MCP routing remains provenance-neutral;
- regression tests pass.

Current gate state:
`P21_1_GATE = VALIDATION_PENDING`
