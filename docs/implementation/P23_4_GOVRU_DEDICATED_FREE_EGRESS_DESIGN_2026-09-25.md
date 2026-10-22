# P23.4 — Dedicated free non-Ukraine egress for government.ru

Date: 2026-09-25
State: `DESIGN_PREPARED / TENANCY_AND_REGION_CAPACITY_NOT_VERIFIED / NO_NODE_PROVISIONED`
Gate: `GOVRU_DEDICATED_FREE_EGRESS_PREFLIGHT`; NOT `P23_4_EVIDENCE_YIELD_COVERAGE_EXPANSION_VALIDATED`.

## Objective and source isolation

Use a **new dedicated OCI Always Free VM**, in a confirmed non-Ukraine **home region** owned and controlled by the KGM owner or a separately authorized account holder, as a VPN-connected **source-specific HTTPS CONNECT egress** for the existing canonical `https://government.ru/news/` adapter. No change to `kgm-e4-owner-pilot` default route, no reuse of HP-OMEN/krc-cobalt/K-Trader, no unknown public VPN/proxy or HTTP downgrade. This is a free-resource *design*, not a guarantee of zero charges or a standing authorization to provision.

Architecture:

```text
kgm-e4-owner-pilot (KGM: only government.ru adapter)
   | dedicated urllib ProxyHandler HTTPS via Tailscale
   v
KGM-exclusive Tailscale connection: encrypted private mesh
   |
   v
NEW kgm-govru-egress (non-Ukraine OCI Always Free home region)
   | Squid HTTP CONNECT (accept only KGM Tailscale IP -> government.ru:443)
   | remote DNS via egress VM, normal upstream cert validation in KGM
   v
https://government.ru/news/
```

The node is a **VPN-connected proxy**, not a global Tailscale exit node. Standard Tailscale exit-node configuration forwards most non-Tailscale traffic and would violate the project's per-source isolation unless used inside an isolated namespace. Do **not** run `tailscale set --exit-node=...` on the existing KGM owner VM.

## Always Free candidate and hard cost guard

As of September 2026 Oracle's published Always Free limits are **2 Ampere A1 OCPUs / 12 GB RAM total**, or up to **two VM.Standard.E2.1.Micro VMs** (1 GB RAM each), and **200 GB total block storage** in the tenancy's home region. Published included outbound traffic is 10 TB/month. **All allocations are tenancy-wide and could already be consumed.** This design asks for only:
- Preferred (if truly available in the designated tenancy): `VM.Standard.E2.1.Micro`, Ubuntu **Always Free Eligible**, 1 GB RAM, one **50 GB** default/minimum boot volume.
- Fallback only with confirmed free capacity: `VM.Standard.A1.Flex`, **1 OCPU / 3–6 GB RAM**, one 50 GB Always Free boot volume.
- No paid trial-only resource, no reserved or billed IP, no paid VCN/NAT/LB, no additional paid volume/backup.
- Home region must be **outside Ukraine** (verify exact region and outbound IP geolocation; no claim that foreign hosting alone guarantees the remote endpoint responds).
- Avoid automatic account upgrade/PAYG and do not provision unless tenancy's **Limits, Quotas and Usage** + create form indicate Always Free eligibility and enough remaining free capacity.
- `OUT_OF_HOST_CAPACITY`: try another availability domain in the **same home region** or wait. **Do not automatically purchase paid capacity**.
- OCI notes that idle Always Free VMs may be reclaimed. Accept this; **no artificial load** or paid redundancy. The adapter must fail closed and remain disabled until route requalification after any rebuild.

Official references:
- https://docs.oracle.com/en-us/iaas/Content/FreeTier/freetier_topic-Always_Free_Resources.htm
- https://tailscale.com/pricing
- https://tailscale.com/docs/features/sharing
- https://tailscale.com/docs/features/exit-nodes

Tailscale Personal currently advertises a $0 option for individual non-commercial use. Confirm **actual account eligibility and usage conditions**; don't assume KGM has a commercial Tailscale entitlement.

## Prerequisites before OCI console provisioning

Owner/operator must confirm:
1. Which **separately authorized OCI tenancy** and its exact **home region** (no account IDs, keys or secrets in chat).
2. `Limits, Quotas and Usage`: current free micro VM slots/A1 OCPUs, available Always Free block volume and whether the chosen region has shape capacity.
3. Whether the new node will be joined directly to the KGM-controlled tailnet or shared from another authorized tailnet. If separate account/tailnet, use documented Tailscale *machine sharing* with restrictive grants instead of broad unrelated project access. Confirm free Tailscale plan eligibility.
4. Approval to create **one** dedicated VM only **after** measured cost preflight.

