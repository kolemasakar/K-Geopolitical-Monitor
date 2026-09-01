# E9A.6 Validation Matrix Result

Status: `OWNER_ONLY_PRODUCTION_CANDIDATE_READY`
Date: 2026-09-01
Project: K-Geopolitical Monitor
Workstream: E9A — Owner-Only Production Runtime Hardening
Runtime storage: `PROJECT_LOCAL_ONLY`
Production/live: `NOT_OPERATIONAL`

## 1. Decision

The E9A.6 validation matrix is complete for the owner-only production-candidate engineering gate.

`E9A.6_VALIDATION_MATRIX = PASS`

`OWNER_ONLY_PRODUCTION_CANDIDATE_READY = ESTABLISHED`

This classification is an engineering readiness state only. It does **not** authorize or establish production/live operation, public ingress, shared runtime storage, Business migration, GPT publication/public sharing, a public API/dashboard, or E9 Shared Production Runtime.

`PRODUCTION_LIVE = NOT_OPERATIONAL`

## 2. Final Regression Anchors

### x64

Canonical restored-tree validation:
- commit: `611e6071a2d0f9e9f84392ddd27edaf8c38d0b38`;
- Git tree: `0bdfde547e756dcbf9ac3c9c84347c84be41574e`;
- workflow: `CI`;
- run ID: `33502510214`;
- job ID: `99838870836`;
- result: `SUCCESS`;
- full regression: `318 passed, 1 warning`.

### native ARM64

Canonical restored-tree validation:
- commit: `611e6071a2d0f9e9f84392ddd27edaf8c38d0b38`;
- Git tree: `0bdfde547e756dcbf9ac3c9c84347c84be41574e`;
- workflow: `E4 ARM64 Validation`;
- run ID: `33502510195`;
- job ID: `99838870759`;
- runner image: `ubuntu-24.04-arm`;
- observed architecture: `aarch64`;
- result: `SUCCESS`;
- full regression: `318 passed, 1 warning`;
- ARM64 bootstrap shell validation: PASS;
- unattended one-tick smoke: PASS;
- `systemd-analyze verify`: PASS.

A reversible workflow-comment trigger was used because the available connector did not expose a workflow-dispatch action. The comment was then removed. The restored commit `611e6071...` and the rpcbind-hardening commit `fa514214b9510af6ecb2a35887ec16f15f73adf0` have the same Git tree SHA `0bdfde547e756dcbf9ac3c9c84347c84be41574e`; therefore the trigger did not leave a repository-tree change.

## 3. Real OCI Validation

State-preserving real-host validation:
- workflow run ID: `33486944907`;
- job ID: `99789127086`;
- result: `SUCCESS`;
- host: owner-only OCI Ubuntu 24.04 ARM64;
- observed architecture: `aarch64`.

Validated on the real host:
- immutable/state-preserving deployment: PASS;
- pre-change online SQLite backup and integrity: PASS;
- effective hardened systemd boundary: PASS;
- exact application writable path limited to `/opt/k-geopolitical-monitor/data`: PASS;
- root-owned code/unit and `kgm:kgm` runtime identity: PASS;
- second-instance lease rejection: PASS;
- normal service restart: PASS;
- SQLite integrity after restart: PASS;
- emergency stop/disable/re-enable recovery: PASS;
- deterministic interrupted-run preparation: PASS;
- physical reboot: PASS;
- changed boot ID after reboot: PASS;
- interrupted run recovery: PASS;
- due-watch resumption: PASS;
- resumed run completion: PASS;
- service active/enabled after reboot: PASS;
- controlled live collection success observed after recovery: PASS;
- journal secret-pattern review: `0` hits.

The host-side validator correctly reports that cloud-firewall state is not inferable from the host itself. OCI perimeter evidence is retained separately from the prior E4 real-host validation: inbound 80/443 and database/API ingress were absent; TCP/22 remained the explicit owner-approved public administrative exception.

## 4. Backup / Disaster-Recovery Validation

Real clean-project-root DR drill from run `33486944907`:
- backup bundle format: `KGM_RUNTIME_BACKUP_V1`;
- bundle verification: PASS;
- manifest source commit validation: PASS;
- canonical storage policy in manifest: `PROJECT_LOCAL_ONLY`;
- restored SQLite integrity: PASS;
- restored table count: `51`;
- source/restored table counts: identical;
- one-tick execution from restored project root: PASS;
- integrity after restored one-tick: PASS;
- measured drill recovery elapsed time: `1 second`;
- measured recovery-point age at evaluation: `0.000 seconds`;
- RTO engineering objective `<= 2h`: PASS for this drill;
- RPO engineering objective `<= 24h`: PASS for this drill.

These measurements are validation-drill evidence only. They are **not** an operational SLA or guarantee.

No off-host backup provider was activated.

## 5. rpcbind / Port 111 Disposition

Real-host remediation:
- workflow run ID: `33488954688`;
- job ID: `99795604234`;
- result: `SUCCESS`.

