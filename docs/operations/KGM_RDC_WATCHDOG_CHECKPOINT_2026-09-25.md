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

## Schedule adjustment — 2026-09-25
Owner approved reducing watchdog frequency from once per minute to once every five minutes. Verified live KGM crontab now contains `*/5 * * * * /home/kgmops/.local/bin/kgm-rdc-watchdog.sh`; `@reboot` remains configured. Script syntax validation PASS. This changes only RDC process checks, not exchange-data collection or trading schedules.

## Superseding operating policy — 2026-09-25: on-demand only
Owner rejected periodic five-minute process polling. Removed `*/5 * * * * /home/kgmops/.local/bin/kgm-rdc-watchdog.sh` from live crontab (verified periodic count 0); retained only `@reboot` launch. Added interactive SSH-login trigger to `/home/kgmops/.bashrc` (only when SSH_CONNECTION or SSH_TTY exists), calling existing flock-serialized watchdog on SSH login. Backed up previous .bashrc in the user-local state directory. Verified `bash -n` PASS, one profile marker, and one @reboot cron entry. No continuous polling, no scheduled health checks, no privileged changes. The 300-second retry cooldown remains to prevent repeated failures when pairing expires. If RDC is offline, connect through existing owner SSH as kgmops; opening an interactive SSH shell triggers recovery. GitHub OIDC/Tailscale/Ansible remains primary but a bounded noninteractive Ansible command does NOT necessarily trigger the interactive login hook. RDC may still need manual owner browser reauthorization if the persisted token is invalid. Actual failure-to-recovery on a fresh SSH login remains untested; do not claim it passed. This section supersedes earlier one-minute/five-minute schedules in this checkpoint.
