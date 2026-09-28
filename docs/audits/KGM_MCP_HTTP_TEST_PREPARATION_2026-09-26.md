# KGM official MCP HTTP test preparation — 2026-09-26

Status: `TEST_PREPARED / EXECUTION_BLOCKED_BY_KGM_RDC_OFFLINE`.

## New test files
- `tests/test_private_mcp_http.py`: official SDK Streamable HTTP ASGI test; initialize, tools/list, tools/call with stateless JSON responses, no socket or external ingress.
- `tests/requirements-private-mcp.txt`: disposable-venv pins for MCP 1.30.0 and FastAPI/Starlette/httpx compatibility. Pins are proposed, **not yet installed or validated**.

## Why not executed
KGM-only RDC device `kgm-e4-owner-pilot` returned `offline` twice in the current session (last seen 2026-09-25T23:11:35Z). No alternative project machine was used. Do not assert KGM service outage from RDC state. No live tests or production changes performed.

## Next owner-side step if RDC remains offline
Via existing authorized Tailscale SSH (do not expose tokens or change ingress), inspect `pgrep -af desktop-commander` and bounded log tail of `~/.local/state/desktop-commander/remote.log`, redacting any credential content. If process absent, run the existing `~/.local/bin/kgm-rdc-watchdog.sh` once and recheck device. If process present but disconnected, inspect status before any restart; do not clear pairing.

## Acceptance command when RDC returns
In existing KGM-only isolated checkout at `/home/kgmops/validation/kgeopolitical-monitor/private-plugin-gate/repo`, fetch branch, checkout exact SHA, create a NEW disposable virtual environment under `private-plugin-gate`, install `tests/requirements-private-mcp.txt`, run `python -m pip check` then:
```bash
PYTHONPATH=src python -m pytest -q tests/test_private_mcp_http.py tests/test_private_mcp_server.py tests/test_private_mcp_adapter.py tests/test_private_plugin_status.py tests/test_backend_action_api.py
```
Do not mark acceptance until real command output and exact SHA are recorded. Local ASGI compatibility does not establish ChatGPT hosted Plugin reachability or authenticated gateway security. No public ingress, PR merge, production deployment or plugin publication.
