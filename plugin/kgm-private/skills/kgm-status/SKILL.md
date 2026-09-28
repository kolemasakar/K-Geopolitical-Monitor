---
name: kgm-status
description: Read-only owner KGM status; use the connected KGM MCP tool only after its private transport is verified.
---

# KGM status

Use only the dedicated KGM `kgm_get_status` MCP tool when it is actually connected. Never fabricate tool responses or assert production health based on historical tests. Preserve NOT_MEASURED, NOT_VERIFIED, stale, unknown and source timestamps. Distinguish canonical main, draft engineering and measured runtime. Do not access other projects, execute shell/SQL, deploy, activate sources, or poll. If no MCP tool is connected, explicitly state that live KGM status is unavailable. Never reveal credentials.
