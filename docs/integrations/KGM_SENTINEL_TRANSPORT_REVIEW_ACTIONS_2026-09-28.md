# KGM response to Sentinel transport/security contract v0.1

Date: 2026-09-28
Reference: Sentinel-Remote `docs/integrations/KGM_KTRADER_TRANSPORT_SECURITY_AND_ACCEPTANCE_V0_1.md` in PR #26; KGM issue #162, draft PR #163; K-Trader draft PR #87.
Status: DESIGN ACCEPTED AS CANDIDATE / LIVE EXPORT NOT APPROVED / TRANSPORT NOT DEPLOYED.

## Agreed boundaries
- Keep owner control plane OIDC -> ephemeral Tailscale -> SSH kgmops -> bounded Ansible separate from per-consumer transport. Existing kgmops has no DB read permission, unchanged.
- Adopt zero-cost candidate: immutable KGM-owned export artifacts, restricted dedicated K-Trader SFTP or read-only rsync identity over private Tailscale, separate peer identity and host-key verification. Tailscale candidate node `100.102.136.23` is historical observed address only, not independently tested consumer reachability.
- K-Trader owns normalized impact policy, instrument mapping and local staging. No shared DB, public ingress, paid relay, shared credentials or Plugin transport reuse. Plugin PR #161 remains paused.
- Exports of DISPUTED, corrections and forecasts remain blocked until explicit KGM-owned versioned release policy and field licensing/redaction review. Schema validation is not release permission. Canonical P13.5 verification semantics unchanged.

## KGM P2 corrections and execution priority
1. Fix current two-file publication race: implement generation-directory staging, fsync files + directory, write completion marker last, atomically rename complete generation directory to final `batch_id` path, fsync parent. Reader accepts only exact manifest, digest, length and completion marker. Unfinished staging never visible. Crash after publish but before response is replay-idempotent by matching manifest digest. Document same-filesystem guarantee and local POSIX assumptions.
2. Separate field classification/release policy from validator. A strict v1 validator rejecting unknown keys is intentional pre-v1 freeze, but cannot be described as additive forward compatibility. Amend published v1 contract only with explicit compatible-field version; incompatible changes require v2 negotiation.
3. Define stream sequence and cursor semantics: KGM-owned monotonically ordered sequence; independent consumer cursor; bounded retention, explicit CURSOR_EXPIRED on missing history; no silent skip or inferred healthy feed from empty batch.
4. Validate negative cases: interrupted staging, corrupt payload, missing manifest/marker, wrong/duplicate cursor, private/symlink path, stale heartbeat, disputed claim, forecast distinction, late correction, prohibited fields.
5. Handoff the exact artifact reader specification and a synthetic fixture to Sentinel and K-Trader. Do not provision consumer keys, deploy listeners or schedule real feeds until independent security and owner authorization gates.

## Audited baseline
On 2026-09-28 authorized KGM RDC observed active `kgm-monitor.service` and the unattended runner; source ingestion, analysis and forecast output were NOT_MEASURED without authorized read access. Exact SHA `515aa4b993e6b6b15b4b7f27d6e29c15e5e91805` validated existing 21 synthetic tests before this decision document. These tests do NOT establish live export readiness. Preserve measured limitations and maintain Phase 23 strategic gates.
