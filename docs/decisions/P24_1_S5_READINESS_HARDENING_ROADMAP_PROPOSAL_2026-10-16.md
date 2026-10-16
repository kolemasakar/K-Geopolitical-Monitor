# P24.1 — S5 transition / strategic roadmap decision proposal
Date: 2026-10-16

**Status: PROPOSED / OWNER_DECISION_REQUIRED / NO_PRODUCTION_ACTIVATION.**

## Evidence baseline
- Canonical main after S4g checkpoint PR #214: `309981b8015546ed220ac0502d9f55efaa0db73a`.
- S3 offline typed-workflow/durable cursor accepted with limitations; production gate OPEN.
- S4 offline exchange slices S4a–S4g each CI PASS and independent ARM64 full regression PASS (last S4g #212: 1595/1595).
- S4f atomic ledger, S4g concurrency, torn-file restart, and symlink refusal tests are **local synthetic only**, not live infrastructure proofs.
- S5 handoff and state pointers synchronized in #207, #209, #214.
- No delivery, source activation or production rollout was approved.

## Decision recommended for next roadmap block
**S5 readiness hardening (RESEARCH_ONLY, FREE_ONLY)** before considering operational source/consumer activation.

1. **S5.1 security and reliability qualification:** isolated real multi-process SIGKILL/failpoint tests around fsync, replacement, lock ownership; malformed/corrupt ledger, symlink/hardlink/path-race checks. No runtime cutover.
2. **S5.2 ledger schema migration study:** plan backwards compatibility of ledger-v1 and ledger-v2 using synthetic fixtures, no transformation of live data.
3. **S5.3 consumer authorization design:** define deny-by-default enrollment for K-Sentinel/K-Trader, independent provenance and source permission gate. Contract-only; no external send.
4. **S5.4 audit & handoff:** exact-head CI, native ARM64 acceptance, owner-pilot permissions, roadmap/state/handoff consistency; preserve the distinction between research and production gates.
5. **Owner go/no-go** required before any network listener/export, source activation, external consumer enrollment or live service deployment.

## Deferred risks
- Exactly-once effect cannot be guaranteed across remote consumer writes by local ledger tests alone.
- Live crashes during the critical fsync and lock transitions are unverified.
- Consumer credentials, authorization, live source corroboration and cross-project trust not established.
- Separate historical owner-pilot deployment SHA has not been re-attested to these research merges.

## Constraints
No paid infrastructure, HP-OMEN, KRC/K-Trader shared resources, production deploy, automatic export, source admission, or unapproved runtime mutation.

Decision gate: `P24_1_S5_STRATEGIC_PROPOSAL_OWNER_REVIEW_REQUIRED`.
