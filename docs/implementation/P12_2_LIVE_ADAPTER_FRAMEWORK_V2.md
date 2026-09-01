# P12.2 — Live Adapter Framework v2

State: `VALIDATED`
Gate: `P12_2_ADAPTER_FRAMEWORK_V2_VALIDATED`
Parent gate: `P12_1_SOURCE_PORTFOLIO_CONTRACT_VALIDATED`

## Objective

Provide a reusable, deterministic and fail-closed public-source adapter framework without creating a parallel canonical ingestion path or activating new external sources.

## Implementation

Canonical implementation:
`src/kgeopolitical_monitor/adapter_framework.py`.

The framework is an additive governed facade over the validated M7 `LiveSourceCollector` and provides:

- bounded read-only HTTPS GET transport;
- rejection of non-HTTPS request URLs;
- rejection of URL-embedded credentials and credential-bearing headers for the public-anonymous framework;
- bounded response size and timeout configuration;
- deterministic RSS and Atom parsing;
- bounded JSON list parsing;
- reusable `PublicFeedAdapterV2` and `PublicJsonListAdapterV2` contracts;
- deterministic `adapter_id`, `adapter_version`, `source_id` and stable item identity;
- concrete v2 adapter definitions for the already-known Consilium and GDELT source shapes;
- P12.1 portfolio governance enforcement before collection and again at each collection;
- exact portfolio adapter-version and outbound-host matching;
- compatibility with existing source-attempt audit, ingestion/provenance and `ReproducibilityInstrumentedCollector`;
- source failure isolation through the validated underlying collector.

## Governance / Fail-Closed Rules

A P12.2 framework adapter cannot collect unless its current P12.1 portfolio record:

- exists;
- is `APPROVED`;
- has `ACTIVE` or `DEGRADED` operational availability;
- matches canonical source name/class;
- is `PUBLIC_ANONYMOUS` with authentication `NONE`;
- is classified `PUBLIC`;
- matches the exact declared `adapter_id` and `adapter_version`;
- permits HTTPS;
- explicitly contains the adapter request hostname in `outbound_domains`;
- if paid, already carries separate paid-provider approval.

P12.2 itself approves or activates no paid provider.

## Deterministic Fixtures

CI-local fixtures:

- `tests/fixtures/p12_2/feed.rss.xml`;
- `tests/fixtures/p12_2/feed.atom.xml`;
- `tests/fixtures/p12_2/gdelt.json`.

Tests do not depend on live network availability.

## Reproducibility Boundary

The framework collector is compatible with the existing E6 reproducibility wrapper. Source attempts link to:

- exact watch query snapshot;
- source ID;
- adapter implementation identity;
- declared adapter version;
- collection attempt status;
- persisted artifact hashes/provenance.

The existing E6 schema still marks remote request locator as `NOT_INSTRUMENTED`. P12.2 does not reconstruct or relabel that field as exact merely because an adapter can deterministically construct a URL.

## Epistemic Boundaries

The framework does not:

- establish underlying origin;
- count independent corroboration;
- promote claim verification;
- alter source reputation truth semantics;
- increase coverage confidence merely because an adapter exists;
- imply exhaustive global coverage;
- imply production/live activation.

Portfolio approval and adapter availability remain governance/collection state, not factual evidence.

## Runtime / Activation State

- existing M7 collector remains available for backward-compatible validated paths;
- P12.2 framework is additive and governed;
- no new external source is seeded or activated by P12.2;
- Consilium/GDELT v2 classes describe reusable adapter shapes but do not automatically switch runtime configuration;
- runtime storage remains `PROJECT_LOCAL_ONLY`;
- production/live operational status remains `NOT_OPERATIONAL`.

## Validation Evidence

Implementation commit:
`f2635cc5724b24ed7f3b880c50a67a4ca0f849fa`.

Initial implementation CI:
- run `33523359982`;
- job `99907884699`;
- `345 passed, 1 failed, 1 warning`;
- sole failure was a deterministic fixture ordering assertion caused by stable item-ID sorting; production framework code was not changed to resolve it.

Validation commit:
`cb6866e82d5dc4a26042e0b9d08e9098aae10ecb`.

Final validation:
- CI run `33523574819`;
- job `99908604206`;
- `346 passed, 1 warning / SUCCESS`.

Validated tests cover request/credential/HTTPS fail-closed behavior, resource bounds, RSS/Atom/JSON deterministic parsing, stable identities, P12.1 governance enforcement, adapter/domain drift rejection, failure isolation, persisted collection audit/provenance compatibility and reproducibility linkage without fabricated exact request history.

## Gate Result

`P12_2_ADAPTER_FRAMEWORK_V2_VALIDATED`

Next engineering activity:
`P12.3_PRIORITY_AUTHORITATIVE_SOURCE_PACK / NEXT_NOT_STARTED`.
