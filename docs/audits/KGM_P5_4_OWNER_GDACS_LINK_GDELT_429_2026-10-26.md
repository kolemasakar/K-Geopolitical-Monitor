# KGM P5.4 actual owner probe — GDACS unsafe-link admission and GDELT HTTP 429

Date: 2026-10-26. Evidence: GitHub Actions manual workflow_dispatch run [40270968105](https://github.com/kolemasakar/K-Geopolitical-Monitor/actions/runs/40270968105), canonical main SHA `f8b77b36e79798817c6377596d5ed2d46f38cd54`, job `one-shot-probe` #121403488180, all steps SUCCESS, source observation `2026-10-26T04:49:01.125237+00:00`.

## Grounded results

- Aggregate `collection_status=PARTIAL`, `source_success_count=2`, `source_failure_count=1`, `item_count=0`.
- GDACS: SUCCESS, 320 total RSS entries, one literal keyword match for the topic, zero admitted. Reason counts exactly: 319 `TOPIC_NO_MATCH`, 1 `UNSAFE_OR_NON_HTTPS_LINK`, 0 `ADMITTED`, 0 `MISSING_LINK`, 0 `MISSING_TITLE`. This is **specific evidence of the one-match admission rejection category**, not evidence that the event is false. Preserve fail-closed HTTPS requirements; do not rewrite or follow an unsafe link without new design review.
- Consilium: SUCCESS, 20 total RSS items, 0 keyword matches and 0 admitted.
- GDELT DOC 2.0: FAILED, HTTP status **429**, classified `HTTP_RESPONSE_FAILURE`, `MANUAL_BACKOFF_ONLY`. Earlier requests showed timeout; this run actually returned rate limiting. Do not mislabel as a generic DNS, TLS or permanent outage.
- `gdelt_timeout_budget_seconds=12`, `gdacs_dedicated_size_cap_bytes=1500000`.
- `analysis=NOT_EXECUTED`, `independent_claim_verification=NOT_ATTESTED`, `send=NONE`, `watch_persistence=EPHEMERAL_ONLY`. No OS-level egress guarantee; current live path has in-process allowlist only.

## Critic / acceptance

**PASS:** bounded owner-initiated GitHub manual route, GDACS/Consilium feed reading, GDACS exact stage-level rejection counters, GDELT HTTP error classification, no production or persistent-watch change.

**SHORTFALL:** zero admitted events and zero primary-source corroboration. P5.4 remains PARTIAL; P5.5 remains BLOCKED.

**NEXT:** investigate GDACS actual RSS link format via a bounded offline captured fixture or safe anonymized metadata (do not export private content), evaluate allowing only verifiably safe canonical URLs in a separately reviewed code change; inspect official GDELT 429 guidance and avoid back-to-back live requests or uncontrolled retry. A new manually approved live probe may occur only after explicit decision. Do not automatically activate monitoring, increase external access, or relax TLS/HTTPS.

Gate: `P5_4_GDACS_UNSAFE_LINK_GDELT_HTTP429_ZERO_EVIDENCE / P5_5_REPORT_BLOCKED / PRODUCTION_NO_GO`.

Policies: FREE_ONLY / ON_DEMAND_ONLY / NO_SEND / CLEANUP_HOLD.
