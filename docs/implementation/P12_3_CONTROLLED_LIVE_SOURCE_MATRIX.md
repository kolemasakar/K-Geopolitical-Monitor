# P12.3 — Controlled-Live Authoritative Source Matrix

Date: 2026-09-01
State: `VALIDATED_EVIDENCE / 3_ACTIVE_1_DEGRADED`
Validation anchor: `038122e44139d6ff23bc5d79bb50a8dee3c38cde`
Workflow: `P12.3 Controlled Live Source Smoke`

## Probes

First probe:
- commit `dbeed606db6d07602b0a17d86c30838afd8a4213`;
- run `33527134432`, job `99920724311`;
- `3 SUCCESS / 1 FAILED`, overall `PARTIAL`.

Repeat probe on validation anchor:
- run `33527433106`, job `99921745640`;
- checked at `2026-09-01T15:43:14.116668+00:00`;
- `3 SUCCESS / 1 FAILED`, overall `PARTIAL`.

## Repeat Results

| Source | Adapter | Endpoint | Result | Parsed items | Governed state |
| --- | --- | --- | --- | ---: | --- |
| European Commission Press Corner | `ec-presscorner-rss-atom@P12.2-2.0` | `https://ec.europa.eu/commission/presscorner/api/rss` | `SUCCESS` | 1 | `ACTIVE` |
| European Parliament Press Releases | `ep-press-releases-rss-atom@P12.2-2.0` | `https://www.europarl.europa.eu/rss/doc/press-releases/en.xml` | `FAILED` — payload not valid XML | 0 | `DEGRADED` |
| UK Government News and Communications | `govuk-news-atom@P12.2-2.0` | `https://www.gov.uk/search/news-and-communications.atom` | `SUCCESS` | 0 | `ACTIVE` |
| OSCE Latest News | `osce-latest-rss-atom@P12.2-2.0` | `https://feeds.osce.org/OSCELatestNews` | `SUCCESS` | 7 | `ACTIVE` |

Failure isolation: `PASS`.

## European Parliament Diagnosis

The European Parliament's official RSS directory resolves `Press releases - All (XML)` to the configured endpoint. Controlled-live retrieval from the unattended runner returns anti-bot HTML requiring JavaScript rather than RSS XML. P12.2 therefore fails closed at XML parsing.

The official URL is retained. No third-party mirror is substituted and no anti-bot bypass is authorized. Operational availability is explicitly governed as `DEGRADED`.

## Interpretation Boundaries

- acquisition/parser state is operational evidence only;
- source count is not independent-origin count;
- official publication confirms what the institution published/stated, not automatically the underlying event;
- zero parsed query matches is not a transport failure;
- a successful probe is not continuous uptime evidence;
- a failed probe is not evidence that relevant information does not exist;
- this matrix is not proof of exhaustive coverage.

## Runtime / Security Boundary

- read-only HTTPS;
- public anonymous endpoints;
- no credentials;
- no paid provider;
- runtime storage `PROJECT_LOCAL_ONLY`;
- public KGM ingress not approved/deployed;
- production/live operational status `NOT_OPERATIONAL`.
