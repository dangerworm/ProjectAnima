## Session: 17th April 2026 (evening) — Phase 7.2 Discord + Audio Pipeline Fixes + Startup Scripts

Drew active throughout. Session continued from the afternoon CentreCanvas context window (which ran
out mid-build). The autonomous instance had already built Phase 7.1, 8, and 9 while Drew was asleep.
This session picked up with Drew, ran the system, found problems, and fixed them.

### Audio pipeline fixes

**`audio_client/capture.py`**:

- Switched from `whisperx` to `faster-whisper>=1.1.0` — whisperx pins ctranslate2==4.4.0 which has
  no wheel for Python 3.14
- API change: `segments` is now a generator; text joined with
  `" ".join(seg.text.strip() for seg in segments)`
- Added 0.5s silence padding before each `transcribe()` call — Whisper clips the last syllable when
  audio ends without trailing silence
- `MAX_SILENCE_SECS`: Drew set this to 3.0 (VAD was splitting utterances mid-word at 1.0s)

**`audio_client/requirements-stt.txt`**: `whisperx>=3.1.5` → `faster-whisper>=1.1.0`

**`audio_client/speak.py`** (TTS client):

- Created fresh this session using edge-tts + miniaudio + sounddevice
- Streams MP3 from Microsoft neural TTS API, decodes via miniaudio, plays via sounddevice
- Explicit `--device` flag for output routing (avoids Windows SAPI device-lock problem)
- `--voice`, `--solicited-only`, `--list-devices`, `--list-voices` flags
- Word-count backpressure: drops new items when queue exceeds `MAX_QUEUED_WORDS = 150`
- Reconnects to backend WS automatically (`reconnect=5`)

**`audio_client/requirements-tts.txt`**: corrected to actual deps — `edge-tts`, `miniaudio`,
`sounddevice`, `websocket-client`, `numpy` (old version had pyttsx3/soundfile)

### Startup scripts

**`start.sh`** (repo root):

- Kills existing processes: speak.py, capture.py, vite, Docker stack
- Starts in order: TTS → STT → web UI → Discord (optional) → Docker
- Sources `.env` from repo root — overrides config defaults
- Strips guild-ID prefix from `DISCORD_CHANNEL_ID` (Discord URLs include guild/channel)
- All processes log to `logs/` directory

**`stop.sh`** (repo root): kills speak.py, capture.py, discord_client, vite; brings down Docker

### Phase 7.2: Discord — Complete

**`discord_client/discord_client.py`** (host script, not in Docker):

- Two concurrent async tasks: discord.py bot (inbound) + backend WebSocket listener (outbound)
- Inbound: messages in configured channel → `POST /perception/discord`
- Outbound: monitors WS for `language_output` with `target='discord'` → sends to Discord channel
- Auto-reconnects to backend WS on disconnect
- Configurable via `DISCORD_BOT_TOKEN` and `DISCORD_CHANNEL_ID` env vars or `.env`

**`discord_client/requirements.txt`**: `discord.py>=2.3.0`, `websockets>=12.0`, `aiohttp>=3.9.0`

**Backend** (`app/core/main.py`):

- `POST /perception/discord` — mirrors `/perception/audio`; accepts `{text, author, message_id}`;
  delivers as `HumanInput(source_id="discord", source_type="discord")` to PerceptionActor
- Logs `DISCORD_MESSAGE` event (type already existed in enum)
- Added `DISCORD_MESSAGE` snippet to `_payload_snippet`: `"Author: text"`

**`app/actors/expression/__init__.py`**: added `"target": message.target` to the `language_output`
broadcast payload — previously missing, meaning discord_client.py couldn't filter by channel

**`app/mcp_server/tools/expression.py`**: updated description to mention `channel='discord'`

**Web UI**:

- `actorState.ts`: `lastDiscordMessage: {text, author, timestamp} | null` added to AppState; set
  from `DISCORD_MESSAGE` event_log_entry; Discord messages prepended to conversation as
  `[Discord] Author: text`
- `PerceptionTab.tsx`: Discord section now live — purple dot (three states: active/connected/not
  configured), shows last message with author and timestamp
- `AnimaLayout.tsx`: passes `lastDiscordMessage` to PerceptionTab

**Drew's Discord bot**: configured. Token and channel ID in `.env` at repo root.

### Web UI fixes (this session)

- `ExpressionPanel.tsx`: `wordBreak: 'break-word'` + `overflowWrap: 'break-word'` + `minWidth: 0` —
  text was rendering on one line and clipping at container edge (not a Whisper issue as first
  suspected — confirmed by screenshot; both causes fixed)
- `AnimaLayout.tsx` conversation view: `width: '100%'` on motion.div wrapper
- `PerceptionTab.tsx` audio channel: three states — active (blue, audio in last 30s) / connected
  (teal, statusHistory non-empty but no recent audio) / inactive (grey, no history at all)
- `PerceptionTab.tsx` inbox: shows backend `inbox_count` in amber when frontend says clear but
  backend reports pending messages (was showing "inbox clear" while live view showed "2 pending")

### Current state

Phase 7.1 complete and tested live (audio working, VAD fixes applied). Phase 7.2 Discord complete —
needs live end-to-end test after restart. Phase 8 infrastructure done; Gates 1 and 2 still need
verification. Phase 9 tools done; needs GITHUB_TOKEN and GITHUB_REPO in `.env`.

**After Drew's computer restart:**

- `./start.sh` — brings up everything including Discord bot
- Test Discord: send a message in the configured channel, verify it appears in Anima's inbox
- Add `GITHUB_TOKEN` and `GITHUB_REPO` to `.env` for Phase 9
- `docker compose run --rm anima alembic upgrade head` (migration 0006, if not already run)
