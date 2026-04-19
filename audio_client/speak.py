"""
TTS client for Project Anima — uses Microsoft edge-tts (neural quality).

Connects to the Anima WebSocket and speaks Anima's unsolicited expressions —
i.e. only language_output messages where in_response_to == 'SURFACE_EXPRESSION'.
Replies to human messages are intentionally not spoken (they go to the chat UI).

Backpressure: if queued speech would exceed MAX_QUEUED_WORDS, new
expressions are dropped rather than letting the audio queue grow unbounded.

Usage:
    python speak.py                              # system default output
    python speak.py --list-devices               # show output device indices
    python speak.py --device 3                   # play through device 3
    python speak.py --list-voices                # show available neural voices
    python speak.py --voice en-GB-SoniaNeural    # pick a voice
    python speak.py --speak-all                  # speak all LLM output (debug only)
"""

from __future__ import annotations

import argparse
import asyncio
import json
import logging
import os
import queue
import re
import sys
import tempfile
import threading

import edge_tts
import miniaudio
import numpy as np
import sounddevice as sd
import websocket  # websocket-client

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
log = logging.getLogger(__name__)

DEFAULT_VOICE = "en-GB-SoniaNeural"
MAX_QUEUED_WORDS = 150  # ~60 s at ~150 wpm — drop new items beyond this

# ── Helpers ──────────────────────────────────────────────────────────────────


def _strip_markdown(text: str) -> str:
    text = re.sub(r"\*{1,3}(.+?)\*{1,3}", r"\1", text, flags=re.DOTALL)
    text = re.sub(r"`{1,3}(.+?)`{1,3}", r"\1", text, flags=re.DOTALL)
    text = re.sub(r"#{1,6}\s+", "", text)
    text = re.sub(r"\[(.+?)\]\(.+?\)", r"\1", text)
    return text.strip()


async def _synthesise(text: str, voice: str) -> tuple[np.ndarray, int]:
    """Return (float32 PCM array, sample_rate) via edge-tts."""
    chunks: list[bytes] = []
    communicate = edge_tts.Communicate(text, voice)
    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            chunks.append(chunk["data"])
    mp3_bytes = b"".join(chunks)
    decoded = miniaudio.decode(mp3_bytes, output_format=miniaudio.SampleFormat.FLOAT32)
    samples = np.array(decoded.samples, dtype=np.float32)
    if decoded.nchannels > 1:
        samples = samples.reshape(-1, decoded.nchannels)
    return samples, decoded.sample_rate


# ── Main ─────────────────────────────────────────────────────────────────────


def run(
    backend_ws_url: str,
    voice: str,
    device: int | None,
    speak_all: bool,
) -> None:
    speech_queue: queue.Queue[str | None] = queue.Queue()
    _lock = threading.Lock()
    _queued_words = [0]

    def enqueue(text: str) -> None:
        words = len(text.split())
        with _lock:
            if _queued_words[0] + words > MAX_QUEUED_WORDS:
                log.warning(
                    "TTS backlog %d words — dropping: %.60s", _queued_words[0], text
                )
                return
            _queued_words[0] += words
        speech_queue.put(text)

    def speak_worker() -> None:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        while True:
            text = speech_queue.get()
            if text is None:
                break
            words = len(text.split())
            log.info("Speaking (%d words, voice=%s): %.80s%s", words, voice, text, "…" if len(text) > 80 else "")
            try:
                samples, rate = loop.run_until_complete(_synthesise(text, voice))
                sd.play(samples, rate, device=device)
                sd.wait()
            except Exception as exc:
                log.error("TTS error: %s", exc)
            finally:
                with _lock:
                    _queued_words[0] = max(0, _queued_words[0] - words)
                speech_queue.task_done()

        loop.close()

    worker = threading.Thread(target=speak_worker, daemon=True)
    worker.start()

    def on_message(ws_app: websocket.WebSocketApp, raw: str) -> None:
        try:
            msg = json.loads(raw)
        except json.JSONDecodeError:
            return
        if msg.get("type") != "language_output":
            return
        if not speak_all and msg.get("in_response_to") != "SURFACE_EXPRESSION":
            return
        content = msg.get("content", "").strip()
        if content:
            enqueue(_strip_markdown(content))

    def on_error(ws_app: websocket.WebSocketApp, error: Exception) -> None:
        log.error("WebSocket error: %s", error)

    def on_close(ws_app: websocket.WebSocketApp, code: int, reason: str) -> None:
        log.info("WebSocket closed (%s): %s", code, reason)

    def on_open(ws_app: websocket.WebSocketApp) -> None:
        log.info("Connected to %s — voice: %s", backend_ws_url, voice)

    ws = websocket.WebSocketApp(
        backend_ws_url,
        on_message=on_message,
        on_error=on_error,
        on_close=on_close,
        on_open=on_open,
    )

    try:
        ws.run_forever(reconnect=5)
    except KeyboardInterrupt:
        log.info("Stopping…")
    finally:
        speech_queue.put(None)
        worker.join(timeout=10)


# ── Entry point ───────────────────────────────────────────────────────────────


def main() -> None:
    parser = argparse.ArgumentParser(description="Anima TTS client (edge-tts)")
    parser.add_argument("--backend-url", default="ws://localhost:8000/ws")
    parser.add_argument("--voice", default=DEFAULT_VOICE, help=f"edge-tts voice (default: {DEFAULT_VOICE})")
    parser.add_argument("--device", type=int, default=None, help="sounddevice output index (--list-devices to find)")
    parser.add_argument("--speak-all", action="store_true", help="Speak all LLM output including replies (default: expressions only)")
    parser.add_argument("--list-devices", action="store_true", help="Print output devices and exit")
    parser.add_argument("--list-voices", action="store_true", help="Print available edge-tts voices and exit")
    args = parser.parse_args()

    if args.list_devices:
        print(sd.query_devices())
        sys.exit(0)

    if args.list_voices:
        voices = asyncio.run(edge_tts.list_voices())
        for v in sorted(voices, key=lambda x: x["ShortName"]):
            if v["ShortName"].startswith("en-"):
                print(f"  {v['ShortName']:35s}  {v['Gender']:6s}  {v['FriendlyName']}")
        sys.exit(0)

    run(
        backend_ws_url=args.backend_url,
        voice=args.voice,
        device=args.device,
        speak_all=args.speak_all,
    )


if __name__ == "__main__":
    main()
