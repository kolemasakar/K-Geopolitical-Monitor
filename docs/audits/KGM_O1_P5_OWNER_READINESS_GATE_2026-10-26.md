# KGM O1 P5 — On-demand owner pilot gate audit (2026-10-26)

**Result: SHORTFALL / NO LIVE END-TO-END EXECUTION / PRODUCTION NO_GO.**

Scope: owner-directed P5 steps 1–5. This audit distinguishes actual execution evidence from earlier offline CI and public-source discovery.

## Step 1: Network namespace qualification — SHORTFALL (direct live diagnostic)

Read-only/nonpersistent shell on existing `kgm-e4-owner-pilot`:
```text
/usr/bin/unshare
unshare: write failed /proc/self/uid_map: Operation not permitted
UNSHARE_EXIT:1
```
Command: `unshare --user --map-root-user --net -- /bin/true`, intentionally no application payload, no network collection and no production DB writes. The unprivileged user/net namespace **could not be established** in current host policy. Fail-closed means **no fallback to host network**, no request for more capabilities, no sysctl tweaks. A different already-approved isolated executor is required for future E2E.

## Step 2: Request authorization / loaded deployment — SHORTFALL

Host checks: `kgm-monitor.service = active`; new `src/kgeopolitical_monitor/on_demand_dispatcher.py` **absent** in production checkout. Existing deployment disk SHA historically `b31b2136b5fe982d0b63b0135479b1549041906c`; loaded in-memory code identity UNKNOWN. PR #263 created an offline, internal library dispatcher, **not** an authenticated user API. No approved live request authorization and no production route have been demonstrated. User owner instructing an audit is not a deployment or permission-expansion gate.

## Step 3: External public sources — PARTIAL / no verified live adapter response

Public website discovery: official GDACS feed reference lists RSS feeds; Council/Consilium press publication pages are indexed; GDELT DOC API documentation is public. Independent URL attempts on source endpoints returned a client/tool-level `unsupported content-type` for GDACS XML and Consilium XML; direct GDELT API URL was inaccessible in the browsing environment. Those **are not** source HTTP status results and are not valid evidence of live adapter success/failure or fresh data. Record `LIVE_SOURCE_RESPONSE_UNVERIFIED` for all three. No network dispatch through KGM occurred.

## Step 4: End-to-end request/collect/verify/analyze/report — SHORTFALL

Offline suite PR #262 exercises temporary synthetic watch and SQL provenance, while PR #263 internal fixture-only dispatcher and PR #264 policy/GDACS/age validation are offline-tested. They **do not** deliver an authenticated user request via a real KGM execution interface. Both persistent production watches remain disabled (expected ON_DEMAND_ONLY design). Do not convert production `unattended_runner --once` into a user request, activate watches, or label an external web search as KGM E2E.

## Step 5: Critic / remediation priorities

| Check | Gate |
|---|---|
| Report proves network namespace startup on actual host | SHORTFALL |
| User authorization and authenticated request entrypoint | SHORTFALL |
| One bounded outbound source fetch via KGM | NOT_EXECUTED |
| Verified independent source ownership/syndication | UNKNOWN |
| Source timestamps and article-level primary provenance | UNKNOWN |
| End-to-end run to auditable response | NOT_EXECUTED |
| Production data integrity and no scheduled watch activation | No production data writes/activation were performed in this audit |
| API-level NO_SEND, bounded budgets, deny-by-default | Not E2E attested |
| False claims of production success absent | PASS |

Critic conclusions: (1) no source may be called *fresh* merely because its official page exists; (2) per-source transport failures cannot be inferred from tooling's unsupported XML type; (3) a tested Python dispatcher in repo is not a deployed authenticated route; (4) a failed unshare test must not trigger more rights or silent fallback; (5) independent URLs are not automatically independent origins.

**Next feasible plan**: build/attest an external isolated execution worker (outside production VM) with hard egress/timeout limits, an authorized one-request ingress, source allowlist, TTL and immutable evidence report; test actual namespace startup in that dedicated environment; then seek independent production/live pilot approval. If no free isolated environment is available, keep NO_GO and develop offline only.

FREE_ONLY / ON_DEMAND_ONLY / NO_SEND / CLEANUP_HOLD / PRODUCTION_NO_GO. No system changes.
