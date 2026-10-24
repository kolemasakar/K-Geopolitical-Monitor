# KGM — S5 full-scope offline qualification and handoff
Date: 2026-10-24
Status: OWNER_AUTHORIZED_RESEARCH_ONLY / IMPLEMENTATION_IN_PROGRESS / PRODUCTION_NO_GO

## Authoritative starting point
Canonical main on entry: `413bb7e415202a5764d28057c754b8ef2a2539d4`. This supersedes the October 16 S4 snapshot. Main includes Phase 24.3/24.4 isolated owner pilot evidence and 2026-10-19 freeze/handoff. Do not roll state back to the earlier S4 plan. PR #215 roadmap proposal was already merged; PR #241 is a distinct DRAFT (CI success) for isolated release qualification, **not accepted in canonical main**. Preserve Phase 23 operational authority pointer independently from Phase 24 research gates.

## S5.0 Project and evidence freeze
- Preserve canonical commit, tested SHAs, native ARM64 and CI IDs from accepted evidence.
- Cross-check `ROADMAP.md`, `docs/state/CURRENT_PROJECT_STATE.json`, `docs/handoff/CURRENT_HANDOFF.md`, the 2026-10-19 freeze checkpoint, and the actual main tree.
- New exact-head tests are mandatory when code or environment changes; do not represent historic full suite as a new run.
- Keep `FREE_ONLY / NO_SEND / CLEANUP_HOLD / PRODUCTION_NO_GO`.

## S5.1 Runtime provenance and crash consistency
- Independently inspect read-only service/checkout/deployed SHA and explicit limitation that old loaded Python source cannot be retrospectively attested.
- On isolated snapshot only, qualify release directory safety, cooperative lock, concurrent writes, kill/failpoint immediately before/after atomic replacement, journal/SQLite reopen, and durable cursor semantics.
- Negative tests must cover torn files, symlink/hardlink/path escape, stale lock and interrupted fsync. Classify outcomes as PASS, SHORTFALL or NOT_RUN; never conflate synthetic SIGKILL with power-loss durability.
- Preserve owner-only P24.2-A accepted backup and independent restore evidence without performing any production restore, cleanup, live pause or switch.
- Respect historical 2026-10-19 bounded busy/forward rollback evidence; do not repeat full suites without changed dependency/code.

## S5.2 Ledger v1 ↔ v2 and release migration qualification
- Build an explicit read-only inventory of schema versions, migrations and artifact compatibility using synthetic or already-approved isolated snapshots only.
- Fail closed on irreversible or lossy conversion. Design code-only forward DB rollback and reverse-switch with fresh provenance; **never** restore a baseline backup over new forward-written data.
- Qualify manifest, source SHA, locked CPython/aarch64 environment, configuration references, runtime-root and file permissions. PR #241 is prior candidate work; review it, do not duplicate or auto-merge.
- Migration remains dry-run, runtime service untouched.

## S5.3 Consumer trust and source disagreement policy
- Design deny-by-default enrollment and independent permission checks for K-Sentinel/K-Trader but DO NOT connect either system.
- Source provenance; FULL/PARTIAL/UNKNOWN/UNVERIFIED; contradictions, TTL, replay cursor, duplicate IDs, cross-tenant rejection, and historical lookahead rules on fixtures.
- NO_SEND: no external network delivery, queue service, listener or new source activation; no credentials in commit history.

## S5.4 Final evidence, state sync and owner gate
- Record per-test exact HEAD, GitHub CI run, native ARM64 summary, dependency lock, tested host/architecture and failure classifications.
- Audit open PRs (#163, #202, #233, #234, #241 and relevant follow-ups) as accepted/deferred/superseded without automatic merge.
- Update canonical roadmap/state/handoff only after relevant gates are evidenced and CI completed.
- Final gate may be `S5_OFFLINE_PASS_WITH_KNOWN_LIMITATIONS`; production stays `NO_GO` until an independent explicit owner decision after fresh writer quiescence/checkpoint, loaded-code attestation, runtime resource enforcement and source/consumer approvals.

## Immediate execution ledger
| Work | State | Evidence |
|---|---|---|
| Current main, freeze, scoped P24.4 reconciling | PASS | main SHA above; 2026-10-19 handoff, canonical state |
| Prior accepted P24.4 release/writer/rollback qualification | HISTORICAL_ACCEPTED_WITH_LIMITATIONS | accepted docs in current main |
| PR #241 release shared boundary | CI_SUCCESS_DRAFT_NOT_MERGED | exact PR head; separate review required |
| S5.1 real critical-point crash/power-loss | NOT_RUN | must be isolated, no production |
| S5.2 complete v1/v2 cutover | NOT_RUN | dry-run only |
| S5.3 external authorization and delivery | NOT_RUN_NO_SEND | design and fixture tests only |
| S5.4 final comprehensive acceptance | OPEN | cannot claim closed |

This checkpoint is not a deployment plan, approval to execute production commands, or proof of power-loss-safe exactly-once delivery.

## Fresh bounded runtime read-only observation — 2026-10-24
- kgm-e4-owner-pilot architecture: `aarch64`.
- `systemctl is-active kgm-monitor.service`: `active`.
- `systemctl show`: `MainPID=125277`, `ExecMainStartTimestamp=Sat 2026-10-24 06:39:45 UTC`, `ActiveState=active`.
- Checkout via per-command git safe.directory override (no persistent configuration change): `b31b2136b5fe982d0b63b0135479b1549041906c`.
- First unprivileged `git rev-parse` attempt was denied by dubious ownership check; only the individual read-only command used `-c safe.directory=...`, no global trust override.
- **Runtime loaded-code provenance UNKNOWN**; checkout version alone is not loaded-code attestation. No restart or service mutation performed.
