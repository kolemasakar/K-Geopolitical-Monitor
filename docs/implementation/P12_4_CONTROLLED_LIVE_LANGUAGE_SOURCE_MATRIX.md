# P12.4 — Controlled-Live Local-Language Source Matrix

Date: 2026-09-01
State: `EVIDENCE_CAPTURED / 4_OF_4_ACQUISITION_PATHS_SUCCESSFUL`
Implementation candidate: `595d7f0f0e6316e95aca518bb9309e615f239479`
Workflow: `P12.4 Controlled Live Language Source Smoke`
Run: `33531518652`
Job: `99935565895`
Checked at: `2026-09-01T16:24:00.594217+00:00`

## Purpose

Capture real read-only P12.2 adapter execution against the P12.4 initial local-language media/discovery slice. This matrix measures endpoint acquisition, RSS parsing and native-query matching only. It is not evidence of factual truth, independent-origin count, exhaustive language/region coverage, continuous uptime or production readiness.

## Results

| Source | Language | Native query | Endpoint | Result | Matched items |
| --- | --- | --- | --- | --- | ---: |
| Ukrainska Pravda — Ukrainian News | `uk` | `Україна` | `https://www.pravda.com.ua/rss/view_news/` | `SUCCESS` | 0 |
| Meduza — Russian RSS | `ru` | `Украина` | `https://meduza.io/rss/all` | `SUCCESS` | 1 |
| RMF24 — Polish News | `pl` | `Ukraina` | `https://www.rmf24.pl/feed` | `SUCCESS` | 1 |
| Haberturk — Turkish News | `tr` | `Ukrayna` | `https://www.haberturk.com/rss` | `SUCCESS` | 0 |

Overall probe state: `COMPLETED`.

- source successes: `4`;
- source failures: `0`;
- transport/parser failures: `0`;
- source-specific native-query matching: `2` sources produced matches, `2` produced zero matches.

Zero native-query matches are not acquisition/parser failures and are not evidence that the publisher had no relevant material outside the bounded feed/query surface.

## Operational Availability Consequence

For this controlled-live probe, all four configured endpoints support `ACTIVE` operational availability:

- `ukrainska-pravda-uk` — `ACTIVE`;
- `meduza-ru` — `ACTIVE`;
- `rmf24-pl` — `ACTIVE`;
- `haberturk-tr` — `ACTIVE`.

`ACTIVE` records a validated current acquisition path. It does not claim continuous uptime.

## Original-Language / Translation Boundary

- acquisition preserves original Unicode title/summary and original URL;
- adapter metadata records `content_language`, native query term, region scope and `translation_state=ORIGINAL_NOT_TRANSLATED`;
- translation is a separate derived representation;
- translation never creates another source or independent origin.

## Provenance / Coverage Boundary

- a media publisher is not automatically the underlying origin;
- media/domain/language/adapter/item count is not independent-origin count;
- syndication, wire copy, citation, repost and translation must not be double-counted as independent corroboration;
- successful parsing does not promote verification;
- the configured `uk/ru/pl/tr` slice is not global language coverage;
- inaccessible, local, closed, removed and not-yet-indexed sources remain explicit gaps.

## Runtime / Security Boundary

- public anonymous HTTPS GET only;
- no credentials;
- no paid provider;
- no public KGM ingress;
- runtime storage remains `PROJECT_LOCAL_ONLY`;
- production/live operational status remains `NOT_OPERATIONAL`.
