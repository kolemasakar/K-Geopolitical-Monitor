# KGM legacy research entry points — owner-only audit and migration gate

Date: 2026-09-29. Scope: KGM PR #163 offline synthetic research modules only. Last verified exact code SHA `e013925f15da84a73b0aede07620b1aa2291520c`: 137/137 selected tests. No live provider, production or K-Trader activity.

## Inventory and observed incompatibilities

- `research_spool_v1.submit/process_fixture/retrieve`: older minimal synthetic fixture. `submit` writes a request with only request_digest/request/status, not canonical durable `updated_at_utc` or `attempts`; `process_fixture` constructs a minimal synthetic result without the canonical typed-completion lifecycle. **Do not mix its request files with canonical durable workflow in one spool**: the canonical snapshot/admission paths expect durable request records and may encounter incompatible files.
- `research_lifecycle_v1.SyntheticResearchJob`: in-memory fixture only; not durable canonical state.
- `research_typed_spool_v1.publish_typed_fixture`: publishes a typed artifact but does not itself advance canonical durable terminal state; only for explicitly modeled crash/reconciliation tests or standalone fixture acceptance.
- `research_offline_acceptance_v1.run_fixture`: standalone synthetic compatibility matrix; admits, advances to ACCEPTED, publishes fixture and retrieves artifact but does not advance PROCESSING/terminal. Not an end-to-end canonical workflow.
- `research_durable_lifecycle_v1.advance`: low-level fixture transition currently permits COMPLETE/PARTIAL without requiring an immutable typed artifact. Existing compatibility test `test_restart_recovery_and_terminal` intentionally uses this old behavior. Canonical `research_typed_workflow_v1.publish_and_complete` instead routes through `research_completion_v1.complete_or_reconcile`, which validates artifact integrity, request correlation and typed terminal status.
- `research_deadline_registry_v1.register_deadline`: separate sidecar retained for old callers. Canonical `accept_request(..., deadline_utc=...)` embeds immutable deadline in one atomic admission record.
- `research_recovery_pass_v1`: rotates caller-managed cursor; `research_durable_cursor_v1.recover_durable` persists cursor under an owner-only cooperative run lock. Both still scan all request records through `recovery_snapshot`.

## Migration gates

1. Treat `research_typed_workflow_v1` plus `research_durable_cursor_v1.recover_durable` as supported owner-only synthetic entry points. Dedicated private spool must not contain minimal legacy records.
2. Add explicit fail-closed record-schema checks and tests that detect mixed legacy/canonical request files, without deleting or silently migrating user data.
3. Gate low-level terminal `advance` for canonical callers while preserving legacy fixture compatibility in explicitly isolated tests; migrate old fixture acceptance to canonical lifecycle only in a separately reviewed change.
4. Before replacing O(total inbox) recovery scanning, benchmark synthetic scale and design a durable indexed manifest with crash reconciliation; avoid claiming `max_items` bounds disk scanning. Maintain exact-SHA isolated test checkpoints.

No hostile-local-human-user certification required under current owner-only threat model. This document records audit findings and intended gates, not implementation or performance claims.
