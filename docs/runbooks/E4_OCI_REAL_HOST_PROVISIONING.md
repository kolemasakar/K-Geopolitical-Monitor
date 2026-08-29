# E4 OCI Real Host Provisioning Runbook

Status: READY_FOR_MANUAL_PROVISIONING
Project: K-Geopolitical Monitor
Target: Oracle OCI Always Free Ampere A1 owner-only pilot
Deployment model: manual VM provisioning -> GitHub Actions SSH deployment -> automated reboot/recovery validation
Runtime status until evidence completes: NOT_DEPLOYED / NOT_OPERATIONAL

## 1. Safety Boundary

This runbook provisions only the E4 owner-only unattended monitoring pilot.

It does not:
- expose the E3 Action API;
- open HTTP/HTTPS listeners;
- create a shared runtime database;
- enable public GPT access;
- upgrade production/live status by wording alone.

Never paste the SSH private key into ChatGPT, an issue, a commit, a workflow file, or repository content.
Store it only in the GitHub Actions secret named `E4_SSH_PRIVATE_KEY`.

## 2. OCI VM Configuration

Create the instance manually in the OCI Console:

- Compute -> Instances -> Create instance
- suggested name: `kgm-e4-owner-pilot`
- image: Ubuntu 24.04 LTS, standard Canonical Ubuntu Arm/aarch64 image
- do not select Minimal Ubuntu for this E4 baseline
- shape series: Ampere
- shape: `VM.Standard.A1.Flex`
- OCPU: 1
- memory: 6 GB
- boot volume: default is sufficient for the pilot
- assign a public IPv4 address
- SSH key: add or generate a dedicated E4 key pair
- default SSH user for the Ubuntu platform image: `ubuntu`

The selected 1 OCPU / 6 GB profile stays within the documented Always Free A1 aggregate limit.

## 3. OCI Network Policy During Validation

The unattended monitoring runtime needs outbound HTTPS access for approved source adapters.
It does not need inbound HTTP/HTTPS.

For the validation window:

- allow inbound TCP 22 so the GitHub-hosted runner can reach SSH;
- do not add inbound TCP 80;
- do not add inbound TCP 443;
- do not expose SQLite or any database port;
- keep normal outbound HTTPS access.

GitHub-hosted runner source IPs are not a single stable address. For the short validation window, an owner may temporarily allow SSH/22 from a broader source CIDR if required. After validation, restrict SSH/22 to the owner's administration source or remove public SSH access according to the maintenance plan.

The GitHub workflow does not claim to verify the OCI Security List/NSG from inside the host. That remains an explicit external-cloud-firewall evidence item.

## 4. First Trusted SSH Connection

After OCI reports the instance RUNNING, note its Public access IP address.

From a trusted local machine, connect once:

```text
ssh -i <private-key-file> ubuntu@<public-ip>
```

Verify the host is the newly created OCI instance before accepting its SSH host key.

Then produce a pinned known-hosts entry for GitHub Actions:

```text
ssh-keyscan -H <public-ip>
```

The resulting line is stored as the GitHub secret `E4_SSH_KNOWN_HOSTS`.

Do not disable SSH host-key checking in the workflow.

## 5. GitHub Actions Secrets

Repository:
`kolemasakar/K-Geopolitical-Monitor`

Open:
Settings -> Secrets and variables -> Actions -> New repository secret

Create exactly:

- `E4_HOST`
  - value: OCI instance public IPv4 address
- `E4_SSH_PRIVATE_KEY`
  - value: complete private key corresponding to the public key installed on the VM
- `E4_SSH_KNOWN_HOSTS`
  - value: trusted `ssh-keyscan -H <public-ip>` output captured after the first trusted connection

The workflow intentionally hardcodes the target Ubuntu SSH user as `ubuntu`.

## 6. Automated Workflow

Workflow:
`.github/workflows/e4-real-host-validation.yml`

Launch manually:
Actions -> E4 Real Host Validation -> Run workflow

Input:
- `deploy_ref`
  - blank: deploy the commit from which the workflow is launched
  - optional: exact commit/ref to validate

The workflow is fresh-host only.
It fails if `/opt/k-geopolitical-monitor` already exists.

Automated sequence:

1. validate required GitHub secrets;
2. verify Ubuntu 24.04 and native `aarch64`;
3. verify passwordless `sudo`;
4. verify the target project root does not already exist;
5. clone the public repository;
6. resolve and deploy an immutable commit SHA;
7. run `deployment/scripts/e4_bootstrap_ubuntu_arm64.sh`;
8. run the pre-reboot host gate;
9. prepare a deterministic interrupted `RUNNING` monitoring run;
10. stop the service;
11. issue a real host reboot;
12. wait for pinned SSH connectivity to return;
13. verify changed Linux `boot_id`;
14. verify `systemd` auto-start;
15. verify interrupted-run recovery;
16. verify due-watch resumption;
17. run the final host runtime gate;
18. collect E4 validation JSON evidence as a GitHub Actions artifact.

## 7. Expected Evidence

Successful workflow evidence must show:

- deployed immutable commit SHA;
- host `aarch64`;
- Ubuntu 24.04;
- service enabled and active;
- service account `kgm`;
- project root `/opt/k-geopolitical-monitor`;
- project-local SQLite integrity `OK`;
- no public HTTP/HTTPS listener;
- changed `boot_id`;
- prepared interrupted run recovered as `FAILED` with recovery marker;
- reboot sentinel watch resumed;
- final host gate PASS.

The workflow artifact is named:
`e4-host-evidence-<deploy-sha>`

## 8. External Firewall Gate

After the workflow passes, verify manually in OCI that:

- inbound 80 is absent;
- inbound 443 is absent;
- no database port is exposed;
- SSH 22 is restricted or removed after the GitHub validation window;
- only expected outbound monitoring traffic is required.

Do not close E4 solely from host workflow success.
The OCI Security List/NSG state must be recorded separately because the host cannot prove the cloud perimeter policy.

## 9. Failure Handling

If the workflow fails before `/opt/k-geopolitical-monitor` is created:
- correct the VM/SSH configuration and rerun.

If it fails after the project root is created:
- do not delete the directory or database automatically;
- inspect the workflow logs and host state;
- preserve `data/` evidence;
- either repair under an explicit reviewed procedure or recreate the disposable E4 pilot VM.

The workflow deliberately refuses an implicit overwrite/redeploy.

## 10. Completion Boundary

Until both the automated host gate and the manual OCI firewall gate are evidenced:

- E4: `REAL_HOST_GATE_PENDING`
- unattended cloud runtime: `NOT_DEPLOYED`
- production/live: `NOT_OPERATIONAL`

No Phase 12 or M14 is created by this runbook.
