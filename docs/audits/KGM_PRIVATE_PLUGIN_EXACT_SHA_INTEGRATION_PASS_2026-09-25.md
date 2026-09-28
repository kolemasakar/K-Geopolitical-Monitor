# Exact-SHA private plugin integration acceptance — 2026-09-25

## Verified isolated execution
- Device: KGM-only `kgm-e4-owner-pilot`, user `kgmops`; RDC online and command execution confirmed.
- Repository fetched from private GitHub URL into isolated `/home/kgmops/validation/kgeopolitical-monitor/private-plugin-gate/repo`; detached checkout verified at `071af158b3ea316e498bf250a02d7bf82ffb975b`; git status clean (0 modified files).
- Used preexisting KGM validation virtual environment (pytest 9.1.1); no production runtime, DB, service or credentials modified.

```bash
cd /home/kgmops/validation/kgeopolitical-monitor/private-plugin-gate/repo
PYTHONPATH=src /home/kgmops/validation/kgeopolitical-monitor/p23-4/venv/bin/python -m pytest -q tests/test_private_plugin_status.py tests/test_backend_action_api.py
```

Actual result:
```
.............. [100%]
14 passed in 9.96s
Process exit code 0
```

## Scope and limitations
- PASS: projection synthetic tests and FastAPI integration tests, including owner auth negative paths and read-only fixture checks.
- NOT YET VALIDATED: private owner transport, secure credential provisioning, exposure/rate-limiting architecture, actual plugin activation, production health and continuity.
- Existing public `/health` and `/openapi.json` endpoints in application code remain unauthenticated; do not deploy or expose this API as-is on public ingress.
- Keep PR draft; no production deployment or merge authorized by this test alone.
- Previously documented SQL optimization remains deferred by owner decision until public/multi-user release or observed performance degradation.
