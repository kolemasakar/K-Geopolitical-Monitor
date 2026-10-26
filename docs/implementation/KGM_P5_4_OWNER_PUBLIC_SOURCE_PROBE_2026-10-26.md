# P5.4 owner-only public source probe — preparation / acceptance

Date: 2026-10-26. Mode: `ON_DEMAND_ONLY`.

## Operational intent

A separate **manual** workflow `.github/workflows/p5-4-owner-public-source-probe.yml` allows owner `kolemasakar` to explicitly choose `YES` for three bounded HTTPS requests to fixed public GDACS, Consilium and GDELT endpoints. It runs only from `main` under `workflow_dispatch`, no scheduled or PR source polling. No production VM, service, SQLite, watch, consumer, messaging bot or token is accessed. No raw returned article/feed content or user query is deliberately printed. Output is aggregate source status, count and error class only.

Data retrieval uses the existing `RestrictedSourceTransport` for three allowlisted URLs, maximum three requests, per-request timeout 7 seconds, 512KB per source, no redirects or ambient proxies, no credential headers. GDELT query is URL-encoded and bounded; other endpoints fixed.

**Critical:** the GitHub-hosted runner uses normal external networking to fetch public endpoints. Application-level allowlisting is **not a host firewall / kernel-level egress guarantee**; malicious code or compromised dependencies could bypass it. Before declaring production-grade live access, require independent egress-boundary proof (proxy/firewall dedicated runner) and source-policy review. The runner's GitHub-context authorization is only for the project owner and not an external user-auth API.

## Acceptance taxonomy

- `PARSE_OK`: response returned and required XML/JSON container parsed; **does not mean current, relevant, or true geopolitical content**. A zero article count is still a successfully parsed response, not corroboration.
- `FAILED`: transport or parser failure, with class-only error identifier; do not present as an outage until failure cause independently checked.
- Three parsed responses = source-endpoint reachability, not comprehensive source provenance, upstream independence or an analyzed user report.
- GitHub workflow SUCCESS = collector and aggregate report executed, **not** three sources PASS: read `source_results`.
- `primary_claims_verified=false`; `provenance_validated=false`; `raw_data_persisted=false`; `report_sent=false`.

## Boundaries and next gates

1. CI tests for fake transport must PASS before merge.
2. Explicit **manual** owner trigger with `authorize_public_fetch=YES` after merge. This does not run automatically merely because PR is merged.
3. Review actual three-source output and classify `FULL/PARTIAL/SHORTFALL`.
4. For P5.5, implement original-source provenance checks, temporal freshness, deduplication, contradiction handling, reproducible evidence storage in separately approved isolated space, and report + Critic.
5. Never enable legacy watches or deploy to production as a substitute for an on-demand request.

FREE_ONLY / ON_DEMAND_ONLY / NO_SEND / CLEANUP_HOLD / PRODUCTION_NO_GO unchanged.
