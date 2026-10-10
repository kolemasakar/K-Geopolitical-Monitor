# KGM independent research readiness audit — 2026-10-07

Status: NOT READY FOR GATE

Exact validated SHA before this audit: `cd1b787991b31b704257952e0a8a78bd8adb3dbd`.
Local isolated regression: 149/149 PASS. GitHub CI run 2383: SUCCESS.

## Proven

- durable bounded admission and per-consumer namespace;
- fail-closed request and embedded deadline integrity;
- typed immutable COMPLETE/PARTIAL completion gate;
- restart reconciliation after artifact publication;
- bounded recovery plus durable cursor failure handling;
- 10,000 pending canonical recovery scan median about 0.616 s on owner pilot;
- minimal legacy durable records fail closed.

## Legacy isolation finding

The supported API is `research_typed_workflow_v1`, but legacy/fixture modules remain runtime dependencies of canonical modules for shared filesystem primitives and transition constants. In particular, canonical lifecycle/completion/deadline/expiry/cursor code imports helpers from `research_spool_v1`, and canonical lifecycle imports `TRANSITIONS` from `research_lifecycle_v1`.

This is not evidence of state mixing: regression coverage rejects legacy minimal records. It is nevertheless an architectural coupling, so the legacy modules cannot yet be removed or treated as fully isolated implementation paths.

## Blocking readiness gaps

1. The request/result contracts and canonical workflow explicitly remain synthetic/offline and perform no provider/source execution.
2. Coverage assessment is fixture-based; no approved real corpus/source coverage acceptance has been demonstrated.
3. There is no production worker/scheduler/provider adapter proven against the canonical lifecycle.
4. Legacy helper coupling should be separated into neutral storage/state primitives before declaring the old execution APIs isolated.
5. Production activation, real providers/corpus, Sentinel transport, and K-Trader integration remain outside this gate and require separate owner authorization.

Decision: do not declare `KGM_INDEPENDENT_RESEARCH_READY`. Continue with a behavior-preserving legacy-helper decoupling design and tests; do not activate real sources or external consumers.
