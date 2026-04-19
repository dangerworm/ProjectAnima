# discord_client

Discord integration for Project Anima — Phase 7.2.

Two concurrent tasks run in one process:

1. **discord.py bot** — listens in the configured channel, POSTs incoming messages to the Anima
   backend as `DISCORD_MESSAGE` perception inputs.
2. **Backend WebSocket listener** — monitors for `language_output` messages with `target='discord'`
   and sends Anima's responses back to the Discord channel.

## Setup

### 1. Create the bot

1. Go to <https://discord.com/developers/applications> and create a new application.
2. Under **Bot**, enable **Message Content Intent** (Privileged Gateway Intents).
3. Under **OAuth2 → URL Generator**, select scopes `bot` and permissions
   `Read Messages / View Channels` + `Send Messages`.
4. Use the generated URL to invite the bot to your server.

### 2. Configure credentials

Add to `.env` in the repo root:

```txt
DISCORD_BOT_TOKEN=your-bot-token
DISCORD_CHANNEL_ID=your-channel-id
```

Channel IDs copied from Discord URLs include a guild prefix (`guild_id/channel_id`); `start.sh`
strips the prefix automatically.

### 3. Python environment

```bash
cd discord_client
python -m venv .venv
source .venv/Scripts/activate   # Git Bash on Windows
python -m pip install -r requirements.txt
```

## Running

The client is launched automatically by `start.sh` (select Discord in the startup TUI) when
`DISCORD_BOT_TOKEN` and `DISCORD_CHANNEL_ID` are set.

To run standalone:

```bash
source .venv/Scripts/activate
python discord_client.py
# or
DISCORD_BOT_TOKEN=... DISCORD_CHANNEL_ID=... python discord_client.py
```
