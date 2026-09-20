# P23.1 — B1 Blocker Remediation & Selective Source Readiness Result

Date: 2026-09-20
Status: `VALIDATED_WITH_PARTIAL_REMEDIATION`
Gate: `P23_1_B1_BLOCKER_REMEDIATION_READINESS_VALIDATED`

## UK Sanctions List

The Phase-22 `BOUNDED_RESPONSE_LIMIT` was reproduced and decomposed into two independent issues:

- the official CSV is about 49.9 MB, larger than the bounded transport;
- the live file contains a `Report Date` preamble before the actual CSV header, so the historical parser recognized zero names on the sampled live payload.

Repository-only remediation now:

- requests only the initial 1.5 MB using HTTP Range;
- keeps the existing 2 MB transport ceiling unchanged;
- detects the CSV header structurally from required fields;
- fails closed if the canonical fields are absent;
- preserves deterministic `max_entries` output.

Exact-branch owner-node probe returned 100 items successfully in about 0.08 s.

This is readiness evidence only. `uk-sanctions-list-en` is **not activated** and still requires an explicit owner activation decision.

## Government of Russia

The canonical HTTPS endpoint remains unreachable from `kgm-e4-owner-pilot`.

Observed:

- `http://government.ru/news/` responds on port 80;
- `https://government.ru/news/` times out;
- first-party HTTPS checks for `government.ru`, `www.government.ru`, `services.government.ru`, and `premier.gov.ru` all timed out;
- the reachable HTTP page exposes `/all/rss/` and `/news/rss/`, but those remain on the same HTTP-only reachable transport path from this vantage.

KGM does not downgrade to HTTP. The HTTPS-only acquisition boundary is preserved, so `russian-government-news-ru` remains blocked.

## Decision

P23.1 is validated with partial remediation:

- UKSL bounded acquisition/parser readiness: `PASS`;
- Government of Russia HTTPS readiness: `BLOCKED`;
- new source activation delta: `0`;
- acquisition resource-limit relaxation: `NO`;
- runtime deployment/restart: `NO`.

Next gate: `P23_2_UNDERLYING_ORIGIN_PROVENANCE_RESOLUTION_VALIDATED`.
