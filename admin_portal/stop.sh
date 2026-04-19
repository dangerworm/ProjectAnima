#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PID_FILE="$SCRIPT_DIR/.pid"

# shellcheck disable=SC1091
source "$SCRIPT_DIR/../lib.sh"

inf "Stopping admin portal..."

stop_from_pid_file "$PID_FILE"
kill_by_cmdline "admin_portal/server.py" "Admin server (stray)" || true

ok "Done"
