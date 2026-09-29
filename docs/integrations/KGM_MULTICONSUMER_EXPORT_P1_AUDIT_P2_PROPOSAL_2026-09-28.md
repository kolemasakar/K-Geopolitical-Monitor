# KGM — P1 audit and P2 multi-consumer export architecture proposal
Date: 2026-09-28
Issue: #162
Coordinator: K_Sentinel (Sentinel-Remote PR #26)
Initial consumer: K-Trader News Impact Engine v0.1 (K-Trader PR #87)
Status: REVIEW CANDIDATE; code and canonical docs audited via GitHub; current VM/runtime not measured.
Scope: parallel KGM-owned integration work; no production activation, runtime mutation, shared canonical DB, or change in source/verification policy.

## Owner scheduling decision
Private ChatGPT Plugin migration (KGM draft PR #161) is **paused** at owner request. This independent multi-consumer export work takes priority. Do not merge the two changes or repurpose the owner-only Plugin as a cross-project bus. Retain the earlier mandatory private-Plugin direction for later resumption; this pause does not revoke it.

## P1 — Audited factual inventory (repository evidence only)
| Component | Repository implementation | Integrator assessment |
|---|---|---|
| Source collection | adapter_framework.py; live_sources.py; live_operational_cycle.py; source_health_egress.py | collectors/health model exist; current running collection status NOT_MEASURED in this session |
| Live event intelligence | live_end_to_end.py, semantic_live_compatibility.py | legacy live rows and semantic links require explicit unambiguous current P13.5 decision |
| Semantic verification | semantic_verification.py | DETECTED/PARTLY_VERIFIED/VERIFIED/DISPUTED/UNVERIFIABLE; eight distinct factual-confidence dimensions (no canonical scalar) |
| Provenance/contradiction | semantic_provenance.py; semantic_evidence.py; semantic_contradictions.py | existing evidence/origin models and contradiction lifecycle DETECTED/UNRESOLVED/EVOLVING/RESOLVED; never infer independent corroboration from host count |
| Forecast queries | forecast_query.py, advanced_forecasting.py, forecast_semantics.py | read-only AdvancedForecastQuery available; forecast probability, calibrated probability, scenario analytical confidence remain separate from facts |
| Source freshness | source_health_egress.py | UNMEASURED/HEALTHY/DEGRADED/STALE/UNAVAILABLE; freshness CURRENT/STALE/UNMEASURED; content FRESH/STALE/UNKNOWN |
| Existing public projection | public_safe_projection.py and publication_eligibility.py | verified/eligible public-safe subset only; **cannot** be full disputed/correction/forecast feed |
| Plugin MCP | branch PR #161 private_mcp_server.py | official MCP prototype exposes only owner `kgm_get_status`; not a K-Trader feed, no hosted access proven |
| Delivery | delivery_transport.py etc. | owner delivery primitives exist; no approved documented bounded multi-consumer export service established |
| Persistent service | canonical state/ROADMAP v4.66 | production_live NOT_OPERATIONAL, deployed public HTTPS NOT_APPROVED; bounded internal work cannot be extrapolated into a continuous reliable feed |

Primary administrative path: GitHub OIDC → Tailscale → SSH → Ansible. Existing `kgmops` has **no direct runtime DB-read permission**. This audit did not establish current availability via that path; RDC status is not app health. Actual source freshness, active forecasting, export artifacts, credentials, network reachability and running task schedule remain UNKNOWN until measured on the authorized KGM path.

## P2 — Proposed owned export boundary, version 1
Introduce a separate, **opt-in** read-only `KGMExportProjection` in KGM code. It reads *only* approved canonical read models under a dedicated KGM-local exporter identity explicitly granted least-privilege snapshot access by owner review. Existing `kgmops` never receives DB privileges. No database connection, query, internal file path, operator credentials, or raw private data crosses the project boundary.

**Recommended first transport candidate:** immutable bounded project-local JSONL batch files plus signed/checksummed manifest, synchronized by separately approved per-consumer read-only transport. The endpoint/artifact directory is **TBD until KGM owner chooses an approved local export area and permissions are tested**. An API/MCP adapter can later provide the same envelope without altering its version. No HTTP listener, public ingress, interproject shared volume or cross-project runtime dependency implied. KGM can produce/export without K_Sentinel continuously running; Sentinel arranges access and audits transfer. Consumers pull with their own credentials, offsets and local copies.

Canonical export records must preserve source model fields as-is, not synthesize certainty:
- Envelope: `schema_version=kgm.exchange.v1`, `batch_id`, `generated_at_utc`, `producer_snapshot_id`, `producer_code_sha`, `minimum_available_cursor`, `high_watermark_cursor`, `heartbeat`, `policy_version`, `records`; `records=[]` plus healthy heartbeat is distinct from unavailable feed.
- Per-record: `record_id`, `kind` (CLAIM_EVENT, CLAIM_REVISION, CLAIM_CORRECTION, FORECAST_VERSION, SOURCE_HEALTH), `change_type` (NEW, UPDATE, CORRECTION, HEARTBEAT), `entity_id`, `entity_version_id`, `recorded_at_utc`, `published_at_utc` when available, `ingested_at_utc` when available, `exported_at_utc`, `supersedes_record_id`, `retraction_state`, `language`, sanitized `content`, `provenance`, `verification`, `contradiction`, `forecast` and `source_health` as applicable.
- Provenance: publisher identity separate from immediate source, cited/quoted source and underlying origin; reference links are **publicly releasable** evidence pointers, never owner-private row identifiers. `origin_resolution=UNKNOWN`/unresolved preserved. Corroboration and independence only if recorded under canonical semantic policy; P23.3 zero-population limitations carried forward.
- Verification: `compatibility_state` and `canonical_verification_state` with canonical P13.5 decision/policy version and multidimensional confidence only if actually persisted/authorized for export. Never fall back to scalar legacy confidence or old host count, and never manufacture a K-Trader 0..1 value.
- Contradiction: explicit lifecycle, typed dimensions and resolution lineage; DISPUTED or UNRESOLVED never mapped to VERIFIED. Do not alter P13.5 truth authority.
- Forecast: independent kind with scenario/version/assumptions/input reference IDs, invalidation factors **only if actually recorded**, raw vs calibrated probability vs scenario_confidence distinct, outcome evaluation separate from ex-ante forecast; no BUY/SELL assertion.
- Source health: record last measured attempt/content freshness and their observation timestamps; `UNMEASURED`/missing feed is not equivalent to `healthy and zero events`.
- Licensing: only allowed public metadata and permitted references; not full raw licensed text. Every record has classification/redaction marker, and blocked records are omitted with aggregate bounded omission reason statistics (no sensitive identifiers).

**Projection safety rule:** export only explicitly allowlisted canonical fields and approved event classes. Unlike P17.2 public-safe projection, disputed and forecast classes need an **independent, versioned release policy and tests**; they must not bypass or broaden public publication eligibility. If policy is not approved, keep record `WITHHELD_POLICY` in aggregated stats and emit no sensitive payload.

## P3 — Separate transfer/access decision for Sentinel
For candidate batch transport, prefer owner-controlled private Tailscale/OIDC access to *export artifacts only*, not application DB or KGM host administration. Distinct read-only consumer identities, no shared root/GitHub/RDC/owner keys; revocation per consumer; deny path traversal; transfer audit includes consumer, batch digest, timestamp, status and cursor. Exporter ledger and manifest are local KGM-owned; sent copies are consumers' separate local storage. Define finite retention and replay bounds with explicit `CURSOR_EXPIRED` rather than unbounded promises. Atomic write/rename and checksum guarantee no partial batch. KGM export continues independently of Sentinel availability; failures must not block collection/analysis or execute trades. An eventual private API/MCP adapter must expose the *same versioned envelope*, only after separate review.

## P4 — Backward compatibility and development independence
- Separate `kgm.exchange.v1` schema from storage migrations; add optional fields only within v1; breaking semantics require v2 with overlap/deprecation period.
- Stable IDs and monotonic sequence per KGM export stream; per-consumer idempotent upsert keyed by record_id and version; correction lineage append-only.
- No backfill claim without measured historical provenance/receipt timestamps. As-of tests must exclude any revision received after decision cutoff.
- Per-consumer instrument/exposure mapping, severity and numeric policy confidence belong **solely** to K-Trader. No price, P&L or trading-action directives from KGM. Preserve geopolitical jurisdictions and structured event tags where evidence-backed.
- Multiple consumers subscribe through independent cursors/scopes and can be revoked separately; no multi-tenant KGM canonical storage.

## Initial acceptance matrix (offline fixtures, then measured host tests)
1. VERIFIED current semantic decision + independent provenance reference.
2. DISPUTED with UNRESOLVED contradiction and no numeric factual-confidence coercion.
3. Late correction and replacement preserving earlier as-of view and lineage.
4. Forecast scenario and updated version; distinguish probability, calibration and analytical confidence.
5. Degraded/stale/missing source vs healthy heartbeat with zero new records.
6. Unrelated asset and ambiguous exposure (leave consumer decision to K-Trader).
7. Wrong consumer token / expired cursor / absent manifest / corrupt hash / partial file / stale batch / unsupported schema.
8. KGM internal failure and Sentinel outage do not block original KGM processes.
9. Licensing/redaction and hidden secret/internal identifier regression tests.
10. Version compatibility: v1 old consumer accepts additive fields; intentional breaking change rejects until v2 negotiation.

## Staged plan and gates
- P1 document audit = REPO_AUDIT_COMPLETE / LIVE_RUNTIME_AUDIT_PENDING.
- P2 schema/specification = PROPOSED / NOT IMPLEMENTED; Sentinel and K-Trader to review the above mappings and policy.
- P3 transport = PROPOSED / NO CHANNEL DEPLOYED; obtain explicit network/credential approval before host writes.
- P4 compatibility = SPECIFIED / TESTS PENDING.
- **Next non-runtime step:** implement isolated typed v1 schema validator and synthetic fixtures in a separate KGM integration branch; test in disposable checkout. Do not connect real data until release policy and KGM-owned exporter permissions are validated.

Cross-project links: KGM #162; Sentinel PR #26; K-Trader PR #87. Strategic P23.4 stays unchanged; Plugin PR #161 explicitly paused and unchanged.
