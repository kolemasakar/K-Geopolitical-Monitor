# E6 Reproducibility Instrumentation

Status: BASELINE_VALIDATED
Project: K-Geopolitical Monitor
Workstream: Approved unnumbered post-pilot expansion E6
Validation date: 2026-08-29

## Objective

Add durable, machine-captured reproducibility metadata to the existing project-local monitoring pipeline without creating a parallel truth store and without reconstructing evidence that was not actually captured.

## Validated implementation

### Migration 020

`migrations/020_reproducibility_instrumentation.sql` adds four additive project-local tables:

- `research_audit_runs`;
- `research_query_executions`;
- `research_artifact_hashes`;
- `research_provenance_annotations`.

The schema keeps reproducibility state separate from substantive verification state.

### Research audit envelope

For an instrumented live collection the runtime persists:

- research run identity;
- watch identity;
- exact watch query snapshot;
- timezone-aware research cut-off;
- instrumentation version;
- canonical source collection identity;
- audit status;
- source collection status;
- start/completion timestamps;
- explicit audit error only when instrumentation itself fails.

A failed source collection does not automatically mean that reproducibility capture failed. `audit status` and `collection status` are persisted independently.

### Query execution capture

For every canonical source collection attempt the audit projection records:

- source identity;
- adapter class identity;
- declared adapter version when available, otherwise a code SHA-256 fingerprint when inspectable;
- exact query snapshot;
- capture timestamp;
- canonical attempt status/item count/error through the existing `source_collection_attempts` relation.

The implementation does not fabricate browser/search history. When a concrete request locator was not instrumented, the state is explicitly `NOT_INSTRUMENTED` and the locator remains null.

### Persisted artifact hashing

For every persisted live item belonging to the audited collection the implementation computes SHA-256 over a deterministic canonical representation of the persisted parsed artifact, including the existing source identity, title, content, collected timestamp, original URL and metadata JSON.

Hash basis:

`KGM_PERSISTED_LIVE_ITEM_V1`

This is a hash of the persisted project artifact, not a claim that raw remote HTTP bytes were retained when they were not.

Repeated identical persisted artifacts produce the same content hash.

### Provenance classification boundary

The E6 audit store does not infer origin/syndication/repost/translation/citation/duplicate relationships from URL count, domain count or publication count.

Supported explicit annotation classes are:

- `PRIMARY_ORIGIN`;
- `SYNDICATION`;
- `REPOST`;
- `TRANSLATION`;
- `CITATION`;
- `DUPLICATE`;
- `DISCOVERY_INDEX`.

Origin/relation fields remain null until an explicit classification with a factual classification basis is persisted.

A provenance annotation is only accepted for a raw item that belongs to the audited canonical collection.

### Verification isolation

Reproducibility annotations do not change:

- claim verification status;
- independent-origin count;
- existing origin list;
- confidence semantics.

Reproducibility metadata is audit context, not independent evidence.

### Canonical runtime integration

`build_unattended_service()` now wraps the existing `LiveSourceCollector` with `ReproducibilityInstrumentedCollector`.

The underlying canonical collection, provenance, analysis, findings, alerts, coverage and project-local SQLite state remain unchanged in ownership.

No parallel collection store and no shared runtime database were introduced.

### Fail-closed behavior

Instrumentation finalization fails closed when the persisted source-attempt set does not match the instrumented adapter set.

On audit-finalization failure:

- the research audit becomes `FAILED`;
- the canonical collection status remains separately visible;
- partial query/hash audit artifacts are not accepted as a completed reproducibility bundle;
- the operational caller receives an explicit reproducibility finalization error.

An uninstrumented base collector does not fabricate a research audit record retroactively.

## Validation

Validated engineering SHA:

`af4444098ff4e1541ddaa2323c0fed723eeb3d65`

### x64 CI

- workflow run: `33264133429`;
- job: `99131026905`;
- result: SUCCESS;
- regression: `290 passed, 1 warning in 27.77s`.

### Native ARM64 CI

- workflow run: `33264133407`;
- job: `99131026851`;
- native architecture confirmation: `aarch64`;
- result: SUCCESS;
- regression: `290 passed, 1 warning in 29.53s`;
- bootstrap shell validation: PASS;
- unattended one-tick smoke: PASS;
- systemd unit contract: PASS.

The remaining warning is the existing Starlette/TestClient deprecation warning and is nonblocking for the E6 baseline.

## Truth-boundary invariants preserved

- publisher is not automatically underlying origin;
- duplicate URLs/domains do not create independent corroboration;
- provenance classification does not alter verification state;
- missing request history is `NOT_INSTRUMENTED`, not reconstructed;
- absence of a provenance annotation is not converted into an inferred classification;
- coverage confidence does not strengthen verification confidence;
- graph inference does not become source evidence;
- forecast probability does not become factual confidence;
- runtime storage remains `PROJECT_LOCAL_ONLY`.

## Non-claims

E6 does not claim:

- complete reproduction of external web state;
- preservation of every raw remote response byte;
- automatic underlying-origin discovery;
- universal source independence detection;
- production/global operational coverage;
- shared production runtime;
- public GPT approval.

## Gate

`E6_REPRODUCIBILITY_INSTRUMENTATION = BASELINE_VALIDATED`

Next approved workstream:

`E7 Forecast Probability Semantics`

E7 is not started by this document.