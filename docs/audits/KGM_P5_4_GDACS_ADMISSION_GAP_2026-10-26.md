# P5.4 — GDACS one matched RSS item vs zero admitted: offline admission audit

Date: 2026-10-26

## Trigger
Owner GitHub workflow_dispatch [40269356087](https://github.com/kolemasakar/K-Geopolitical-Monitor/actions/runs/40269356087) on SHA `e0501f021330add6039a83ce193b3c92380ec67e`: GDACS 319 RSS items, 1 literal topic match, 0 ingested; Consilium 20 RSS, 0 topic matches; GDELT NETWORK_TIMEOUT at dedicated 12s. Overall PARTIAL, 0 admitted evidence, report not run.

## Change
The independent GDACS counting predicate previously checked **only** text, whereas the admission adapter also required a title, a link and HTTPS. The shared `gdacs_admission_reason` now consistently classifies entry-level decisions as `ADMITTED`, `TOPIC_NO_MATCH`, `MISSING_TITLE`, `MISSING_LINK` and `UNSAFE_OR_NON_HTTPS_LINK`. The parser and the diagnostic counter use the same predicate, eliminating silent divergence in their logic. Counts only are emitted; never raw titles, URLs, descriptions or publisher payloads.

The policy stays **fail closed**: HTTP-only, credential-bearing, fragment-bearing and malformed links are rejected, not silently upgraded. This is not a claim that the previous single real match's exact cause has been discovered: that requires a separately authorized manual rerun with the new counters. The count `ADMITTED` reflects qualifying feed entries, while the existing adapter `max_records=10` may cap returned items.

GDELT remains a `NETWORK_TIMEOUT` under the 12-second budget from PR #280. Raising the timeout again without an independently diagnosed failure mechanism is not justified. No extra live calls, automatic retries, modified source allowlist or OS-level egress access were added.

## Critic
- Unit tests use fully synthetic RSS fixtures to demonstrate that one keyword match can fail admission due to missing link/title or non-HTTPS URL.
- Passing CI is evidence of correct classification logic only; no live source success or source truth is claimed.
- No real research report or claim verification: P5.5 remains BLOCKED.
- No persistent watches enabled, no production service changes, no messaging.

Gate: `P5_4_GDACS_ADMISSION_AUDIT_CI_PENDING / GDELT_TIMEOUT_UNRESOLVED / P5_5_REPORT_BLOCKED / PRODUCTION_NO_GO`.
FREE_ONLY / ON_DEMAND_ONLY / NO_SEND / CLEANUP_HOLD.
