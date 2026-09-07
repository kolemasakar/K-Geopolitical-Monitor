# P18.3 — Shared Datastore Schema and Migration Contract

Status: `IMPLEMENTED / PENDING_EXACT_VALIDATION`
Date: 2026-09-07
Project: K-Geopolitical Monitor
Target gate: `P18_3_SHARED_DATASTORE_SCHEMA_MIGRATION_CONTRACT_VALIDATED`

## Purpose

P18.3 introduces a provider-neutral, in-memory relational schema and migration contract for a future shared/team runtime. It does not create or connect a shared datastore, execute DDL, allocate a repository migration number, activate shared runtime, or authorize canonical cutover.

## Implemented Contract

`src/kgeopolitical_monitor/shared_datastore_schema.py` defines:

- a PostgreSQL-compatible relational capability contract without selecting a provider;
- mandatory `workspace_id` + `project_id` tenant keys for every modeled shared canonical table;
- composite tenant-scoped primary-key rules;
- composite tenant-preserving foreign-key rules that prevent an object reference from dropping workspace/project scope;
- fail-closed database-policy/RLS-equivalent scope descriptors using both tenant-key columns;
- representative shared canonical object families for event, semantic claim, forecast, delivery intent and publication release state;
- explicit transactional-semantics requirement;
- a logical migration contract with version advance, forward operations, rollback operations and explicit mixed-version compatibility rules;
- a hard P18.3 boundary that rejects any allocated repository migration number, destructive migration, or canonical-cutover authorization;
- controlled owner-local SQLite export provenance contracts with source database SHA-256, per-table row counts and checksums;
- import reconciliation that can only produce `ready_for_shadow_validation=True` and always keeps `canonical_cutover_authorized=False`.

## Tenant Isolation Rule

Every shared canonical table represented by this contract must contain non-null:

- `workspace_id`;
- `project_id`.

Both values must lead the table primary key. Every inter-object foreign key must carry both tenant columns on the local and referenced sides. A foreign key that references only an object identifier is invalid even if that identifier happens to be globally unique in a test fixture.

This moves tenancy enforcement below UI/request filtering and into the relational contract itself.

## Database Policy Rule

Every shared canonical table requires a fail-closed database-policy scope equivalent to:

`(workspace_id, project_id)`

The P18.3 contract does not install concrete PostgreSQL RLS SQL. Provider/database-specific DDL remains outside this step until a separately reviewed migration/provider implementation exists.

## Migration Rule

P18.3 validates a logical schema transition contract only.

Required before a future migration can be validated:

- strictly advancing schema version;
- non-empty forward operation set;
- non-empty rollback operation set;
- explicit compatibility policy;
- non-destructive behavior within this P18.3 contract;
- no implicit canonical cutover.

Repository migration number state remains:

`MIGRATION_033 = NOT_CREATED / NOT_PREAUTHORIZED`

No other Phase 18 migration number is allocated or reserved by this implementation.

## Export / Import Rule

A future controlled export may originate only from the validated owner-local project SQLite storage scope and must carry:

- explicit `TenantContext`;
- source schema version;
- source database SHA-256;
- per-table row counts;
- per-table SHA-256 reconciliation checksums.

Import reconciliation fails on row-count or checksum mismatch. A successful reconciliation is evidence for later shadow validation only; it does not authorize shared canonical cutover.

## Explicit Non-Actions

This P18.3 implementation does **not**:

- create `migrations/033_*.sql`;
- reserve migration `033` or another Phase 18 migration number;
- create PostgreSQL or another database instance;
- select a managed database/provider;
- add provider credentials or secrets;
- expose database/public/shared ingress;
- change owner-local SQLite data;
- activate `SHARED_TEAM` as the canonical runtime;
- set `PHASE_18_SHARED_RUNTIME_ACTIVE = YES`;
- approve canonical cutover;
- change `PRODUCTION_LIVE = NOT_OPERATIONAL`;
- change `PAID_PROVIDERS = NONE_APPROVED`.

## Validation Plan

Implementation validation requires:

1. dedicated P18.3 negative/positive contract tests;
2. full repository x64 regression;
3. native ARM64 full regression;
4. ARM64 bootstrap/unattended/systemd guards;
5. exact-head evidence before formal P18.3 closure.

Until those checks are complete, canonical state remains `PHASE_18_P18_2_VALIDATED_P18_3_READY_GATE`.
