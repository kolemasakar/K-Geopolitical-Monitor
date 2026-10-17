#!/bin/bash
set -Eeuo pipefail
test "$(id -u)" -eq 0
SRC_DIR="$(cd "$(dirname "$0")" && pwd)"
id kgmops >/dev/null
python3 -m py_compile "$SRC_DIR/kgm-p24-runtime-report" "$SRC_DIR/kgm-p24-backup"
bash -n "$SRC_DIR/kgm-p24-cleanup"
grep -q 'kgm-p24-report.service' "$SRC_DIR/61-kgm-p24.rules"
grep -q 'kgm-p24-backup.service' "$SRC_DIR/61-kgm-p24.rules"
grep -q 'kgm-p24-cleanup.service' "$SRC_DIR/61-kgm-p24.rules"
install -d -o root -g root -m 0755 /usr/local/libexec
install -d -o root -g root -m 0755 /etc/polkit-1/rules.d
install -o root -g root -m 0755 "$SRC_DIR/kgm-p24-runtime-report" /usr/local/libexec/kgm-p24-runtime-report
install -o root -g root -m 0755 "$SRC_DIR/kgm-p24-backup" /usr/local/libexec/kgm-p24-backup
install -o root -g root -m 0755 "$SRC_DIR/kgm-p24-cleanup" /usr/local/libexec/kgm-p24-cleanup
install -o root -g root -m 0644 "$SRC_DIR/kgm-p24-report.service" /etc/systemd/system/kgm-p24-report.service
install -o root -g root -m 0644 "$SRC_DIR/kgm-p24-backup.service" /etc/systemd/system/kgm-p24-backup.service
install -o root -g root -m 0644 "$SRC_DIR/kgm-p24-cleanup.service" /etc/systemd/system/kgm-p24-cleanup.service
install -o root -g root -m 0644 "$SRC_DIR/61-kgm-p24.rules" /etc/polkit-1/rules.d/61-kgm-p24.rules
install -d -o root -g kgmops -m 0750 /var/lib/kgm-p24-export
install -d -o root -g root -m 0700 /var/lib/kgm-p24-validation
systemctl daemon-reload
echo KGM_P24_DIAG_INSTALL=PASS
