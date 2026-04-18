#!/usr/bin/env bash
# ============================================================
#  Project Anima — startup script
#  Run from repo root: bash start.sh
# ============================================================

set -euo pipefail

# ── Paths (relative to repo root) ───────────────────────────
REPO_ROOT="$(cd "$(dirname "$0")" && pwd)"

# shellcheck disable=SC1091
source "$REPO_ROOT/lib.sh"

# ── Machine-specific configuration ──────────────────────────
# Defaults below; override any of these in .env at the repo root.
# Run: python audio_client/speak.py --list-devices   to find TTS_DEVICE
# Run: python audio_client/capture.py --list-devices to find STT_DEVICE
# Run: python audio_client/speak.py --list-voices    to browse voices

TTS_DEVICE=""          # e.g. 3  — leave empty to use system default
TTS_VOICE="en-GB-RyanNeural"
TTS_SOLICITED_ONLY=0   # 1 = only speak direct replies, not background thoughts

STT_DEVICE=""          # e.g. 1  — leave empty to use system default microphone
STT_MODEL="base"       # tiny | base | small | medium | large-v2

# Discord (Phase 7.2) — set in .env or here; leave empty to skip
DISCORD_BOT_TOKEN=""
DISCORD_CHANNEL_ID=""

BACKEND_URL="ws://localhost:8000/ws"
BACKEND_HTTP="http://localhost:8000"

# ── Load .env ────────────────────────────────────────────────
if [[ -f "$REPO_ROOT/.env" ]]; then
    set -a
    # shellcheck disable=SC1091
    source "$REPO_ROOT/.env"
    set +a
fi

# Discord channel IDs are sometimes copied as "guild_id/channel_id" from URLs.
# Strip the guild prefix — discord_client.py only needs the channel ID.
DISCORD_CHANNEL_ID="${DISCORD_CHANNEL_ID##*/}"
AUDIO_DIR="$REPO_ROOT/audio_client"
DISCORD_DIR="$REPO_ROOT/discord_client"
WEBUI_DIR="$REPO_ROOT/anima-core/web-ui"
DOCKER_DIR="$REPO_ROOT/anima-core"
LOG_DIR="$REPO_ROOT/logs"
PIDS_FILE="$LOG_DIR/.pids"

mkdir -p "$LOG_DIR"

# ── 0. Kill existing processes ───────────────────────────────
inf "Stopping existing processes..."

# Try saved PIDs first (precise), then fall back to command-line patterns
# to catch anything that started outside a previous run of this script.
if [[ -f "$PIDS_FILE" ]]; then
    # shellcheck disable=SC1090
    source "$PIDS_FILE"
    kill_tree "${TTS_PID:-}"     "TTS"     || true
    kill_tree "${STT_PID:-}"     "STT"     || true
    kill_tree "${WEBUI_PID:-}"   "Web UI"  || true
    kill_tree "${DISCORD_PID:-}" "Discord" || true
fi

kill_by_cmdline "speak.py"       "TTS (stray)"     || true
kill_by_cmdline "capture.py"     "STT (stray)"     || true
kill_by_cmdline "discord_client" "Discord (stray)" || true
kill_by_cmdline "vite"           "Web UI (stray)"  || true

# Give processes a moment to release ports
sleep 1

# Bring down Docker stack if running
if docker compose -f "$DOCKER_DIR/docker-compose.yml" ps --quiet 2>/dev/null | grep -q .; then
    inf "Stopping Docker stack..."
    docker compose -f "$DOCKER_DIR/docker-compose.yml" down
    ok "Docker stack stopped"
fi

# Clear stale PID file before starting fresh
rm -f "$PIDS_FILE"

echo ""

# ── 1. TTS — text to speech ──────────────────────────────────
inf "Starting TTS (speak.py)..."

TTS_ARGS="--backend-url $BACKEND_URL --voice $TTS_VOICE"
[[ -n "$TTS_DEVICE" ]]      && TTS_ARGS="$TTS_ARGS --device $TTS_DEVICE"
[[ "$TTS_SOLICITED_ONLY" == "1" ]] && TTS_ARGS="$TTS_ARGS --solicited-only"

python "$AUDIO_DIR/speak.py" $TTS_ARGS > "$LOG_DIR/tts.log" 2>&1 &
TTS_PID=$!
ok "TTS running (PID $TTS_PID) — logs: logs/tts.log"

# ── 2. STT — speech to text ──────────────────────────────────
inf "Starting STT (capture.py)..."

STT_ARGS="--model $STT_MODEL"
[[ -n "$STT_DEVICE" ]] && STT_ARGS="$STT_ARGS --device $STT_DEVICE"

python "$AUDIO_DIR/capture.py" $STT_ARGS > "$LOG_DIR/stt.log" 2>&1 &
STT_PID=$!
ok "STT running (PID $STT_PID) — logs: logs/stt.log"

# ── 3. Web UI ────────────────────────────────────────────────
inf "Starting web UI..."

(cd "$WEBUI_DIR" && npm run dev) > "$LOG_DIR/web-ui.log" 2>&1 &
WEBUI_PID=$!
ok "Web UI running (PID $WEBUI_PID) — logs: logs/web-ui.log"

# ── 2b. Discord (optional) ───────────────────────────────────
DISCORD_PID=""
if [[ -n "$DISCORD_BOT_TOKEN" && -n "$DISCORD_CHANNEL_ID" ]]; then
    inf "Starting Discord client..."
    DISCORD_BOT_TOKEN="$DISCORD_BOT_TOKEN" DISCORD_CHANNEL_ID="$DISCORD_CHANNEL_ID" \
        python "$DISCORD_DIR/discord_client.py" > "$LOG_DIR/discord.log" 2>&1 &
    DISCORD_PID=$!
    ok "Discord client running (PID $DISCORD_PID) — logs: logs/discord.log"
else
    inf "Discord not configured (DISCORD_BOT_TOKEN/DISCORD_CHANNEL_ID not set — skipping)"
fi

# ── 4. Docker ────────────────────────────────────────────────
inf "Starting Docker stack..."

docker compose -f "$DOCKER_DIR/docker-compose.yml" up -d
ok "Docker stack started"

# ── Save PIDs (source-able by stop.sh) ──────────────────────
{
    echo "TTS_PID=$TTS_PID"
    echo "STT_PID=$STT_PID"
    echo "WEBUI_PID=$WEBUI_PID"
    [[ -n "$DISCORD_PID" ]] && echo "DISCORD_PID=$DISCORD_PID"
} > "$PIDS_FILE"

# ── Summary ──────────────────────────────────────────────────
echo ""
echo -e "${GRN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RST}"
echo -e "${GRN}  Project Anima is starting up${RST}"
echo -e "${GRN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RST}"
echo ""
echo "  TTS   PID $TTS_PID    logs/tts.log"
echo "  STT   PID $STT_PID    logs/stt.log"
echo "  UI    PID $WEBUI_PID  logs/web-ui.log"
[[ -n "$DISCORD_PID" ]] && echo "  DC    PID $DISCORD_PID  logs/discord.log"
echo ""
echo "  Web UI  →  http://localhost:5173"
echo "  Backend →  $BACKEND_HTTP"
echo ""
echo "  To tail all logs:"
echo "    tail -f logs/tts.log logs/stt.log logs/web-ui.log"
echo ""
echo "  To stop everything:"
echo "    bash stop.sh"
echo ""
