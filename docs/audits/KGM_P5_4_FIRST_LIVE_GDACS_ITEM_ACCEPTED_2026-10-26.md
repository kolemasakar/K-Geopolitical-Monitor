# KGM P5.4 owner live test — first accepted GDACS item (2026-10-26)

## Exact evidence

Manual owner GitHub Actions workflow_dispatch [run 40272331792](https://github.com/kolemasakar/K-Geopolitical-Monitor/actions/runs/40272331792), on main `55b71abc1d80441f0cb2aa674121386cf57a0721`, job `one-shot-probe` #121407630698 all steps SUCCESS. Observation timestamp `2026-10-26T05:05:01.236493+00:00`.

The actual aggregate report:
- `collection_status=PARTIAL`; `source_success_count=2`, `source_failure_count=1`; `item_count=1`.
- GDACS RSS: SUCCESS; 320 feed entries, 1 text-topic match; `TRUSTED_GDACS_HTTP_NORMALIZED=1`, `ADMITTED=0`, `UNSAFE_OR_NON_HTTPS_LINK=0`, `TOPIC_NO_MATCH=319`, `MISSING_LINK=0`, `MISSING_TITLE=0`; *one* accepted data record. This verifies the formerly blocked legacy HTTP link-to-HTTPS code path in one actual run; article dereference and publisher-domain authenticity are NOT verified.
- Consilium RSS: SUCCESS; 20 feed entries, 0 topic matches, 0 accepted.
- GDELT DOC 2.0: FAILED, HTTP 429; `MANUAL_BACKOFF_ONLY`; 0 accepted. No automatic retries or egress changes authorized.
- `gdelt_timeout_budget_seconds=12`, `gdacs_dedicated_size_cap_bytes=1500000`, `watch_persistence=EPHEMERAL_ONLY`, `send=NONE`, `analysis=NOT_EXECUTED`, `independent_claim_verification=NOT_ATTESTED`.
- Live workflow uses application-level allowlist; `network_policy=IN_PROCESS_ALLOWLIST_ONLY_NOT_OS_EGRESS_ATTESTATION`. Never assert OS-enforced egress or production readiness.

## Critic

**PASS**: manually triggered owner action, protected one-shot on-demand path, actual GDACS item admission through narrow trusted-domain legacy link normalization, aggregate evidence accounting, 2/3 reachable source adapters.

**PARTIAL**: three-source collection because GDELT 429.

**NOT ACCEPTED**: item authenticity and source page body, publication date and relevance, contradiction resolution, independent cross-source corroboration, analyst findings, Critic-reviewed report and production endpoint. One collected record is not itself a verified claim. Collection SQLite was ephemeral; raw article content was not exported as an artifact.

## Next gates

P5.4 GDACS adapter acceptance `LIVE_PASS_WITH_LIMITATIONS`; global multi-source collection `PARTIAL`; P5.5 evidence provenance + independent claim verification + report `BLOCKED` until executed and attested. Implement a separately bounded, owner-authorized and isolated original-source evidence path before any P5.5 publication. Respect GDELT HTTP429 without automatic retries.

FREE_ONLY / ON_DEMAND_ONLY / NO_SEND / CLEANUP_HOLD / PRODUCTION_NO_GO.
