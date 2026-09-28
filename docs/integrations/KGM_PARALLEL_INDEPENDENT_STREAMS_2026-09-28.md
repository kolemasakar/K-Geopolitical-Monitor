# Parallel KGM-only preparation checkpoint

Date: 2026-09-28. Owner authorized independent streams A (request/response), B (historical coverage), C (security/acceptance). Do not interact with K-Trader until separately ready.

Exact tested code SHA: `d9d5dad97f73d474737edd0c3b76b10b2ebadb47`. Authorized isolated KGM host checkout; 14 explicit exchange/research test modules: **94 passed in 0.87s, exit 0**. No production deployment or live source calls.

**Stream A:** `research_typed_spool_v1.py` now validates the fully typed synthetic result before publishing a correlated, immutable, digest-bound per-consumer response. Negative tests cover duplicate idempotent replay, conflicting publication, historical lookahead and policy revocation. Existing minimal `research_spool_v1.process_fixture` remains available for legacy synthetic tests; do not confuse its minimal output with the new typed path.

**Stream B:** `research_coverage_fixture_v1.py` evaluates only explicitly supplied synthetic historical corpus windows and publication/availability timestamps. Unknown or unverified windows yield UNMEASURED; even a declared complete synthetic window with no matching evidence **never** authorizes a claim that no significant news occurred. Real KGM historical corpus, ingestion health and source licensing remain unmeasured.

**Stream C:** Prior local negative tests validate tampering, policy revocation and cross-consumer retrieval at the application layer. They do **not** establish OS-level ACL isolation, hostile-local-user resistance, authentic transport identity or crash-safe end-to-end queue transitions. Before KGM_INDEPENDENT_RESEARCH_READY, add persisted lifecycle and quotas, stricter filesystem and atomic no-clobber checks, actual authorized corpus observation, and a standalone offline acceptance bundle. Do not claim private cross-host E2E PASS.

Remaining gates: owner-reviewed request and release policy, full canonical KGM data mapping and actual source coverage, per-consumer OS isolation and authenticated private transport. Plugin PR #161 paused. Phase 23 unchanged.
