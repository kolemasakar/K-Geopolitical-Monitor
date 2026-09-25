# KGM owner-only plugin-first decision (2026-09-25)

Decision: implement a private owner-only KGM plugin before considering any public user-facing API or shared access. Public deployment is deferred until project development is complete and requires a separate owner decision.

The plugin must use KGM's own authorized backend and project-local canonical storage, not trading-project infrastructure. Its functions must not depend on Desktop Commander. Remote Desktop Commander is supplemental development access; the accepted primary administrative route is GitHub OIDC, Tailscale SSH as kgmops and bounded Ansible. Do not expand access privileges or publish the plugin as part of this decision.

Live audit limitation: the KGM RDC device was offline at the latest check. Independent SSH/Ansible health and actual collection continuity during RDC outage have not been revalidated. No public ingress or owner-only plugin backend is claimed to be deployed.

Next gates: independently verify VM/service health through the accepted control path, validate KGM application continuity without RDC, then design and validate a least-privilege owner-only plugin backend. No periodic monitoring unless the owner specifically requests it.
