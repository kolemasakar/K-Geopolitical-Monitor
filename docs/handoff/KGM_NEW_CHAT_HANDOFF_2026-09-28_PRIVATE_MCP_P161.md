# KGM new-chat handoff — 2026-09-28 — private owner MCP / PR #161

Status: DOCUMENTED HANDOFF ON DRAFT BRANCH; NOT MERGED; NO PRODUCTION DEPLOYMENT.

## Authoritative baseline and scope
- Repo: `kolemasakar/K-Geopolitical-Monitor`.
- Work branch: `audit/rdc-independence-20260925`; draft PR #161: https://github.com/kolemasakar/K-Geopolitical-Monitor/pull/161
- This handoff records **parallel private Plugin/MCP engineering**, not completion of the strategic Phase 23 gate.
- Existing strategic baseline in `docs/handoff/CURRENT_HANDOFF.md`, `docs/state/CURRENT_PROJECT_STATE.json`, `ROADMAP.md`: ROADMAP state-sync v4.66; P23.3 validated with zero corroboration population; P23.4 preselection complete, controlled UKSL pilot with material limitations; P23.4 expansion owner decision and validation pending. Keep strategic truth and source-activation gates unchanged.
- Government.ru non-UA VPN exit is owner-allowed but NOT CONFIGURED; do not assert reachability or deploy a VPN as part of Plugin work.
- Owner policy: FREE-ONLY, owner-only private Plugin first, no public ingress/Funnel, paid provider, cross-project runtime, HP-OMEN, new 5-minute polling, production changes or unapproved source activation.

## Validated MCP engineering
- Official SDK: `src/kgeopolitical_monitor/private_mcp_server.py`; `kgm_get_status` sanitized, read-only; no listener is created by the factory.
- Integrated local ASGI bearer gateway: `src/kgeopolitical_monitor/private_mcp_gateway_v2.py`. Dedicated >=32-character bearer, constant-time compare, deny Origin, POST /mcp only, max 4096 bytes buffered before SDK, per-process 30/60s rate limit, fixed audit codes. Separate legacy JSON-RPC-like adapter remains prototype and does not constitute official MCP transport.
- Superseded defective `private_mcp_gateway.py` deleted on commit `a30badf8641f89fe4dc4199cf475308687c8b759`.
- Latest **actually executed** focused suite: exact SHA `f8b823c5ae499059e16d0f266e3ba371513e8de7`; eight modules: `test_private_mcp_gateway_stream.py`, `test_private_mcp_gateway_security.py`, `test_private_mcp_gateway_integrated.py`, `test_private_mcp_http.py`, `test_private_mcp_server.py`, `test_private_mcp_adapter.py`, `test_private_plugin_status.py`, `test_backend_action_api.py`; **29 passed, 1 warning in 10.17s; exit 0** on KGM-only VM isolated venv. Warning is Starlette test-client deprecated anyio alias. Pytest warning configuration overridden with `-o filterwarnings=` because pinned Starlette lacks a newer warning class referenced by repository config; no tests disabled.
- Streamed oversized request with absent Content-Length, duplicated auth header, old token denied by a NEW gateway instance passed. New-instance token replacement is NOT live rotation or revocation.
- Later docs-only branch commits after tested SHA: `63f2d7f39ade9a48b6ed4fb1de598c1bc90515d5`, `124dc403319517c666ebbd6c7c2b3eeb908e221d`, `5a3ca27915f56b218ea302a3fd289560c0837d52`. This handoff commit will be newer; **do not claim latest HEAD has been exact-SHA tested** without rerun.
- Audit: `docs/audits/KGM_MCP_STREAM_TOKEN_SECURITY_2026-09-26.md`; prior exact-SHA acceptance and cleanup audits under `docs/audits/`.

## Connectivity and operational truth
- RDC device `kgm-e4-owner-pilot` id `b4c8a41a-449e-401e-aa73-6d6ec51ad16a` was observed **offline** on 2026-09-28 during handoff preparation. RDC offline does NOT imply KGM service offline; no fresh KGM runtime/acquisition health measurement available.
- Existing authorized SSH recovery, if owner has SSH: `/home/kgmops/.local/bin/kgm-rdc-watchdog.sh`. No recurring watchdog polling added.
- GitHub-hosted Actions quota contingency through 2026-10-01; prefer isolated local exact-SHA tests once KGM owner VM is reachable; do not infer quota state beyond that date without verification.

## Plugin and network gates
- `docs/design/KGM_PRIVATE_PLUGIN_TRANSPORT_DECISION_2026-09-26.md` and `docs/design/KGM_PRIVATE_PLUGIN_V0_1_PACKAGE_CONTRACT.md` specify candidate. Personal private KGM Plugin **not created**. Earlier Plugin Creator personal list returned no owned personal plugins at that time; recheck on resumption.
- Hosted ChatGPT private-tailnet access and supported transport NOT VERIFIED. Local `127.0.0.1` ASGI tests are not hosted connectivity evidence.
- No production listener, TLS endpoint, actual hosted connector, owner secret provisioning, live rotation/revocation, persistent audit or distributed rate limiting validated.
- Do not create a plugin archive with fabricated backend URL or declare activation. Do not use RDC/Tailscale admin tokens as Plugin credentials.

## Resume procedure
1. Verify current canonical main SHA and draft PR #161 HEAD/changes via GitHub; read `CURRENT_HANDOFF.md`, `CURRENT_PROJECT_STATE.json`, `ROADMAP.md` on canonical main; do not silently promote parallel MCP work into P23.4 validation.
2. Check RDC once. If offline, do docs-only work or ask owner to run existing SSH watchdog; do not repeatedly poll.
3. On isolated KGM VM, fetch exact draft HEAD, rerun focused 29-test suite, record exact SHA and observed outcome.
4. Complete threat review: exception paths, disconnect/timeout, Origin/proxy semantics, credential rotation/revocation, persistent audit, rate-limit scope. Verify current hosted Plugin private-network transport capability from authoritative docs before any network action.
5. Keep PR draft and do not merge/deploy/publish until independent review and owner-approved gates. Wait for user's transition generator to move to the next chat.

RESUME_FROM=KGM_PRIVATE_MCP_29_TESTS_PASS_DOCS_SYNCED_TRANSPORT_PENDING
NEXT_GATE=PRIVATE_MCP_SECURITY_TRANSPORT_CAPABILITY_VERIFIED
STRATEGIC_GATE_UNCHANGED=P23_4_EVIDENCE_YIELD_COVERAGE_EXPANSION_VALIDATED
