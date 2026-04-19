#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
LOG_DIR="$SCRIPT_DIR/../logs"
PID_FILE="$SCRIPT_DIR/.pid"

# shellcheck disable=SC1091
source "$SCRIPT_DIR/../lib.sh"

mkdir -p "$LOG_DIR"

# ── Kill any existing instance ───────────────────────────────
stop_from_pid_file "$PID_FILE"
kill_by_cmdline "admin_portal/server.py" "Admin server (stray)" || true

# ── Install deps & build frontend ────────────────────────────
inf "Installing Python dependencies..."
source "$SCRIPT_DIR/.venv/Scripts/activate"
pip install -r "$SCRIPT_DIR/requirements.txt" --quiet

inf "Building frontend..."
cd "$SCRIPT_DIR/client"
npm install --silent
npm run build --silent
cd "$SCRIPT_DIR"

# ── Start server ─────────────────────────────────────────────
inf "Starting admin server..."
ADMIN_PID=$(start_bg "$LOG_DIR/admin.log" "$SCRIPT_DIR/.venv/Scripts/python" "$SCRIPT_DIR/server.py")

echo "ADMIN_PID=$ADMIN_PID" > "$PID_FILE"

ok "Admin portal running (PID $ADMIN_PID)"
echo ""
echo "  UI   →  http://localhost:8765"
echo "  Logs →  logs/admin.log"
echo ""
