# KGM P23.4 — Dedicated non-Ukraine Free VPN node (NOT provisioned)

Status: `REPOSITORY_PREPARED / OCI_TENANCY_PREFLIGHT_REQUIRED / NO_PROVIDER_MUTATION`.
Scope: `government.ru` source only. Architecture is a **WireGuard peer + exact-host HTTPS CONNECT relay**. It is intentionally not a host-wide Tailscale exit node: ordinary KGM, Docker, SSH, other sources, and default routing must remain unchanged.

## Cost and account boundary

- Use an **authorized existing, separate, independently eligible** Oracle Cloud Always Free tenancy. An existing family-owned tenancy may be used only with that account owner's permission. Do not create duplicate accounts to evade quotas.
- Must deploy in that tenancy's actual **Home Region outside Ukraine**. Frankfurt (`eu-frankfurt-1`) is a candidate only if it is genuinely its Home Region; never switch to a paid or trial-credit-funded foreign region.
- Default: one NEW `VM.Standard.E2.1.Micro` (AMD, 1 GB RAM) with free-eligible Ubuntu image and **50 GB** boot, free-eligible public IPv4. Choose this only if console inventory confirms fewer than two existing free E2 Micro instances AND at least 50 GB free in the 200 GB combined boot/block allowance.
- Fallback ONLY if owner explicitly selects: new `VM.Standard.A1.Flex` 1 OCPU / 2 GB and 50 GB boot, *within* 2 OCPU/12 GB combined Always Free A1 tenancy envelope and the same storage budget. Never use paid bursts.
- OCI Always Free outbound allowance is shared at tenancy scope; verify ongoing usage. OCI can reclaim continuously idle Always Free VMs; treat that as an availability limitation rather than generating artificial CPU load.
- Absolutely no Pay-As-You-Go upgrade, paid subnet NAT gateway, paid load balancer, marketplace VPN, paid backup, paid static IP assumptions or sharing KRC/K-Trader production machines. If console does not explicitly show Always Free eligibility and capacity: **STOP**.
- This preparation has not created, changed, reserved or paid for cloud resources. `oci_free_guard.py` audits a **locally populated** inventory template; it does not call OCI or handle credentials.

Provider policy references:
- https://docs.oracle.com/en-us/iaas/Content/FreeTier/freetier_topic-Always_Free_Resources.htm
- https://docs.oracle.com/en-us/iaas/Content/FreeTier/freetier.htm

## Network / application architecture

```text
 KGM owner node (existing; DEFAULT ROUTE UNCHANGED)
  `government.ru` source-specific HTTPS transport ONLY
     | HTTP CONNECT government.ru:443 via 10.254.90.1:18180
     | WireGuard wg-kgm-govru 10.254.90.2/32, peer AllowedIPs=10.254.90.1/32
     | UDP/51820 (encrypted) --> new EU Always Free VM public IP
 NEW independent, project-only EU OCI VM
     | wg-kgm 10.254.90.1/32; sole permitted peer 10.254.90.2/32
     | official_connect_proxy.py (10.254.90.1:18180)
     | CONNECT allowlist: government.ru:443,
     |                    services.government.ru:443 ONLY
     | DNS resolved on EU VM, official HTTPS TLS verified on KGM client
     v
 https://government.ru/news/   or approved first-party HTTPS discovery
```

**Important:** source-specific proxy routing is not yet integrated into any running KGM adapter. Installation on the existing owner node is a separate runtime-network gate; this package tests only the isolated helper and documentation.

## Stage 0 — Mandatory OCI read-only capacity audit

