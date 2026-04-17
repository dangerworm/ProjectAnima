#!/usr/bin/env bash
# Project Anima — stop script
# Run from repo root: bash stop.sh

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")" && pwd)"
DOCKER_DIR="$REPO_ROOT/anima-core"
LOG_DIR="$REPO_ROOT/logs"

GRN="\033[0;32m"; YLW="\033[0;33m"; RST="\033[0m"
ok()  { echo -e "${GRN}✓ $*${RST}"; }
inf() { echo -e "${YLW}→ $*${RST}"; }

inf "Stopping Project Anima..."

pkill -f "speak.py"        2>/dev/null && ok "TTS stopped"     || true
pkill -f "capture.py"     2>/dev/null && ok "STT stopped"     || true
pkill -f "discord_client" 2>/dev/null && ok "Discord stopped" || true
pkill -f "vite"           2>/dev/null && ok "Web UI stopped"  || true

if docker compose -f "$DOCKER_DIR/docker-compose.yml" ps --quiet 2>/dev/null | grep -q .; then
    docker compose -f "$DOCKER_DIR/docker-compose.yml" down
    ok "Docker stack stopped"
fi

rm -f "$LOG_DIR/.pids"
ok "Done"
