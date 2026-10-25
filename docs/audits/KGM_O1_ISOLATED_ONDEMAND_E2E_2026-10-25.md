# KGM O1 — On-demand isolated end-to-end qualification (2026-10-25)

Mode: **ON_DEMAND_ONLY** (explicit owner decision). No continuous scheduled source collection; 2 disabled production watches are expected configuration.

## Code-path audit

Deployed disk source at `b31b2136b5fe982d0b63b0135479b1549041906c`:
- `unattended_runner --once`: one supervisor tick, **not** an explicit user research request.
- `LiveOperationalCycle.execute_due()`: schedules work for enabled persisted watches via `due_watches()`; no independent user-facing request dispatcher has yet been attested.
- `LiveSourceCollector.collect()` persists source attempt outcomes and raw-item provenance; adapters may partially fail, with status PARTIAL when at least one succeeds.
- `LiveEndToEndProcessor.process_collection()` groups claims by normalized title, records independent origin evidence and persists findings.

## Isolated acceptance tests

`tests/test_o1_ondemand_offline_e2e.py` invokes the existing pipeline in a **disposable, network-free temp project** with synthetic adapters and a synthetic enabled watch solely inside a temporary SQLite. This is a fixture to exercise underlying collection/analysis logic, not a production enabling procedure.

Covered scenarios:
1. Explicit test invocation processes two synthetic independent sources, persists one source collection, two attempts, evidence and analysis; a repeated same-time call yields no scheduled repeat.
2. One synthetic adapter raises an error: source collection PARTIAL, a single evidence origin retained; missing source not silently counted as verified.
3. Both synthetic adapters fail: monitoring run FAILED; no analysis or provenance is fabricated.

Test result remains pending CI until GitHub explicitly reports success. These fixture tests are **not** a real user API, authenticated/plugin on-demand entrypoint, network fetch, freshness measurement, or loaded-code attestation.

## Architecture and gates

The project should add/verify an explicit request dispatcher separate from persistent watch scheduling:
- Accept a bounded user request (topic, dates, sources, freshness cut-off).
- Validate source allowlists, input size, provenance and no unsolicited delivery.
- Execute one bounded acquisition-analysis cycle through approved adapters and produce an auditable response.
- Preserve disabled production watches and NO_SEND.
- Require owner approval before any real live operational query or production deployment.

Final real-world on-demand acceptance is OPEN. Production NO_GO. FREE_ONLY / NO_SEND / CLEANUP_HOLD.
