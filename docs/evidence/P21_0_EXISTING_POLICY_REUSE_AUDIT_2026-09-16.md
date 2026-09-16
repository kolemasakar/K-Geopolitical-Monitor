# P21.0 — Existing Coverage Policy Reuse Audit

Date: 2026-09-16
Status: `AUDIT_COMPLETE / POLICY_PROPOSAL_REQUIRED`
Project: `K-Geopolitical Monitor`
Parent: `Phase 21 — Source Network Operational Adequacy & Evidence Population`

## Scope

Repository-only audit. No live source, ingestion, runtime, service, provider, storage, migration or deployment mutation was performed.

## Canonical inputs

- `docs/contracts/p20_2_coverage_matrix_policy.schema.json`
- `docs/evidence/P20_2_OBSERVED_COVERAGE_MATRIX_2026-09-16.json`
- `docs/evidence/P20_0_EXISTING_COVERAGE_BASELINE_2026-09-16.json`
- `docs/evidence/P20_1_SOURCE_TAXONOMY_RECONCILIATION_2026-09-16.json`
- `docs/implementation/P20_7_PHASE_20_ACCEPTANCE_RESULT.md`
- `docs/decisions/PHASE_21_SOURCE_NETWORK_OPERATIONAL_ADEQUACY_ROADMAP_DECISION_2026-09-16.md`

## Findings

### 1. P20.2 is reusable and must not be replaced

The existing target-policy contract already defines:

- `REQUIRED / OPTIONAL / NOT_REQUIRED / UNSET`;
- target cells by `geography_scope × language × source_type` with optional `topic_role`;
- `minimum_source_count`;
- `minimum_independent_origin_count`;
- `minimum_healthy_source_count`;
- `maximum_stale_share`;
- `maximum_dominant_origin_share`.

These semantics remain valid for P21.0.

### 2. P20.2 closure intentionally contains no approved target policy

The observed matrix contains 17 cells but its canonical policy state is `UNSET`.

Absence from the observed matrix is explicitly not equivalent to `NOT_REQUIRED`.

Therefore P21.0 must not mutate the historical P20.2 evidence or infer target policy from the existing ten-source portfolio.

### 3. P20.1 intentionally leaves coverage activation unresolved

`active_for_coverage` is not derived from source availability. P20.1 explicitly leaves it unresolved until coverage policy exists.

This remains correct. Governance/availability state cannot silently create policy authority.

### 4. P21.0 needs only a policy extension layer

The minimum missing policy concepts are:

- explicit policy authority/approval state;
- explicit criticality tier;
- explicit collection-latency target;
- explicit content-freshness target;
- effective/review dates;
- explicit rationale/provenance for each target cell;
- deterministic rule that unmentioned cells inherit an explicit default, with `UNSET` remaining fail-closed;
- explicit distinction between policy targets and observed current capability.

### 5. Global scope cannot be backfilled from observed cells

The present observed matrix contains cells for the current governed source universe only. It is not an exhaustive world-region or language inventory.

A Phase 21 target policy may introduce zero-observed required cells. Those cells are policy requirements and future gap candidates; they are not evidence that a source currently exists.

## Reuse decision

`REUSE_P20_2_POLICY_CONTRACT = YES`

`REPLACE_P20_2_ENGINE = NO`

`MUTATE_P20_HISTORICAL_EVIDENCE = NO`

`ADD_P21_0_POLICY_EXTENSION = YES`

## Remaining decision boundary

The contract can be implemented and tested without choosing geopolitical priorities.

The actual target manifest — which geographies, languages and source types are `REQUIRED`, at what criticality and thresholds — is a strategic policy decision and must be explicit, versioned and auditable. It must not be reconstructed from the current portfolio.

## Safety boundary

```text
LIVE_SOURCE_EXPANSION = NO
LIVE_INGEST_CHANGE = NO
RUNTIME_DEPLOYMENT = NO
SERVICE_RESTART = NO
PAID_PROVIDERS = NONE_APPROVED
SHARED_RUNTIME_ACTIVE = NO
MIGRATION_033 = NOT_CREATED / NOT_PREAUTHORIZED
PRODUCTION_LIVE = NOT_OPERATIONAL
```
