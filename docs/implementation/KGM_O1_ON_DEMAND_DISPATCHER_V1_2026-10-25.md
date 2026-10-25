# KGM O1 — One-shot offline dispatcher V1

Date: 2026-10-25. Scope: **library API, synthetic offline adapters only**.

## Public API within source tree

`OnDemandRequest(topic, requested_at, request_id)` → `dispatch_offline_once(request, adapters=[...])` → `OnDemandResult`.

The dispatcher validates a bounded topic, explicit UTC-aware time and short request identifier; refuses missing, duplicate, or >5 adapters; and permits only adapters with `offline_fixture_only is True`. The library accepts adapters injected by **trusted test code**. The marker is a contract, **not** a sandbox or a security boundary against a malicious adapter. No user-facing/public API or CLI is installed.

Each request owns a `TemporaryDirectory` containing an ephemeral SQLite schema and one *fixture-only* enabled watch, solely to reuse existing M7/M8 pipeline. The temporary workspace is removed on scope exit. No production watch, persistent server DB, service, scheduler, or backend Action API is modified. A one-shot request must yield exactly one execution. Only aggregate status, source attempt counts, evidence/finding counts, source identity count, and time are returned; no raw events or URLs.

Tests cover two synthetic successes, PARTIAL collection with one failed adapter, full failure without fabricated findings, invalid input and denial of an adapter not marked offline. GitHub CI acceptance is reported separately; do not claim run success until it completes.

## Limitations and OPEN gates

- `distinct_source_id_count` is NOT independent-source-origin attestation; domain ownership and evidence independence remain separate.
- The installed adapter type declaration does not itself prevent network access. Use controlled/frozen test fixtures only. Enforced no-network sandbox/runner still OPEN.
- Fresh external data, GDACS/GDELT/Consilium activation, actual user-request transport/auth, deadlines/resource budgets, source freshness, Critic review, disagreement handling and production routing are **not verified by this library**.
- No consumer/TG dispatch, public HTTP execution, scheduled watches, production release or database migration is authorized. Do not call live `execute_due` against production as a substitute for request handling.
- Before any live one-shot pilot, implement externally enforced egress/time budgets, approved source allowlist with attestable identity, request authorization and final audit. Keep fail-closed rollback/cleanup policies.

Acceptance proposed: `O1_DISPATCHER_OFFLINE_V1_TESTED` only if CI passes; `ON_DEMAND_LIVE_INTEGRATION_OPEN`, `PRODUCTION_NO_GO`.

FREE_ONLY / NO_SEND / CLEANUP_HOLD remain.
