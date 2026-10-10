# KGM owner-only development threat model — 2026-09-28

**Owner decision (current development stage):** KGM has one authorized human user, the project owner. A malicious local human user / hostile multi-user threat model is **out of scope at this stage**. Do not spend development effort on simulated hostile co-tenants, malicious local user ACL attack scenarios or multi-human role management unless the owner explicitly changes this decision.

**This is a scope decision, not permission to weaken existing safeguards.** Continue testing accidental corruption, symlink mistakes, crash/restart recovery, concurrent KGM processes, permissions necessary for safe operation, secret hygiene, integrity/provenance, policy revocation and consumer-specific logical isolation. A single human owner does not imply a single process or eliminate accidental or external risks. Keep existing fail-closed controls; do not remove passing negative tests.

**Architecture boundaries remain:** no public ingress, no shared databases, no HP-OMEN, no K-Trader interaction until separately authorized, no real provider/release/production activation without owner approval. A future multi-user or external access phase must trigger explicit threat-model review before deployment.

**Roadmap adjustment:** remove adversarial-local-user resistance and hostile multi-user ACL certification from the current independent research readiness gate. Retain ordinary OS permission sanity checks and process-level concurrency/crash tests. Focus near-term work on unified durable typed processing, bounded automated recovery/expiry, verified actual source coverage when authorized, and synthetic acceptance.

Last confirmed isolated code validation: exact SHA `f1e7067b021106a8bac762bd97d6ebf72e7f9878`, 115/115 selected tests passed. This documentation-only scope change does not claim new code validation.
