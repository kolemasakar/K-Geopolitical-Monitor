# P23.4 — Free non-Ukraine VPN node preparation (NOT provisioned)

Date: 2026-09-25
Status: `REPOSITORY_PREPARED_TENANCY_PREFLIGHT_REQUIRED`

Owner approved preparation of a **separate new zero-cost foreign VPN node**, not reusing KGM owner VM as the egress location and not using HP-OMEN, KRC or K-Trader.

Selected architecture: verified separate owner-authorized OCI Always Free tenancy's genuine non-Ukraine Home Region; `VM.Standard.E2.1.Micro` + 50-GB free boot by default, or explicitly owner-selected A1 Flex 1 OCPU/2 GB within free budget; independent WireGuard VM peer, exact `government.ru` HTTPS CONNECT proxy with WG-IP-only binding and official-host allowlist; no host-wide exit-node/default-route mutation. OCI limits, availability, Home Region and the other person's account owner's approval must be checked from the actual destination tenancy before any VM is created.

Repository-only outputs: immutable proxy/guard/tests/config templates and a sequential provisioning/rollback runbook in `ops/p23_4_govru_free_vpn/`.

`CLOUD_RESOURCE_CREATED=0`, `VPN_CONFIGURED=0`, `SOURCE_ACTIVATED=0`, `EXISTING_KGM_NODE_CHANGED=0`, `PAID_RESOURCES=0` (no cloud provider operations executed).

New node and existing-node network changes remain independently gated; policy cannot be treated as successful HTTPS access until actual provider-native controlled validation proves it. Phase 23 remains P23.3 validated, P23.4 unclosed; P13.5/P13.6 factual authority unchanged.

Free provider references: https://docs.oracle.com/en-us/iaas/Content/FreeTier/freetier_topic-Always_Free_Resources.htm and https://docs.oracle.com/en-us/iaas/Content/FreeTier/freetier.htm.
