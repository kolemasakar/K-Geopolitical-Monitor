# P24.1 — Source Parser and Mapping Acceptance Checkpoint 02

Status: CHECKPOINT_02_PASS_WITH_KNOWN_BOUNDARIES / P24_1_CONTINUES
Recorded: 2026-10-13
Code PR: #166 stacked on independent research PR #163. Code HEAD 5c5dd2e34f1b898539530328ea9a310e1d9d8dcd.

## Two direct public official pages: HTTP200 and actual parser SUCCESS
UK: https://www.gov.uk/government/news/joint-uk-germany-statement-berlin-8-october-2026
UK parsed publication time: 2026-10-08T13:36:40Z, source origin uk-government.
Germany: https://www.bundesregierung.de/breg-en/news/chancellor-merz-uk-pm-burnham-2456444
German live page lacked expected time datetime element; initial parser failed. Narrow fallback extracts unique article-header list item Thursday, 8 October 2026, rejects ambiguous or inconsistent weekday data.
German parser after fix SUCCESS, published-at day anchor 2026-10-08T00:00:00Z. This is DATE-ONLY SOURCE PRECISION, NOT VERIFIED CLOCK TIME.
Both source-bound opt-in profiles attached a shared Kensington Treaty ratification event. Result: event_match TRUE; claim_match TRUE; independent_origin_candidate TRUE, two distinct official origin groups. No automatic factual verification was added.

## Negative contract coverage
Source-specific identity and strict phrase checks; wrong or incomplete source text fails closed; profile copy isolation.
False positives blocked for changed event day, contradictory claims, copied identical origin on different publishers, duplicate publisher, unapproved source profile.
Naive/missing/bad publication timestamps rejected; transport TLS timeout and OSError report UNAVAILABLE; ambiguous German day header rejected.

## Test provenance and limits
Initial venv editable import erroneously pointed to previous research checkout. Results from that environment were not accepted for PR166.
Corrected by setting PYTHONPATH to the exact detached PR166 worktree src and tests.
Focused exact-head tests: 32 PASS at 5c5dd2e34f1b898539530328ea9a310e1d9d8dcd.
Final exact-head ARM64 full suite: 1745 passed in 533.43s; GitHub CI #3009: 1745 passed in 167.59s, SUCCESS. PR #166 MERGED into research PR #163 ONLY at merge SHA 2bfd2cc4b0c71072abff64d4be1231a11feb2cfc; canonical main not changed by this code merge.
Of 11 dedicated adapters only UK and German official page parsers were directly validated against actual content here. HTTP200 alone is insufficient. GDELT TLS timeout remains separate transport degradation.

## Release boundary
P24.1 remains IN PROGRESS. Code PR #166 is merged into draft research PR #163 only; no research code merged to canonical main. No production, public Plugin, paid resources, unattended scheduler or cross-project integration.
