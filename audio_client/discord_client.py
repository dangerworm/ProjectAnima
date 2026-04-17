"""
Discord client for Project Anima — Phase 7.2.

Two concurrent tasks:
  1. discord.py bot — listens in the configured channel, POSTs messages to
     the Anima backend as DISCORD_MESSAGE inputs.
  2. Backend WebSocket listener — monitors for language_output with
     target='discord', sends Anima's responses to the Discord channel.

Setup:
  1. Create a bot at https://discord.com/developers/applications
  2. Enable "Message Content Intent" under Bot → Privileged Gateway Intents
  3. Invite the bot to your server with permissions: Read Messages, Send Messages
  4. Set DISCORD_BOT_TOKEN and DISCORD_CHANNEL_ID (below or as env vars)

Usage:
    python discord_client.py
    DISCORD_BOT_TOKEN=... DISCORD_CHANNEL_ID=... python discord_client.py
"""

from __future__ import annotations

import asyncio
import json
import logging
import os

import aiohttp
import discord
import websockets

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
log = logging.getLogger(__name__)

# ── Configuration ─────────────────────────────────────────────────────────────
# Set these here or via environment variables.

DISCORD_TOKEN: str = os.environ.get("DISCORD_BOT_TOKEN", "")
CHANNEL_ID: int = int(os.environ.get("DISCORD_CHANNEL_ID", "0"))

BACKEND_HTTP: str = os.environ.get("BACKEND_URL", "http://localhost:8000")
BACKEND_WS_URL: str = os.environ.get("BACKEND_WS_URL", "ws://localhost:8000/ws")

# ── Discord bot ───────────────────────────────────────────────────────────────

intents = discord.Intents.default()
intents.message_content = True  # privileged intent — must be enabled in Discord dev portal

bot = discord.Client(intents=intents)

_channel: discord.TextChannel | None = None


@bot.event
async def on_ready() -> None:
    global _channel
    log.info("Discord bot logged in as %s (id=%s)", bot.user, bot.user.id if bot.user else "?")
    ch = bot.get_channel(CHANNEL_ID)
    if ch is None:
        log.error(
            "Channel %d not found — check DISCORD_CHANNEL_ID and that the bot has access.",
            CHANNEL_ID,
        )
    elif not isinstance(ch, discord.TextChannel):
        log.error("Channel %d is not a text channel.", CHANNEL_ID)
    else:
        _channel = ch
        log.info("Listening in #%s (guild: %s)", ch.name, ch.guild.name)


@bot.event
async def on_message(message: discord.Message) -> None:
    if message.author.bot:
        return
    if message.channel.id != CHANNEL_ID:
        return

    text = message.content.strip()
    if not text:
        return

    log.info("Discord → backend: %s#%s: %.80s", message.author.display_name, message.author.id, text)

    async with aiohttp.ClientSession() as session:
        try:
            resp = await session.post(
                f"{BACKEND_HTTP}/perception/discord",
                json={
                    "text": text,
                    "author": message.author.display_name,
                    "message_id": str(message.id),
                },
                timeout=aiohttp.ClientTimeout(total=10),
            )
            if resp.ok:
                log.debug("Queued in backend perception inbox.")
            else:
                body = await resp.text()
                log.warning("Backend returned %d: %s", resp.status, body[:120])
        except Exception as exc:
            log.error("Failed to POST to backend: %s", exc)


# ── Backend WebSocket listener ────────────────────────────────────────────────


async def _listen_backend() -> None:
    """
    Monitor the backend WebSocket for language_output messages targeted at Discord.
    Reconnects automatically if the connection drops.
    """
    while True:
        try:
            async with websockets.connect(BACKEND_WS_URL) as ws:
                log.info("Connected to backend WebSocket — listening for discord-targeted output.")
                async for raw in ws:
                    try:
                        msg = json.loads(raw)
                    except json.JSONDecodeError:
                        continue

                    if msg.get("type") == "language_output" and msg.get("target") == "discord":
                        content = msg.get("content", "").strip()
                        if not content:
                            continue
                        log.info("Anima → Discord: %.80s", content)
                        if _channel is not None:
                            try:
                                await _channel.send(content)
                            except discord.DiscordException as exc:
                                log.error("Failed to send to Discord: %s", exc)
                        else:
                            log.warning("Channel not ready — dropping Anima response.")

        except (OSError, websockets.exceptions.WebSocketException) as exc:
            log.warning("Backend WS disconnected (%s) — reconnecting in 5s…", exc)
            await asyncio.sleep(5)
        except asyncio.CancelledError:
            return


# ── Entry point ───────────────────────────────────────────────────────────────


async def main() -> None:
    if not DISCORD_TOKEN:
        log.error(
            "DISCORD_BOT_TOKEN is not set. "
            "Edit discord_client.py or set the environment variable."
        )
        return
    if not CHANNEL_ID:
        log.error(
            "DISCORD_CHANNEL_ID is not set. "
            "Edit discord_client.py or set the environment variable."
        )
        return

    ws_task = asyncio.create_task(_listen_backend())
    try:
        await bot.start(DISCORD_TOKEN)
    finally:
        ws_task.cancel()
        try:
            await ws_task
        except asyncio.CancelledError:
            pass


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        log.info("Stopping…")
