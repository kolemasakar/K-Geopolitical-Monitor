# Supplemental RDC auto-recovery checkpoint — 2026-09-25

Scope: access channel only; KGM runtime/ROADMAP unchanged. Canonical remote-access documentation: Sentinel-Remote draft PR #25, docs/incidents/KGM_RDC_WATCHDOG_RECOVERY_2026-09-25.md.

Observed: KGM VM remained up, Tailscale active; RDC offline because persisted refresh token was invalid and manual device code expired. Owner completed browser re-pairing; RDC was independently observed ONLINE.

Deployed as unprivileged kgmops:
- user script `~/.local/bin/kgm-rdc-watchdog.sh`, executable 0700, `flock` serialized;
- process-existence check for actual RDC node remote process;
- start via existing user-local Node/npx only when absent, minimum 300-second retry spacing;
- cron `@reboot` and once per minute watchdog; previous crontab backed up locally.
- Syntax and non-disruptive no-op PASS; one agent process after cron update.

Not yet verified: real process-failure recovery, real reboot, end-to-end hung-process detection, persisted refresh token longevity. Invalid token still requires owner browser authorization. No sudo, linger, service restart, production source activation, or cross-project host change.

Primary GitHub OIDC/Tailscale SSH/bounded Ansible remains unchanged. SentinelX remains retired on KGM. Refer to Sentinel-Remote for authoritative future recovery policy; do not duplicate divergent operating procedures here.