If no qualified free OCI tenancy remains, halt and ask for another eligible free provider/owner-controlled node; do not silently switch to a billable region/provider.

## Provisioning runbook (manual OCI console, not yet executed)

1. In the **new authorized OCI tenancy**, switch to its home region and a KGM-only compartment; verify quotas. Make a new `kgm-govru-egress` VM of approved Always Free shape/image with one 50 GB Always Free boot volume and no paid add-ons.
2. Secure SSH: use a newly generated project-specific public key. Keep the corresponding private key out of chat and out of git; restrict temporary SSH ingress to the current owner admin /32 only. Do not expose TCP 3128 publicly.
3. Install supported OS security updates, Tailscale via its official installation procedure, and Squid from the distro repository. Enable security updates and minimal host firewall; do not install monitoring agents that incur cost.
4. Enroll just this VM in an approved KGM Tailscale access scope; record **only non-secret node metadata** (region, instance shape, tailnet connection status and Tailscale IP). If the tenancy owner uses a separate tailnet, explicitly share only this machine with the intended KGM principal; validate restrictive access grants.
5. Configure Squid using the policy *template* below after real KGM and egress Tailscale IPv4 addresses are known. The proxy must bind only its Tailscale interface IP. No 0.0.0.0/public proxy.
6. Run read-only `curl --proxy http://<egress-ts-ip>:3128 --proto '=https' --connect-timeout 5 --max-time 12 -I https://government.ru/news/` from `kgm-e4-owner-pilot`. Confirm success from the new foreign exit and external DNS resolution by that exit. Keep TLS validation enabled; HTTP 200 or documented/validated official redirects only.
7. Add **one** explicit HTTP CONNECT proxy handler to the canonical `russian-government-news-ru` acquisition path in a separate repository-only PR. Never set global `HTTPS_PROXY` / `ALL_PROXY` on the owner VM. Enforce source ID + canonical host allowlist, bounded response bytes, timeouts, DNS/redirect checks, TLS verification and fail-closed path on tunnel/proxy failure.
8. Qualify the resulting source with P20.5 live health, fixture, governance and deterministic empty-selection rollback. Require a **separate source-activation decision** before changing repository active source IDs. No production deployment/restart as part of node preflight.

### Proxy policy template (illustrative; do not apply without confirmed addresses)

```squidconf
# Replace <EGRESS_TS_IP> and <KGM_TS_IP> with verified Tailscale IPv4 addresses.
# IMPORTANT: Replace the DEFAULT squid.conf, not merely append this to a
# configuration that still binds 0.0.0.0:3128.
http_port <EGRESS_TS_IP>:3128
acl kgm_client src <KGM_TS_IP>/32
acl CONNECT method CONNECT
acl SSL_ports port 443
acl government_hosts dstdomain government.ru .government.ru
http_access deny !kgm_client
http_access deny !CONNECT
http_access deny !SSL_ports
http_access deny !government_hosts
http_access allow kgm_client government_hosts CONNECT SSL_ports
http_access deny all
cache deny all
via off
forwarded_for delete
```

Operational checks: `squid -k parse`, `ss -lntp` reports Tailscale-only listening for TCP 3128, owner-to-proxy Tailscale reachability PASS, direct public IP:3128 MUST FAIL, and proxy CONNECT to an unrelated host MUST FAIL. Never disable TLS certificate validation in client. The access control above is defense in depth, not a substitute for Tailscale identity restrictions.

## Security, cost and operational acceptance

- OCI tenancy owner and KGM operator explicitly authorize this one dedicated resource. No credentials are printed in logs or committed.
- Free-shape + Always Free boot storage verified **before clicking Create**, measured after creation, and recurring usage/cost observed through free console monitoring. If any anticipated charge is nonzero/unknown, do **not** provision.
- No changes to existing OCI instances or global network routes. No shared-project runtime reuse.
- `kgm-e4-owner-pilot` must still fetch its current non-Russian sources **directly**, unchanged.
- With proxy stopped/removed, the government source fails closed and no other source is affected. Disabling the specific adapter is the rollback.
- A working foreign tunnel alone does NOT establish independent factual proof. P13.5/P13.6 remain sole factual-verification authority.

## Current measured state / next gate

As of 2026-09-25, the owner node has Tailscale installed, `tailscale exit-node list` shows **no configured exit nodes**, and direct HTTPS/443 to canonical government.ru times out. Dedicated VM not provisioned, no foreign proxy configured, no source activated, no incremental cost incurred by this preparatory design.

**Next dependency:** owner confirms selected OCI tenancy home region and real remaining Always Free capacity, then approves explicit one-VM creation.
