# KGM owner-only plugin-first decision (2026-09-25)

Decision: implement a private owner-only KGM plugin before considering any public user-facing API or shared access. Public deployment is deferred until project development is complete and requires a separate owner decision.

The plugin must use KGM's own authorized backend and project-local canonical storage, not trading-project infrastructure. Its functions must not depend on Desktop Commander. Remote Desktop Commander is supplemental development access; the accepted primary administrative route is GitHub OIDC, Tailscale SSH as kgmops and bounded Ansible. Do not expand access privileges or publish the plugin as part of this decision.

Live audit limitation: the KGM RDC device was offline at the latest check. Independent SSH/Ansible health and actual collection continuity during RDC outage have not been revalidated. No public ingress or owner-only plugin backend is claimed to be deployed.

Next gates: independently verify VM/service health through the accepted control path, validate KGM application continuity without RDC, then design and validate a least-privilege owner-only plugin backend. No periodic monitoring unless the owner specifically requests it.

## Live read-only follow-up (2026-09-25)
- After an owner SSH login, the on-demand watchdog recorded an agent start at 16:18:17 UTC; the RDC session was restored and the device is reachable again. The earlier logs contain `Invalid Refresh Token: Already Used` and an expired device code. The precise causal chain is not fully established; no claim of automatic recovery from a truly revoked token.
- Fresh live check: `kgm-monitor.service=active`, `NRestarts=0`, active since 06:47:37 UTC; RDC process running independently. This supports continued systemd service operation across the observed RDC offline interval, but does not prove acquisition continuity or all KGM functions.
- Watchdog shell syntax passed; only `@reboot` cron is installed. No five-minute cron. No intentional disconnect/reboot/revocation test was run.
- Owner-only plugin next design gate: define bounded read-only tools, authentication and a private connectivity method independent of RDC. Public API remains deferred; do not assume the private plugin is already deployed.
