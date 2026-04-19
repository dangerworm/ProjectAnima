#!/usr/bin/env bash
# Project Anima — stop script
# Run from repo root: bash stop.sh

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")" && pwd)"
DOCKER_DIR="$REPO_ROOT/anima-core"
LOG_DIR="$REPO_ROOT/logs"
PIDS_FILE="$LOG_DIR/.pids"

# shellcheck disable=SC1091
source "$REPO_ROOT/lib.sh"

inf "Stopping Project Anima..."

# ── 1. Kill by saved PID (preferred — precise, kills whole tree) ──
stop_from_pid_file "$PIDS_FILE"

# ── 2. Sweep up anything the PID-based kill missed ──────────
# (e.g. if start.sh wasn't used, or a child survived its parent)
kill_by_cmdline "speak.py"       "TTS (stray)"     || true
kill_by_cmdline "capture.py"     "STT (stray)"     || true
kill_by_cmdline "discord_client" "Discord (stray)" || true
kill_by_cmdline "vite"           "Web UI (stray)"  || true

# ── 3. Docker stack ─────────────────────────────────────────
if docker compose -f "$DOCKER_DIR/docker-compose.yml" ps --quiet 2>/dev/null | grep -q .; then
    docker compose -f "$DOCKER_DIR/docker-compose.yml" down
    ok "Docker stack stopped"
fi

ok "Done"
