# KGM independence from Desktop Commander — read-only audit (2026-09-25)

Scope: repo architecture, accepted Sentinel-Remote access contract, and live **non-disruptive** KGM VM observations. No RDC process termination, auth revocation, service restart, network exposure or privilege changes.

## Verified
- KGM architecture identifies the primary control plane as GitHub workflow_dispatch -> project-scoped OIDC -> ephemeral Tailscale -> SSH as kgmops -> bounded Ansible. RDC is supplemental, not a required control-plane component.
- Existing `.github/workflows/tailscale-kgm-control.yml` supports bounded `health` and `restart`, does not call RDC, and uses batch-mode SSH. Its GitHub-hosted runner dependency is subject to the known Actions quota contingency.
- Live VM: system `kgm-monitor.service` active/running/enabled; Tailscale address present. RDC process independently present.
- Live VM: no owner-local HTTP response from `127.0.0.1:8000/health` at audit time. This is **not** evidence of KGM service failure: no endpoint or port is established by this audit.
- Earlier live crontab: only `@reboot /home/kgmops/.local/bin/kgm-rdc-watchdog.sh`; no periodic five-minute entry. SSH interactive shell has a user-local on-demand watchdog hook.
- Current repo explicitly does not authorize/deploy public KGM HTTP/HTTPS/API/dashboard ingress. Shared/team/public use must not be assumed available.

## Dependency matrix
| Operation | RDC required? | Verification |
| --- | --- | --- |
| KGM system service remains running | No architectural dependency documented | Live service active while RDC present; **RDC-off fault injection NOT TESTED** |
| Existing unattended collection | No architectural dependency documented | Runtime execution/continuity during RDC outage NOT TESTED |
| Bounded owner health/restart | No in workflow or Ansible control architecture | Repo inspection only this audit; fresh end-to-end workflow NOT RUN |
| Public third-party interactive KGM request | No public ingress approved/deployed per architecture | NOT AVAILABLE as a demonstrated interface; do not imply tested |
| Supplemental remote terminal via RDC | Yes | Token expiry/revocation prevents this route |
| Owner SSH break-glass | No | Accepted documented route; fresh interactive failover NOT TESTED |

## Findings
1. Losing RDC should not by itself stop KGM's independent systemd runtime; that is a documented architectural boundary, **not a completed RDC-off resilience test**.
2. Third-party users cannot be promised a working independent KGM API/UI: public ingress and shared runtime have explicit owner gates.
3. A revoked RDC refresh token cannot be repaired by merely restarting the agent or invoking SSH-login watchdog; owner reauthorization may still be required.
4. Do not grant a third party the owner's credentials or recovery privileges. Only expose separately authorized, least-privilege user-facing KGM interfaces.
5. GitHub Actions quota makes the primary workflow availability conditional; do not substitute RDC or assume self-hosted fallback is installed.

## Next acceptance gates (not executed)
- Non-disruptive application-level probe using the *actual documented* local KGM health interface, if one exists, and source acquisition state under a permitted identity.
- Controlled RDC-disconnect fault injection only after owner approval and confirmed independent recovery channel; verify collection/service continuity before, during, after.
- Verify accepted OIDC/Tailscale/SSH/Ansible path when runner availability permits.
- Separately approve and test a least-privilege user-facing access channel before asserting third-party independence.
- No periodic polling. Event-specific monitoring frequency requires explicit owner direction.

Status: **DOCUMENTED ARCHITECTURAL SEPARATION / PARTIAL LIVE VERIFICATION / END-TO-END OUTAGE RESILIENCE NOT VALIDATED**.
