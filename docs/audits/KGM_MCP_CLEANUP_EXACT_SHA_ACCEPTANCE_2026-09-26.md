# KGM private MCP cleanup exact-SHA acceptance — 2026-09-26

- Obsolete `src/kgeopolitical_monitor/private_mcp_gateway.py` removed from draft PR #161. Active tested gateway remains `private_mcp_gateway_v2.py`.
- KGM VM isolated checkout exact SHA `a30badf8641f89fe4dc4199cf475308687c8b759`.
- Explicit file-absence check: `OBSOLETE_DRAFT_REMOVED=PASS`.
- Full focused suite: `23 passed, 1 warning in 10.18s`, exit 0, in isolated `mcp-http-venv` with warning-filter configuration override. Deprecation warning originates in pinned Starlette test client.
- Verified official MCP SDK ASGI HTTP protocol and integrated local gateway tests, but **no production listener or remote ChatGPT connectivity**. Per-process in-memory rate limit does not establish distributed rate limiting.
- A proposed additional denial-regression test file could not be created because the tool call was blocked; **do not count these proposed tests as executed**.
- Draft PR #161 remains unmerged. No production deploy, paid services, public ingress, Funnel, or plugin publication.
- Next gates: extend denial tests (duplicate Authorization, chunked oversized requests, upstream exception, token rotation/revocation), independent security review of the gateway, credential handling, and proof of a private transport actually reachable by hosted ChatGPT. Any internet-exposed transport requires owner approval.