Before mutation the gate established:
- `rpcbind` was the owner of TCP/UDP port `111`;
- no NFS server dependency was present;
- NFS mounts: `0`;
- NFS `/etc/fstab` entries: `0`;
- no required non-portmapper RPC program was registered.

Remediation and reboot validation:
- `rpcbind` disabled/masked: PASS;
- physical reboot: PASS;
- `rpcbind` remained masked/inactive after reboot: PASS;
- TCP/UDP port `111` did not return: PASS;
- `kgm-monitor.service` active/enabled after reboot: PASS;
- canonical SQLite integrity after reboot: `ok`;
- host public listener surface after remediation: TCP/22 only.

The canonical ARM64 bootstrap now fails closed on detected NFS dependency before applying the rpcbind hardening, so the host cleanup is also represented in future deployment behavior.

## 6. Validation Matrix

| Required E9A.6 gate | Result | Primary evidence |
| --- | --- | --- |
| Full x64 regression | PASS | run `33502510214`, `318 passed, 1 warning` |
| Full native ARM64 regression | PASS | run `33502510195`, native `aarch64`, `318 passed, 1 warning` |
| Real OCI immutable/state-preserving deployment | PASS | run `33486944907` |
| Second-instance lease rejection | PASS | real-host validation |
| Normal service restart | PASS | real-host validation |
| Physical reboot recovery | PASS | real-host validation and rpcbind remediation reboot |
| Interrupted-run recovery | PASS | real-host validation |
| SQLite integrity after restart/reboot | PASS | real-host validation and rpcbind remediation |
| Backup integrity | PASS | online backup + bundle verification |
| Clean project-local restore drill | PASS | restored 51-table DB, one-tick smoke, integrity PASS |
| RPO/RTO engineering-objective evaluation | PASS | drill: 0.000 s recovery-point age / 1 s recovery elapsed |
| Controlled live execution/recovery | PASS | retained E4 real-host baseline plus E9A.6 live collection observed after reboot recovery |
| Source/runtime failure visibility | PASS | full regression plus deterministic interrupted-run recovery evidence; no failure converted to success |
| No public-web substitution for persisted backend state | PASS | retained epistemic regression/invariant |
| E3/E5 read-only non-mutation behavior | PASS | full x64/native ARM64 regression |
| Provenance/verification/coverage/forecast/report isolation | PASS | full x64/native ARM64 regression; unchanged semantic invariants |
| No shared/mixed canonical runtime storage | PASS | `PROJECT_LOCAL_ONLY`; DR bundle and restored path preserve policy |
| No new KGM public ingress | PASS | no HTTP/HTTPS/database/API listener; port 111 removed; TCP/22 is the explicit owner administrative exception |
| Real-host security hardening evidence | PASS WITH EXPLICIT OWNER EXCEPTIONS | systemd/journal/listener/rollback/reboot evidence plus retained OCI perimeter evidence |

## 7. Explicit Owner-Approved Candidate Exceptions

The following exceptions remain deliberately visible:

- `PUBLIC_SSH_TCP_22_FROM_0_0_0_0_0 = OWNER_ACCEPTED_FOR_OWNER_ONLY_CANDIDATE`;
- `BROAD_OUTBOUND_EGRESS = OWNER_ACCEPTED_FOR_OWNER_ONLY_CANDIDATE`.

They remain security exceptions and must not be silently reclassified as least-privilege production networking. They do not authorize public KGM application ingress.

Port `111` is **not** a remaining exception; it was removed and its persistent closure was validated after physical reboot.

## 8. Preserved Architecture / Truth Boundaries

The candidate gate preserves:
- one canonical project-local runtime database;
- no shared/mixed canonical storage;
- publisher/publication is not automatically the underlying origin;
- repost/syndication/translation/citation does not create independent corroboration;
- an official statement proves `actor said X`, not automatically `X happened`;
- source reputation does not automatically determine truth of every new claim;
- graph inference cannot promote factual verification or independent-origin count;
- forecast probability/confidence cannot promote present-tense factual verification;
- coverage confidence cannot promote factual verification confidence;
- GLOBAL remains intended scope, not proof of exhaustive coverage;
- exact tool/search history is never reconstructed and labeled exact;
- public-web research is never substituted for unavailable persisted backend state;
- runtime-health instrumentation cannot imply unavailable coverage, source-health, uptime, verification, or production facts.

## 9. Final E9A Gate

`E9A_OWNER_ONLY_PRODUCTION_RUNTIME_HARDENING = OWNER_ONLY_PRODUCTION_CANDIDATE_READY`

`OWNER_ONLY_PRODUCTION_CANDIDATE_READY = ESTABLISHED`

`PRODUCTION_LIVE = NOT_OPERATIONAL`

`E9_SHARED_PRODUCTION_RUNTIME = NOT_APPROVED`

`BUSINESS_MIGRATION = HOLD_UNTIL_SEPARATE_OWNER_REQUEST`

`GPT_PUBLICATION_OR_PUBLIC_SHARING = HOLD_UNTIL_SEPARATE_OWNER_REQUEST`

Any transition from this engineering candidate state to production/live operation requires a separate explicit owner launch decision and a launch-specific gate. No such launch decision is recorded by this result.