Using the destination tenancy (do not assume current project tenancy's budget):
1. OCI Console -> Home Region and Account type. Verify owner approval. Home Region must be outside Ukraine; the exit location is NOT guaranteed to pass `government.ru` until tested.
2. Governance & Administration -> Limits, Quotas and Usage: record existing E2 Micro instance count, A1 OCPU+RAM consumed, and 200 GB total used boot/block storage.
3. Select exact free-eligible shape/image and home AD; check current availability and VCN limit. Note that E2 Micro can be limited to one specific availability domain.
4. Confirm free-eligible public IPv4/VNIC, 50 GB boot, outbound data remaining and **all** zero-cost service selections; disable cost-bearing optional cloud services.
5. Copy `inventory.template.json` to an ignored **local** project subdirectory (never commit filled inventory or credentials); fill non-secret quantities and true/false observations. Execute `python3 oci_free_guard.py ./inventory.local.json`. It must report `PASS_TO_MANUAL_PROVISIONING_GATE`. Actual OCI capacity can change between checking and clicking Create.
6. No new VM until the inventory is verified, the correct account is accessible, and the owner confirms the proposed tenancy/region/shape. Stop on out-of-host-capacity; retry only permitted free ADs or wait, without paid upgrades.

## Stage 1 — NEW EU VM provisioning, only after Stage 0 PASS

Proposed instance name `kgm-govru-egress-free`, own compartment/project boundary, Ubuntu Always Free-eligible image, single 50 GB boot volume, free E2.1.Micro by default.

- New SSH key pair dedicated to this VM, generated locally and kept **out of chat, GitHub and other projects**.
- OCI ingress: TCP/22 only from explicitly approved administrator IPv4/32 for initial setup; UDP/51820 only from verified KGM owner VM public IPv4/32. **NO** inbound TCP/18180 on a public VNIC, no open public proxy.
- Guest firewall: deny unsolicited inbound; allow same restricted SSH and WireGuard; TCP/18180 only via `wg-kgm` from `10.254.90.2`. Outbound requires only DNS, OS updates, and target HTTPS.
- No new NAT gateway, managed VPN appliance, OCI Site-to-Site VPN, LB, or extra volume. The new VM must remain isolated from existing research and trading hosts.

## Stage 2 — WireGuard key distribution and service, separately authorized

On each authorized host generate WireGuard private keys **locally**, `umask 077; wg genkey`. Share only public peer keys by an owner-approved channel. Use the config shapes in `wireguard-node.example.conf` and `wireguard-kgm-owner.example.conf`. Fill placeholders into root-owned `/etc/wireguard` config files, `chmod 600`, then start each relevant `wg-quick` service. No private-key values in repo or chat.

On the new VM only, install Ubuntu packages `wireguard`, `python3` and firewall tooling through the Ubuntu repository. Create a locked unprivileged account `kgmproxy`; install `official_connect_proxy.py` read-only under `/opt/kgm-govru-egress` and install the supplied sample systemd unit. It must bind only to `10.254.90.1:18180`; start it **after** the WireGuard interface. Configure a local OS firewall in addition to OCI ingress restrictions.

Adding a scoped `wg-kgm-govru` peer to `kgm-e4-owner-pilot` requires a **separate explicit existing-host network-change gate**, an authorized admin account, a rollback plan, and exact-route evidence. Do not change the `kgmops` sudo policy.

## Stage 3 — Acceptance, then source-specific integration gate

- Verify the KGM owner node default IPv4/IPv6 routes and unrelated DNS are unchanged.
- Verify WireGuard can reach only `10.254.90.1/32` from that owner node; VPN does **not** advertise `0.0.0.0/0`, `::/0`, IP forwarding or NAT.
- Test CONNECT to `government.ru:443` with a bounded source-only client, proxy DNS resolution at the EU node, certificate verification and request/time/size limits. Try port 80, a third-party hostname and a non-tunnel source: all must fail or remain direct as specified.
- The `government.ru` adapter remains inactive until P20.5 health, freshness, governed access, provenance, rollback and explicit repository activation acceptance. A foreign IP is not proof the official host is reachable.
- If the VM exits Always Free eligibility, immediately **disable the VPN and do not upgrade to paid**.

## Rollback

1. Disable only the source-specific proxy integration; keep blocked source absent from `B1_REPOSITORY_ACTIVE_SOURCE_IDS`.
2. Stop the dedicated `kgm-govru-egress.service` on the NEW VM; disable the new peer if no longer in use.
3. Once separately authorized, stop only `wg-quick@wg-kgm-govru` on KGM owner, and verify route `10.254.90.1/32` is removed and original default routes never changed.
4. Review residual cloud resources and terminate the new zero-cost VM if the owner no longer needs it; check separate free-volume accounting. Do not alter existing project VMs.

**Current status**: plan/templates/pure proxy policy only. Region, destination tenancy capacity and network permissions unverified; no EU VM or WireGuard interface created. P23.4 strategic expansion gate stays NOT VALIDATED.
