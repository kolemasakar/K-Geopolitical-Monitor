# P12.3 — Controlled-Live Authoritative Source Matrix

Date: 2026-09-01
State: `EVIDENCE_CAPTURED / PARTIAL_SOURCE_AVAILABILITY`
Implementation commit under probe: `dbeed606db6d07602b0a17d86c30838afd8a4213`
Workflow: `P12.3 Controlled Live Source Smoke`
Run: `33527134432`
Job: `99920724311`
Checked at: `2026-09-01T15:40:17.588524+00:00`

## Purpose

Capture real read-only P12.2 adapter execution against the P12.3 public authoritative endpoints. This matrix measures acquisition/parser availability only. It is not evidence of factual truth, independent-source count, exhaustive coverage, production readiness or continuous uptime.

## Results

| Source | Adapter | Endpoint | Result | Parsed items | Interpretation |
| --- | --- | --- | --- | ---: | --- |
| European Commission Press Corner | `ec-presscorner-rss-atom@P12.2-2.0` | `https://ec.europa.eu/commission/presscorner/api/rss` | `SUCCESS` | 1 | HTTPS acquisition and feed parsing succeeded for the probe query. |
| European Parliament Press Releases | `ep-press-releases-rss-atom@P12.2-2.0` | `https://www.europarl.europa.eu/rss/doc/press-releases/en.xml` | `FAILED / DEGRADED` | 0 | Endpoint is official/current, but the unattended runner received anti-bot HTML rather than XML; P12.2 parser correctly failed closed. |
| UK Government News and Communications | `govuk-news-atom@P12.2-2.0` | `https://www.gov.uk/search/news-and-communications.atom` | `SUCCESS` | 0 | HTTPS acquisition and Atom parsing succeeded; zero query matches is not a transport/parser failure. |
| OSCE Latest News | `osce-latest-rss-atom@P12.2-2.0` | `https://feeds.osce.org/OSCELatestNews` | `SUCCESS` | 7 | HTTPS acquisition and feed parsing succeeded for the probe query. |

Overall probe state: `PARTIAL`

- source successes: `3`;
- source failures: `1`;
- failure isolation: `PASS`;
- failed source: `eu-parliament-press-releases`;
- failure class: `RuntimeError / feed payload is not valid XML`.

## European Parliament Diagnosis

The European Parliament's current official RSS directory still lists `Press releases - All (XML)` and resolves it to the configured endpoint. A direct retrieval surface shows an anti-bot interstitial requiring JavaScript rather than the RSS XML. Therefore the configured URL is retained as the official endpoint, but unattended RSS availability is governed as `DEGRADED` instead of being silently replaced by a third-party mirror.

## Governance Consequence

P12.3 pack governance must reflect:

- European Commission: `ACTIVE`;
- European Parliament: `DEGRADED`;
- GOV.UK: `ACTIVE`;
- OSCE: `ACTIVE`.

`DEGRADED` is an operational availability state accepted by the P12.2 framework; it does not downgrade or upgrade the truth value of claims from the institution. It also does not authorize bypassing anti-bot controls.

## Epistemic / Coverage Boundary

- 4 configured publishers are not 4 independent underlying origins;
- official publication confirms what the institution published/stated, not automatically the underlying event;
- parsed item count is not coverage completeness;
- a successful one-time probe is not continuous uptime evidence;
- a failed probe is not evidence that the institution did not publish relevant information;
- no web mirror or repost is substituted for the official endpoint as canonical evidence.

## Runtime / Security Boundary

- read-only HTTPS only;
- public anonymous endpoints only;
- no credentials;
- no paid provider;
- no public KGM ingress;
- runtime storage remains `PROJECT_LOCAL_ONLY`;
- production/live operational status remains `NOT_OPERATIONAL`.
