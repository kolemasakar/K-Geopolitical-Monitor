# KGM private owner-only Plugin — interface and security design v0.1

Status: DESIGN CANDIDATE / NOT DEPLOYED / NO PUBLIC INGRESS. Date: 2026-09-25.

## Decision and sequence
1. Build and validate a **private owner-only** KGM ChatGPT Plugin before considering public deployment.
2. KGM continues collecting and storing canonical data on its own owner-local VM independently of ChatGPT and RDC.
3. Public API, shared user accounts, public plugin publication and paid services remain out of scope until separate owner authorization after project development.

## Proposed minimal read-only interface (not yet implemented)
- `kgm_get_status`: sanitized service/collection health, source freshness, last completed acquisition timestamp, explicit unknown/uninstrumented states; no raw credentials, host secrets or arbitrary logs.
- `kgm_get_brief`: bounded geopolitical brief by period, geography and theme, with item timestamps, source attribution and uncertainty. Never invent unavailable persisted state.
- `kgm_get_events`: bounded, paginated geopolitical event search by time/geography/topic, preserving provenance and factual-verification distinctions.
- `kgm_get_evidence`: bounded evidence/source/claim inspection for an event, with independence and corroboration status only when persisted and instrumented.

Read-only v0.1 explicitly excludes shell, SQL, arbitrary filesystem, sudo, restarts, deployments, source activation, scheduling, publication, shared accounts, and cross-project resources. Event-specific watch operations require a later separate owner-approved design; no default five-minute polling.

## Authentication and connectivity acceptance
- Owner-only plugin visibility, no sharing/public marketplace publication.
- Independently authenticated backend access with owner identity verified **server-side on every request**, explicit tool allowlist, bounded response sizes, rate limits and audit logs without secrets.
- RDC credentials, device pairing and refresh token are **not** plugin authentication and are never passed to the plugin.
- Avoid directly exposing the canonical database or unrestricted host endpoints. Use a separate narrow read-only adapter and non-privileged runtime identity; evaluate secure supported connector reachability before deployment.
- No cross-project credentials or shared canonical runtime. Free-only provider/resource policy, with explicit cost/quotas review.
- Private plugin visibility **does not itself make its backend private**. Any needed internet-reachable endpoint, gateway, authentication method and network policy are a distinct owner approval gate. Do not deploy a public unauthenticated API as a shortcut.

## Read-model semantics
- Existing KGM P13.5/P13.6 truth and provenance policy remains authoritative; source health and coverage are not factual verification.
- Preserve `UNKNOWN`, `NOT_OBSERVED`, stale, unavailable and zero corroboration without silent upgrades.
- Return sanitized timestamps and evidence identifiers; no internal secrets, raw DB dumps or administrative metadata.

## Implementation gates
A. Inspect current repository read models and runtime boundaries; map four proposed tools to existing **real** functions and identify missing functions. No synthetic endpoints.
B. Produce a deterministic local/test adapter and security tests: deny unauthorized caller, deny unlisted tool, bounded query, no raw DB access, no RDC dependency, secret redaction, evidence integrity.
C. Independently validate KGM service and acquisition continuity without RDC using the approved owner SSH route. Current observation: KGM system service active with zero restarts across an observed RDC offline interval; acquisition continuity remains unverified.
D. Select supported private Plugin integration and authenticated transport based on available product capabilities, then seek owner approval before introducing ingress, credentials or network changes.
E. Create private personal/local Plugin, test owner-only read paths and error handling. No public deployment or activation implied by this design.

## Existing access evidence
- Primary bounded admin workflow in `.github/workflows/tailscale-kgm-control.yml` does not use RDC, but GitHub Actions unavailable until 2026-10-01; it is not an available live test path during this window.
- Owner SSH was verified directly; on-demand watchdog recovered RDC from a persisted session. Revoked-token unattended reauthorization remains unsupported/unverified.
