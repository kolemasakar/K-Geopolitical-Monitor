# Phase 21 — Source Network Operational Adequacy & Evidence Population — Roadmap Decision

Date: 2026-09-16
Status: `APPROVED / NOT_STARTED`
Project: `K-Geopolitical Monitor`
Parent strategic position: `PHASE_20_GLOBAL_SOURCE_COVERAGE_VALIDATED / PASS_WITH_KNOWN_LIMITATIONS`
Authorization basis: owner approval after strategic audit of Phases 12–20.

## Decision

Approve the next strategic development block as:

`Phase 21 — Source Network Operational Adequacy & Evidence Population`

Phase 21 exists to convert the validated Phase 20 coverage framework into measured operational evidence and policy-bounded source-network adequacy.

It does not replace or weaken Phase 13 factual verification. P13.5/P13.6 remain the sole canonical factual-verification authority.

## Strategic objective

Advance the primary project chain:

`COLLECT -> VERIFY -> SUMMARIZE -> ANALYZE -> FORECAST`

by addressing the current first-order constraint at the collection/evidence layer:

- target coverage policy is currently `UNSET`;
- source-level underlying-origin evidence is unresolved for the governed portfolio;
- current fresh health evidence is not represented in the canonical P20 closure report;
- coverage adequacy therefore remains `UNKNOWN` rather than measurably adequate or gapped.

## Phase 21 sequence

### P21.0 — Coverage Policy Definition & Criticality Contract

Goal: define explicit policy for required/optional/not-required coverage by geography, language and source type, including criticality and freshness expectations.

Proposed gate:
`P21_0_COVERAGE_POLICY_CRITICALITY_CONTRACT_VALIDATED`

### P21.1 — Existing Portfolio Provenance Resolution

Goal: resolve source-level underlying-origin, syndication/copy relations and origin groups where evidence supports them; preserve unresolved cases as `UNKNOWN`.

Proposed gate:
`P21_1_SOURCE_PROVENANCE_RESOLUTION_VALIDATED`

### P21.2 — Fresh Operational Health Baseline

Goal: collect and preserve fresh operational evidence for the existing governed portfolio without expanding the live source set.

Required dimensions include reachability, parser/adapter health, collection latency, content latency, recovery state and measurement timestamp.

Proposed gate:
`P21_2_FRESH_SOURCE_HEALTH_BASELINE_VALIDATED`

### P21.3 — Coverage Adequacy Baseline v1

Goal: combine policy, provenance and fresh health into a deterministic explainable coverage evaluation.

Expected states may include:
`ADEQUATE`, `THIN`, `MONOCULTURE_RISK`, `DEGRADED_COLLECTION`, `MISSING_EXPECTED_COVERAGE`, `NOT_REQUIRED_BY_POLICY`, `UNKNOWN`.

Proposed gate:
`P21_3_OPERATIONAL_COVERAGE_ADEQUACY_BASELINE_VALIDATED`

### P21.4 — Gap-Driven Source Expansion Plan

Goal: derive source additions from measured gaps rather than raw source-count targets.

This gate prepares explicit onboarding candidates and does not itself authorize live activation.

Proposed gate:
`P21_4_GAP_DRIVEN_SOURCE_EXPANSION_PLAN_VALIDATED`

### P21.5 — Controlled Public/Free Source Onboarding

Goal: onboard only approved public/free sources required by measured gaps, using the validated P20.5 onboarding contract and explicit rollback/disable semantics.

Entry requires a separate owner-approved activation decision for live source expansion.

Proposed gate:
`P21_5_CONTROLLED_SOURCE_ONBOARDING_VALIDATED`

### P21.6 — Intelligence Quality Impact Validation

Goal: measure how the improved evidence universe affects verification yield, provenance completeness, contradiction handling, analytical coverage and forecast cohort quality without allowing coverage metrics to promote factual truth.

Proposed gate:
`P21_6_INTELLIGENCE_QUALITY_IMPACT_VALIDATED`

### P21.7 — Phase 21 Acceptance

Final gate:
`PHASE_21_SOURCE_NETWORK_OPERATIONAL_ADEQUACY_VALIDATED`

## Explicit non-authorization

This roadmap decision does not authorize or perform:

- runtime deployment or service restart;
- live-source expansion before the explicit P21.5 activation decision;
- paid-provider selection or spending;
- shared-runtime activation;
- public/shared ingress;
- migration `033`;
- canonical storage cutover;
- production/live activation;
- Phase 17 external publication;
- Phase 18 shared runtime activation.

## Permanent boundaries

Preserve:

`SOURCE_COUNT != INDEPENDENT_ORIGIN_COUNT`

`COVERAGE_CONFIDENCE != FACTUAL_VERIFICATION_CONFIDENCE`

`COLLECTION_HEALTH != CONTENT_CREDIBILITY`

`GLOBAL_SCOPE != EXHAUSTIVE_GLOBAL_COVERAGE`

`FORECAST_CONFIDENCE != FACTUAL_VERIFICATION_CONFIDENCE`

Unknown evidence remains unknown; missing operational evidence must not be reconstructed or inferred from governance/configuration state.

## Deferred work

The following remain deferred unless separately authorized:

- owner operational activation from Phase 14;
- external publication from Phase 17;
- shared/team runtime activation from Phase 18;
- paid or secret-bearing source providers;
- private GPT Action/backend HTTPS/public dashboard exposure;
- migration `033`.

## Entry state

`PHASE_21_STATE = APPROVED / NOT_STARTED`

`NEXT_GATE = P21_0_COVERAGE_POLICY_CRITICALITY_CONTRACT_VALIDATED`
