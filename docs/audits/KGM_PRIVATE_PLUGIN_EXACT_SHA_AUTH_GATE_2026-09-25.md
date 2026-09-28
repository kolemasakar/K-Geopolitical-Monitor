# Exact-SHA integration gate: execution constraints and auth review (2026-09-25)

Target branch SHA verified through GitHub refs API: `071af158b3ea316e498bf250a02d7bf82ffb975b` (before this documentation commit).

## Execution environment
- KGM-only RDC device `kgm-e4-owner-pilot` reported offline at check.
- Disposable execution container has pytest 9.0.2 and FastAPI 0.128.2 but cannot resolve github.com and has no authenticated private-repository checkout. GitHub connector permits source reads but cannot mount an exact-SHA checkout into that container.
- Accordingly **do not mark full integration tests passed**. The exact-SHA command remains `PYTHONPATH=src pytest -q tests/test_private_plugin_status.py tests/test_backend_action_api.py` in a verified KGM-only checkout. Do not run GitHub Actions before quota reset.

## Source-level auth and safety audit
- `/v1/private-plugin/status` uses `OwnerAuth` from existing FastAPI `create_action_app`; bearer token comparison is `secrets.compare_digest`, missing/wrong token returns 401.
- Added regression that monkeypatches both reader methods to raise on access while sending unauthenticated requests; added read-only persisted row-count check on authorized request. These tests are **committed but not yet executed against exact repository checkout**.
- Output adapter whitelists fields and applies strict ID/status/timestamp regexes; rejects bool-as-count; caps output at 20, returns explicit NOT_MEASURED/NOT_VERIFIED.
- Existing public `/health` and `/openapi.json` remain unauthenticated in `create_action_app`; neither should be exposed to the internet as part of the private Plugin. Token authentication alone is insufficient to establish private network transport, rate limiting or secure token provisioning.
- Existing `degraded_sources()` performs an unbounded upstream read; owner explicitly deferred optimization until public/multi-user release. Revisit earlier only if observed contention.

## Gate
`SOURCE_REVIEW_COMPLETE / EXACT_SHA_INTEGRATION_TEST_BLOCKED / PRIVATE_TRANSPORT_NOT_APPROVED / NO_DEPLOYMENT`.

Next: obtain authenticated KGM-only isolated checkout execution path, run the exact-SHA test command, save unredacted test counts and nonsecret environment details, and review owner-only transport without enabling public ingress.
