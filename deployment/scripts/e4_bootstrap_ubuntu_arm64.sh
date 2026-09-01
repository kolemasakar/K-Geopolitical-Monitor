#!/usr/bin/env bash
set -Eeuo pipefail

PROJECT_ROOT="/opt/k-geopolitical-monitor"
ALLOW_EXISTING_STATE="${KGM_ALLOW_EXISTING_STATE:-0}"
SERVICE_NAME="kgm-monitor.service"
SERVICE_USER="kgm"

usage() {
  cat <<'EOF'
Usage: sudo deployment/scripts/e4_bootstrap_ubuntu_arm64.sh [--project-root PATH]

Fresh-host bootstrap for the E4 owner-only unattended pilot.
The repository must already be checked out at PATH.

Environment:
  KGM_ALLOW_EXISTING_STATE=1   Explicitly allow bootstrap over an existing runtime DB.
                               Default is fail-closed.
EOF
}

fail() {
  echo "E4 bootstrap failed: $*" >&2
  exit 1
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --project-root)
      [[ $# -ge 2 ]] || fail "--project-root requires a value"
      PROJECT_ROOT="$2"
      shift 2
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      fail "unknown argument: $1"
      ;;
  esac
done

[[ "$EUID" -eq 0 ]] || fail "run as root via sudo"
[[ "$(uname -m)" == "aarch64" ]] || fail "requires native aarch64 host"
[[ -r /etc/os-release ]] || fail "/etc/os-release is unavailable"
# shellcheck disable=SC1091
source /etc/os-release
[[ "${ID:-}" == "ubuntu" ]] || fail "requires Ubuntu"
[[ "${VERSION_ID:-}" == "24.04" ]] || fail "requires Ubuntu 24.04"

PROJECT_ROOT="$(readlink -f "$PROJECT_ROOT")"
[[ -d "$PROJECT_ROOT/.git" ]] || fail "repository checkout is missing at $PROJECT_ROOT"
[[ -f "$PROJECT_ROOT/pyproject.toml" ]] || fail "pyproject.toml is missing"
[[ -f "$PROJECT_ROOT/deployment/systemd/kgm-monitor.service" ]] || fail "systemd unit is missing"
[[ -f "$PROJECT_ROOT/src/kgeopolitical_monitor/e4_host_validation.py" ]] || fail "E4 host validator is missing"

DATABASE_PATH="$PROJECT_ROOT/data/kgeopolitical_monitor.db"
if [[ -e "$DATABASE_PATH" && "$ALLOW_EXISTING_STATE" != "1" ]]; then
  fail "existing runtime DB detected; set KGM_ALLOW_EXISTING_STATE=1 only after explicit review"
fi

export DEBIAN_FRONTEND=noninteractive
apt-get update
apt-get install -y --no-install-recommends \
  ca-certificates \
  git \
  iproute2 \
  python3 \
  python3-pip \
  python3-venv \
  sqlite3 \
  util-linux

# KGM does not use NFS/RPC. Remove the default rpcbind listener only when the
# host proves that no NFS mount or persistent NFS configuration is present.
if findmnt -rn -t nfs,nfs4 | grep -q .; then
  fail "NFS mount detected; refusing to disable rpcbind"
fi
if grep -Ev '^[[:space:]]*(#|$)' /etc/fstab | grep -Eq '[[:space:]]nfs4?[[:space:]]'; then
  fail "NFS fstab entry detected; refusing to disable rpcbind"
fi
systemctl disable --now rpcbind.socket rpcbind.service 2>/dev/null || true
systemctl mask rpcbind.socket rpcbind.service 2>/dev/null || true
if systemctl is-active --quiet rpcbind.socket || systemctl is-active --quiet rpcbind.service; then
  fail "rpcbind remains active after hardening"
fi
if ss -H -ltn '( sport = :111 )' | grep -q . || ss -H -lun '( sport = :111 )' | grep -q .; then
  fail "port 111 listener remains after rpcbind hardening"
fi

if ! id -u "$SERVICE_USER" >/dev/null 2>&1; then
  useradd \
    --system \
    --user-group \
    --home-dir "$PROJECT_ROOT" \
    --no-create-home \
    --shell /usr/sbin/nologin \
    "$SERVICE_USER"
fi

systemctl stop "$SERVICE_NAME" 2>/dev/null || true
systemctl disable "$SERVICE_NAME" 2>/dev/null || true

rm -rf "$PROJECT_ROOT/.venv"
python3 -m venv "$PROJECT_ROOT/.venv"
"$PROJECT_ROOT/.venv/bin/python" -m pip install --upgrade pip
(
  cd "$PROJECT_ROOT"
  "$PROJECT_ROOT/.venv/bin/python" -m pip install -e ".[test]"
  "$PROJECT_ROOT/.venv/bin/python" -m pytest -q
)

mkdir -p "$PROJECT_ROOT/data/e4_host_validation"
chown -R root:root "$PROJECT_ROOT"
# The repository may have been staged through mktemp(1), whose root directory
# is 0700. Keep code root-owned but make the project root traversable/readable
# by the dedicated service user; runtime state remains the only writable tree.
chmod 0755 "$PROJECT_ROOT"
chown -R "$SERVICE_USER:$SERVICE_USER" "$PROJECT_ROOT/data"
chmod 0750 "$PROJECT_ROOT/data" "$PROJECT_ROOT/data/e4_host_validation"

runuser -u "$SERVICE_USER" -- \
  "$PROJECT_ROOT/.venv/bin/python" \
  -m kgeopolitical_monitor.unattended_runner \
  --project-root "$PROJECT_ROOT" \
  --once

BACKUP_PATH="$PROJECT_ROOT/data/e4_host_validation/pre_service_backup.db"
rm -f "$BACKUP_PATH"
runuser -u "$SERVICE_USER" -- \
  env PROJECT_ROOT="$PROJECT_ROOT" BACKUP_PATH="$BACKUP_PATH" \
  "$PROJECT_ROOT/.venv/bin/python" - <<'PY'
import os
from kgeopolitical_monitor.runtime_backup import backup_project_database

backup_project_database(os.environ["PROJECT_ROOT"], os.environ["BACKUP_PATH"])
PY

RESTORE_ROOT="$(mktemp -d /tmp/kgm-e4-restore.XXXXXX)"
chown "$SERVICE_USER:$SERVICE_USER" "$RESTORE_ROOT"
runuser -u "$SERVICE_USER" -- \
  env PROJECT_ROOT="$RESTORE_ROOT" BACKUP_PATH="$BACKUP_PATH" \
  "$PROJECT_ROOT/.venv/bin/python" - <<'PY'
import os
from kgeopolitical_monitor.runtime_backup import restore_project_database

restore_project_database(os.environ["BACKUP_PATH"], os.environ["PROJECT_ROOT"])
PY
sqlite3 "$RESTORE_ROOT/data/kgeopolitical_monitor.db" 'PRAGMA integrity_check;' | grep -qx 'ok'
rm -rf "$RESTORE_ROOT"

install -o root -g root -m 0644 \
  "$PROJECT_ROOT/deployment/systemd/kgm-monitor.service" \
  "/etc/systemd/system/$SERVICE_NAME"

systemd-analyze verify "/etc/systemd/system/$SERVICE_NAME"
systemctl daemon-reload
systemctl enable --now "$SERVICE_NAME"
systemctl is-enabled --quiet "$SERVICE_NAME"
systemctl is-active --quiet "$SERVICE_NAME"

runuser -u "$SERVICE_USER" -- \
  "$PROJECT_ROOT/.venv/bin/python" \
  -m kgeopolitical_monitor.e4_host_validation \
  --project-root "$PROJECT_ROOT" \
  status \
  --require-pass

cat <<EOF
E4 fresh-host bootstrap PASS
project_root=$PROJECT_ROOT
service=$SERVICE_NAME
runtime_storage=PROJECT_LOCAL_ONLY
rpcbind_surface=DISABLED
next_gate=prepare-reboot -> real reboot -> verify-reboot
production_live=NOT_OPERATIONAL
EOF
