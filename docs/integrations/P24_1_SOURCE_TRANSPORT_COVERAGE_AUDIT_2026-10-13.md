# P24.1 — Bounded Source Transport and Coverage Audit

Date: 2026-10-13
Status: **P24.1 IN PROGRESS** (transport assessment only; functional parser and provenance validation pending)
Implementation reference: PR #163 `f135014e2962907c76ea14bf3b10ddc7c288046c`.

## 11 dedicated adapter inventory

| Adapter/source | Region or domain | HTTPS transport status | Evidence acceptance |
|---|---|---|---|
| `consilium-press-releases` | EU diplomacy/politics | 200, previous bounded test | parser/current data not checked |
| `germany-federal-government` | German government | 200, Oct 13 landing page | parser/current data not checked |
| `france-presidency` | French presidency | 200, Oct 13 landing page | parser/current data not checked |
| `govuk-official` | UK government | 200, Oct 13 FCDO landing page | parser/current data not checked |
| `moldova-mfa` | Moldovan foreign ministry | 200, Oct 13 landing page | parser/current data not checked |
| `nato-news` | NATO defence/diplomacy | 200, previous NATO home page test | parser/current data not checked |
| `ecb-press` | eurozone monetary policy | 200, previous RSS probe | parser/current data not checked |
| `gdacs-events` | global disasters | 200, previous SEARCH API probe | parser/current data not checked |
| `usgs-earthquake` | global earthquake events | 200, previous FDSN version probe | parser/current data not checked |
| `gfz-geofon` | global earthquake events | 200, previous FDSN version probe | parser/current data not checked |
| `gdelt-doc-v2` | global media discovery | **TLS handshake timeout**, Oct 13 | transport degraded, not accepted |

### Evidence and limits
- On Oct 13 the owner-pilot VM performed 5 additional bounded read-only HTTPS requests: 4 returned 200 (Germany, France, GOV.UK, Moldova MFA), and GDELT raised TLS handshake timeout. Requests used no credentials or paid provider.
- Six earlier requests to Consilium, ECB, NATO, GDACS, USGS and GFZ were 200; **those are earlier probes**, not a simultaneous Oct 13 health snapshot.
- Aggregated observational tally 10 positive HTTP probes and 1 failed probe, **not** 10 validated functional source integrations.
- GDELT has pre-existing cooldown/rate-limit history; this timeout does not establish current upstream outage, and no unbounded retries are authorized.
- `gdacs-events` and `usgs-earthquake` can refer to common `usgs-neic` earthquake origin. Different feeds and URLs are not independent proof.
- Political official-source coverage is Europe/NATO-heavy, with weak dedicated official adapters for Africa, Middle East, Asia and Americas. This is a *code inventory observation*, not a quantitative global coverage percentage.
- Source reputations, official status, and source origin are distinct from proof of assertions in their content.

## Immediate engineering acceptance targets
1. Inspect adapter input contracts and create deterministic local fixtures representing success, empty, malformed, 429/cooldown, HTTP timeout/TLS failure, and missing timestamps.
2. Extend explicit mapping profiles only for controlled known event/claim cases; negative tests for false merge and false independent-origin promotion.
3. Run independently attributed source pairs and same-origin replication comparisons; preserve `UNVERIFIED` when factual validation unavailable.
4. Capture UTC event and publication timestamps separately and report missing/unknown coverage.
5. Complete isolated ARM64 research regression and GitHub CI before promoting a code or source-specific gate.

## Constraints
No new live source activation, unattended scheduling, production deployment, public publication, paid/shared infrastructure or cross-project integrations.
