# M13 Full Reporting Environment Implementation Plan

Status: ACTIVE
Date: 2026-08-26
Project: K-Geopolitical Monitor
Roadmap phase: Phase 10 - Full Reporting Environment

## Goal

Build one durable, reproducible, project-local reporting environment that assembles already validated findings, alerts, coverage, graph intelligence and forecasts without creating new truth stores or changing upstream confidence/verification semantics.

## Architecture Rule

M13 introduces the first canonical report assembly layer.

It must converge existing output/query surfaces into one common report contract rather than create report-type-specific engines.

A report is an immutable analytical presentation snapshot, not a fact or verification authority.

Runtime storage remains PROJECT_LOCAL_ONLY.

## Approved Report Types

- STRATEGIC_ALERT
- GLOBAL_GEOPOLITICAL_BRIEF
- REGIONAL_COUNTRY_BRIEF
- STORYLINE_REPORT
- EVENT_DOSSIER
- FORECAST_REPORT
- STRATEGIC_OUTLOOK

## Presentation Classes

Every substantive report section must explicitly declare one of:

- OBSERVED_FACT
- VERIFICATION_STATE
- ANALYTICAL_CONTEXT
- GRAPH_INFERENCE
- FORECAST_SCENARIO
- ANALYST_ASSUMPTION
- COVERAGE_METADATA

Presentation class is descriptive metadata only. It cannot change upstream truth state.

## Mandatory Boundaries

- No shared or mixed runtime database.
- No external publishing/delivery provider is required by the baseline.
- Report ranking/order does not modify importance, confidence or verification.
- Graph inference remains graph inference and is never source evidence.
- Forecast probability and scenario confidence remain separate from evidence confidence.
- Report assembly must not increase independent-origin count.
- Report assembly must not create VERIFIED claims.
- Report assembly must not mutate M11 graph state.
- Report assembly must not mutate M12 forecast versions, outcomes or calibration history.
- Report assembly must not silently create canonical storylines.
- Prior report snapshots remain immutable.

## Canonical Durable Model

### Report Snapshot

Required fields:

- report_id;
- report_type;
- scope_key;
- subject_ref_type;
- subject_ref_id;
- title;
- summary;
- as_of;
- created_at;
- generator_version.

Report identity is deterministic from report type, scope key, subject reference and normalized as-of timestamp.

### Report Section

Required fields:

- section_id;
- report_id;
- section_order;
- section_type;
- heading;
- presentation_class;
- content_json;
- explanation;
- created_at.

Sections are immutable after a report snapshot is persisted.

### Report Reference

Required fields:

- reference_id;
- report_id;
- section_id optional;
- reference_kind;
- reference_value;
- reference_role;
- created_at.

Reference kinds baseline:

- SOURCE;
- RAW_ITEM;
- CLAIM;
- EVENT;
- FINDING;
- ALERT;
- GRAPH_NODE;
- GRAPH_EDGE;
- FORECAST;
- FORECAST_VERSION;
- SCENARIO_VERSION;
- REGION;
- LANGUAGE;
- COVERAGE_REPORT;
- ANALYST_ASSUMPTION.

Durable project references fail closed where a canonical durable object is required.

## M13.1 Canonical Report Contract and Durable Snapshots

Implement:

- migration `015_full_reporting_environment.sql`;
- common report type/presentation/reference contracts;
- deterministic report/section/reference identity;
- immutable report snapshot persistence;
- fail-closed subject/reference validation;
- restart persistence and repeated-save idempotence;
- no report-type-specific truth stores.

Gate:
`M13_1_REPORT_CONTRACT_VALIDATED`

## M13.2 Common Report Assembly and Provenance

Implement:

- one `ReportAssembler` interface;
- finding, alert, coverage, graph and forecast adapters into common report sections;
- required short summary;
- ordered critical-events/changes/context/impact/forecast/confidence/sources sections when applicable;
- typed provenance/reference accumulation;
- deterministic ordering;
- explicit distinction between source evidence, graph inference and forecast scenarios.

Gate:
`M13_2_REPORT_ASSEMBLY_VALIDATED`

## M13.3 Strategic, Global and Regional Briefs

Implement:

- Strategic Alert report from durable alert/finding/evidence state;
- Global Geopolitical Brief from explicit selected persisted findings/alerts/forecasts;
- Regional/Country Brief using canonical region/language scope and explicit selected inputs;
- coverage metadata section for regional reports;
- no automatic global-completeness claim when coverage is incomplete.

Gate:
`M13_3_BRIEFS_VALIDATED`

## M13.4 Event Dossier and Storyline Report

Implement:

- Event Dossier anchored to a valid canonical event ID;
- explicit optional links to persisted findings, claims, graph nodes/edges and source evidence;
- timeline/context sections derived only from explicit persisted references;
- Storyline Report as an explicit report-scoped collection of canonical references;
- no hidden canonical storyline entity created by reporting;
- contradiction/context/relationship sections preserve their analytical labels.

Gate:
`M13_4_DOSSIER_STORYLINE_VALIDATED`

## M13.5 Forecast Report and Strategic Outlook

Implement:

- Forecast Report anchored to a valid forecast ID/version;
- scenario probability/confidence display with typed provenance;
- outcome/evaluation/calibration history when available;
- Strategic Outlook as explicit composition of selected validated forecasts plus findings/graph context;
- explicit uncertainty and invalidation-signal sections;
- no forecast-to-fact promotion.

Gate:
`M13_5_FORECAST_REPORTS_VALIDATED`

## M13.6 Rendering, Reproducibility and Isolation Gate

Implement/validate:

- deterministic structured representation from persisted snapshot;
- deterministic plain-text/Markdown rendering from the same snapshot;
- identical snapshot renders identically after restart;
- all approved report types use the same durable contract;
- report references remain traceable to upstream project-local objects;
- M8 verification confidence/origin count unchanged;
- M11 graph state unchanged;
- M12 forecast versions/probabilities/calibration unchanged;
- region/language metadata does not create source independence;
- runtime database remains project-local;
- no external publishing/delivery service required;
- full deterministic repository regression CI passes.

Gate:
`M13_FULL_REPORTING_ENVIRONMENT_BASELINE_PASS`

## Initial Implementation Order

1. Add migration 015 and durable common report contracts.
2. Add report repository with deterministic immutable identities.
3. Add common assembler and typed provenance adapters.
4. Add Strategic Alert, Global and Regional Brief assembly.
5. Add Event Dossier and report-scoped Storyline assembly.
6. Add Forecast Report and Strategic Outlook assembly.
7. Add deterministic structured/Markdown rendering.
8. Add cross-layer isolation regressions.
9. Run full CI and record completion/validation artifacts.

## Completion Boundary

M13 is complete only when all M13 gates pass and the full deterministic regression suite succeeds on final reconciled main.

M13 completion may validate ROADMAP Phase 10 Full Reporting Environment engineering baseline. It does not approve external publishing/delivery, global operational coverage, shared runtime storage, production dashboards or production/live OPERATIONAL status.
