# Phase 11 Global Operational Coverage Delta Audit

Status: COMPLETE
Date: 2026-08-26
Project: K-Geopolitical Monitor
Roadmap phase: Phase 11 - Global Operational Coverage

## Purpose

Determine the exact implementation delta required for measurable global operational coverage without duplicating M6, M7, M8, M10 or M13 coverage-related capabilities and without treating coverage as factual verification confidence.

No new engineering milestone number is assigned by this audit.

## Approved Contract

The canonical COVERAGE_CONTRACT.md already defines these coverage dimensions:

- time_window;
- regions;
- countries;
- actors;
- storylines;
- event_categories;
- source_classes;
- languages;
- importance_threshold;
- freshness_requirement;
- verification_requirement;
- cross_check_requirement;
- forecast_requirement;
- report_depth.

It also requires:

- achieved coverage;
- coverage confidence;
- coverage gaps;
- unavailable sources;
- language/platform limitations.

The contract explicitly states that coverage is not measured by source count.

## Existing Coverage Capabilities

### M6 Controlled Pilot

Already provides:

- required source-class configuration for a pilot runner;
- observed source classes;
- missing source classes;
- run-linked PilotCoverageReport;
- deterministic source-class coverage_confidence;
- project-local persistence.

Current limitation:

- the M6 confidence value is only source-class completeness;
- it does not express live source availability, freshness, region/language scope, measurement observability or wider Coverage Contract dimensions;
- required source-class policy is runner configuration rather than one reusable durable coverage contract.

### M7 Live Public-Source Pilot

Already provides:

- source collection audit records;
- COMPLETED/PARTIAL/FAILED collection state;
- source success/failure counts;
- explicit failed source IDs and errors;
- collection timestamps;
- raw-item provenance.

Current limitation:

- source success/failure is collection health, not a complete coverage model;
- only two controlled-pilot live integrations are approved;
- a successful collection must not be interpreted as global coverage.

### M8 Live End-to-End Analysis

Already provides:

- original publisher/origin evidence independence;
- explicit DETECTED/PARTLY_VERIFIED semantics;
- same-origin deduplication;
- finding references to claims/raw items/origins.

Phase 11 constraint:

- origin count and verification status are evidence truth, not coverage metrics;
- coverage must never increase M8 confidence, independent-origin count or verification status.

### M10 Region and Language Coverage

Already provides:

- canonical region registry;
- canonical language registry;
- watch-scoped required region/language pairs;
- observation attribution;
- required/observed/missing scopes;
- deterministic coverage_ratio;
- restart-safe project-local persistence.

Current limitation:

- any attribution can make a region/language pair observed regardless of source availability or freshness;
- coverage_ratio does not incorporate source-class requirements, source failures, freshness or unmeasured Coverage Contract dimensions;
- region/language coverage remains one dimension-specific report, not an operational coverage envelope.

### M13 Full Reporting Environment

Already provides:

- typed COVERAGE_REPORT references;
- COVERAGE_METADATA presentation class;
- Regional/Country Brief validation against region/language coverage reports;
- explicit visibility of incomplete coverage.

Current limitation:

- reporting only presents selected coverage state;
- it does not own or calculate a canonical operational coverage assessment;
- report volume or report completeness cannot be used as coverage evidence.

## Gaps Requiring Phase 11 Work

### 1. No unified durable operational coverage contract

There is no single persisted contract that declares the exact monitoring scope to be measured across currently supported dimensions.

A Phase 11 contract must be explicit. The word `global` must never imply an undeclared world-complete scope.

### 2. No per-requirement measurement status

Existing coverage reports provide ratios and gaps, but not one typed status model that can distinguish:

- SATISFIED;
- GAP;
- UNAVAILABLE;
- STALE;
- UNKNOWN;
- UNMEASURED.

This distinction is required so absence, failed acquisition, stale acquisition and unsupported measurement are not collapsed into one number.

### 3. Coverage confidence is not yet a cross-dimension measurement-confidence concept

M6 source-class confidence and M10 coverage_ratio are dimension-specific completeness measures.

Phase 11 needs a separately named and defined coverage assessment confidence that means confidence in the coverage measurement itself, not confidence that a geopolitical claim is true.

### 4. Freshness is not part of a unified coverage decision

M7 collection timestamps and M10 attribution timestamps exist, but no canonical evaluator determines whether a requirement is current, stale or unknown against an explicit freshness threshold.

### 5. Source availability is not connected to scope completeness

M7 persists collection failure information, but M10 region/language completeness does not automatically expose whether required source acquisition was unavailable in the relevant assessment window.

### 6. Some approved Coverage Contract dimensions are not currently measurable from canonical domain state

There is no canonical durable actor-coverage registry or canonical storyline truth table. M13 intentionally avoided creating storyline truth.

Country versus broader region semantics are also not separately typed in the current region catalog.

Phase 11 must not fabricate these missing canonical domains. Unsupported declared dimensions must remain explicit UNMEASURED limitations until a separate domain model is approved.

### 7. No durable composite coverage snapshot/history/query surface

There is no canonical object that records one reproducible coverage assessment with:

- exact contract version/scope;
- assessment window;
- per-requirement results;
- completeness;
- coverage confidence;
- gaps/unavailable/stale/unknown/unmeasured limitations;
- upstream evidence references;
- historical snapshots.

### 8. Live adapter source-identity hardening is relevant to coverage integrity

LiveSourceCollector validates adapter source_id uniqueness but does not explicitly verify that each returned LiveSourceItem source_id/source_name/source_class matches the adapter declaration.

This was previously identified as a future hardening item. Phase 11 coverage measurement depends on trustworthy source identity, so this should be closed before live source availability is used as coverage evidence.

## Convergence Decision

Phase 11 must extend existing M6/M7/M10 coverage state rather than replace it.

Canonical direction:

- M6 source-class reports remain valid historical baseline data;
- M7 source collection audits remain the source-availability truth;
- M8 remains the evidence-verification truth;
- M10 remains the region/language scope and attribution truth;
- M13 remains the report/presentation layer;
- Phase 11 adds one durable operational coverage contract and assessment layer that references these existing stores.

## Coverage Metric Semantics

Phase 11 should separate at least two concepts:

1. `coverage_ratio`
   - fraction of explicitly required coverage units currently SATISFIED;
   - measures achieved coverage, not factual truth.

2. `coverage_confidence`
   - fraction of explicitly required coverage units for which the system has a known, reproducible assessment state;
   - SATISFIED, GAP, UNAVAILABLE and STALE are known states;
   - UNKNOWN and UNMEASURED reduce assessment confidence;
   - a system may therefore have high confidence that coverage is poor.

Neither value may modify evidence confidence or forecast probability.

## Global Claim Boundary

A `GLOBAL` scope label is only a user-defined coverage contract scope key.

It does not mean:

- every country is covered;
- every language is covered;
- every relevant event was detected;
- every source was available;
- production/global operations are approved.

All required units and all limitations must remain explicit.

## Storage and Integration Boundary

- PROJECT_LOCAL_ONLY remains mandatory;
- no shared runtime database;
- no external coverage provider required;
- no automatic translation provider approved;
- no production/global source expansion is implied by this phase;
- production/live status remains NOT_OPERATIONAL.

## Audit Result

`PHASE_11_GLOBAL_OPERATIONAL_COVERAGE_DELTA_AUDIT = PASS`

The required implementation is a convergence/measurement layer over existing coverage and collection truth, not a replacement coverage engine and not a new verification engine.
