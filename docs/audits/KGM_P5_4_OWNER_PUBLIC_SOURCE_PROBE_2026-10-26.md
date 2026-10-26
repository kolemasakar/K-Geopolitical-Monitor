# KGM P5.4 — Owner-only, one-shot public source probe (2026-10-26)

## Scope and launch

This PR adds an owner-manual **public, read-only source collection diagnostic**, not a production on-demand research service. The sole trigger is GitHub Actions `workflow_dispatch` on `main` by `kolemasakar` (checked both in workflow and `authorize_public_probe`). Separate mode `PUBLIC_SOURCE_READONLY` is **never** accepted by the existing fixture-only `authorize_manual_request`.

One invocation attempts exactly one HTTPS GET each from **GDACS RSS**, **Consilium RSS**, and **GDELT DOC 2.0** using the existing restricted transport, 3-request budget, per-request 7-second timeout, at most 512 KiB per response, exact hostname/path allowlist, no redirects, ambient proxy disabled, no credentials. GDELT uses bounded 24-hour discovery and at most 10 records; GDACS parser at most 10 items. All work is performed against a disposable local SQLite and one disposable internal watch; persistent production watches remain disabled. No service restart, retention cleanup, consumer send or notification.

**Explicit architecture warning:** `RestrictedSourceTransport` is a Python in-process allowlist, NOT kernel-enforced egress. The ephemeral GitHub runner has general network capability for dependency installation. This workflow is a limited owner-requested **diagnostic** with no secrets, not a hardened external-source execution environment. Do **not** interpret it as passing the previously OPEN hard egress-control gate.

The workflow prints only aggregation per adapter: SUCCESS/FAILED, item count, timestamps, SHA-256 of public topic, no raw titles/URLs/query or errors; output status can be COMPLETED, PARTIAL or FAILED. Such a source attempt is NOT independent verification of a geopolitical claim, a scholarly Critic result, or a finished brief. It deliberately does not invoke claim analysis.

## Test and safety gates

Tests use injected synthetic transport, assert 3 distinct source attempts and fail-closed total failure; test owner/repository/ref/event/mode restrictions; assert no scheduled trigger. Live workflow is not triggered by a PR or push. No production secrets or DB is mounted.

Only after CI merges can the GitHub owner manually use:
`Actions → KGM P5.4 Owner Public Source Probe → Run workflow` on `main`.
Use a public non-sensitive keyword, e.g. `Ukraine`; topic may appear in workflow-dispatch metadata, so NEVER enter private user data.

**Limitations**: External HTTP status, response validity and freshness remain UNKNOWN until manual execution logs provide evidence. GDACS may legitimately contain zero keyword matches; GDELT and Consilium could return no items. On error we report FAILED for that adapter, not falsely PASS. A successful source fetch alone is not a complete geopolitical analysis.

After actual user-initiated run: independently audit job steps and per-source aggregates, assess source provenance, freshness and independence, then plan P5.5 report generation. No live production or ChatGPT plugin activation is authorized.

Gates before manual run:
`P5_4_OWNER_READONLY_PROBE_CODE_CI_PENDING / P5_4_LIVE_RESPONSES_NOT_ATTESTED / HARD_EGRESS_NOT_ATTESTED / PRODUCTION_NO_GO`.

Policies: `ON_DEMAND_ONLY / FREE_ONLY / NO_SEND / CLEANUP_HOLD`.
