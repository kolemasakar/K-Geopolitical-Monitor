# KGM private Plugin v0.1 — migration implementation package

Status: IMPLEMENTATION-READY INSTRUCTION DRAFT; NOT REGISTERED; NO HOSTED CONNECTION CLAIM.
Owner direction: mandatory full Plugin migration before tunnel research (2026-09-28 decision).

## Identity and privacy
Name: K-Geopolitical Monitor
Description: Owner-only, read-only access to sanitized KGM project status; never infer unmeasured runtime health.
Scope: personal USER; PRIVATE. No listing, publication, sharing or cross-project app dependencies.
Version candidate: 0.1.0.

## Core Plugin instructions (candidate)
- Serve only the owner's K-Geopolitical Monitor requests.
- For live project status use the connected KGM MCP tool `kgm_get_status` only when its real connection is available.
- Report the returned values verbatim in meaning, preserving `NOT_MEASURED`, `NOT_VERIFIED`, stale, unavailable and unknown distinctions.
- Distinguish canonical strategic repository state, parallel draft engineering, and live VM runtime observations.
- Never infer live health from an offline remote desktop connection or from historical test results.
- Never invoke shell, filesystem, database, deployment, source activation, other projects' plugins or unapproved external providers.
- No background polling. No automatic public publication or credential disclosure.
- If the connection is absent, explain that live KGM status is unavailable; do not fabricate a response.

## Tool mapping
- KGM official MCP server: `src/kgeopolitical_monitor/private_mcp_server.py`.
- Only `kgm_get_status` allowed for v0.1.
- HTTP contract: Streamable HTTP `/mcp`, authenticated by dedicated owner-only KGM credential via gateway v2; **endpoint intentionally unset** until a verified approved private route exists.
- Return shape: follow actual official MCP server tool schema, do not invent manifest argument fields or live status fields.
- Explicitly exclude `kgm_get_brief`, `kgm_get_events`, `kgm_get_evidence` until later separately approved releases.

## Package assembly gates
1. Retrieve the actual current Plugin Creator manifest/app schema and required package paths from a verified schema/example. Do not invent plugin.json or app.json structure.
2. Build private candidate archive with these instructions, only required manifests and verified app mapping. No credentials, no local/imaginary endpoint, no KGM internal documents beyond the instructions.
3. Validate the archive schema and local static security properties. Keep unconnected candidate distinct from installed live Plugin.
4. Rerun focused tests against final exact SHA on isolated KGM environment, including negative auth, oversize streaming, duplicate headers, no Origin, redaction, and bounded resource use.
5. Audit exception paths, disconnect/timeout, proxy/Origin semantics, rotation/revocation, persistent audit and rate-limit process boundaries; record PASS/FAIL/UNKNOWN separately.
6. After preparation, research native private transport or approved free-only outbound tunnel, and demonstrate synthetic hosted initialize/list/call/unauthorized denial.
7. Provision dedicated KGM-only credentials only after owner-approved network/secret gate; register/activate PRIVATE Plugin and run end-to-end read-only acceptance. Do not create an unusable live connector.

## Release gate
PREPARATION_STARTED / PACKAGE_SCHEMA_NOT_YET_VERIFIED / TRANSPORT_NOT_YET_VERIFIED / PLUGIN_NOT_CREATED.
Strategic P23.4 evidence/coverage decision is unchanged.
