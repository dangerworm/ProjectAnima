# clients/

Host-side client processes that connect to Anima's core via WebSocket or HTTP.
Each client runs on the host machine (not in Docker) and manages its own Python venv.

## audio_client/

- **speak.py** — TTS output surface. Receives synthesis requests from Anima and plays audio.
- **capture.py** — STT input source. Captures microphone audio, transcribes via WhisperX, and posts to `/perception/audio`.

```bash
cd audio_client
source .venv/Scripts/activate   # Git Bash on Windows
python speak.py --list-devices  # find TTS_DEVICE
python capture.py --list-devices # find STT_DEVICE
```

## discord_client/

- **discord_client.py** — Discord bot registered as Anima's Discord identity. Forwards channel messages to `/perception/discord` and routes Anima's Discord expressions back to the channel.

```bash
cd discord_client
source .venv/Scripts/activate
# Requires DISCORD_BOT_TOKEN and DISCORD_CHANNEL_ID in .env
```

Both clients are started and stopped by the root `start.sh` / `stop.sh`.
