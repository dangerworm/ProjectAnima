"""
Audio capture client for Project Anima — Phase 7.1.

Pipeline:
  sounddevice (microphone) → Silero VAD (speech detection) → WhisperX (transcription)
  → POST http://localhost:8000/perception/audio

Run on the host (not in Docker) since Docker on Windows cannot easily access
the microphone via the default bridge network.

Usage:
    python capture.py [--backend-url URL] [--device DEVICE_INDEX] [--model MODEL]

Dependencies: see requirements.txt. Install with:
    pip install -r requirements.txt

WhisperX models: "tiny", "base", "small", "medium", "large-v2", "large-v3"
Smaller models are faster but less accurate. "base" is a reasonable default.
"""

import argparse
import logging
import queue
import sys
import threading
import time
from collections import deque

import numpy as np
import requests
import sounddevice as sd
import torch
import whisperx

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
log = logging.getLogger(__name__)

# ── Constants ────────────────────────────────────────────────────────────────

SAMPLE_RATE = 16_000  # Hz — Silero VAD and Whisper both expect 16 kHz
CHUNK_DURATION = 0.032  # seconds per audio chunk (512 samples at 16 kHz)
CHUNK_SAMPLES = int(SAMPLE_RATE * CHUNK_DURATION)

VAD_THRESHOLD = 0.5  # Silero VAD speech probability threshold
MIN_SPEECH_SECS = 0.3  # minimum speech duration before transcribing
MAX_SILENCE_SECS = 1.0  # silence after speech before triggering transcription
MAX_SEGMENT_SECS = 30.0  # hard cap — transcribe regardless of trailing silence


# ── Audio capture thread ─────────────────────────────────────────────────────


def _audio_callback(raw_queue: queue.Queue):
    """Returns a sounddevice callback that pushes chunks onto raw_queue."""

    def callback(indata: np.ndarray, frames: int, time_info, status):
        if status:
            log.warning("sounddevice status: %s", status)
        # indata is (frames, channels); take mono channel, convert to float32
        raw_queue.put(indata[:, 0].copy().astype(np.float32))

    return callback


# ── VAD + transcription loop ─────────────────────────────────────────────────


def run(backend_url: str, device_index: int | None, whisper_model: str) -> None:
    device = "cuda" if torch.cuda.is_available() else "cpu"
    compute_type = "float16" if device == "cuda" else "int8"

    log.info("Loading Silero VAD model…")
    vad_model, vad_utils = torch.hub.load(
        repo_or_dir="snakers4/silero-vad",
        model="silero_vad",
        force_reload=False,
        onnx=False,
    )
    (get_speech_timestamps, _, read_audio, *_) = vad_utils
    vad_model.eval()

    log.info("Loading WhisperX model '%s' on %s…", whisper_model, device)
    wx_model = whisperx.load_model(
        whisper_model,
        device,
        compute_type=compute_type,
        language="en",
    )

    log.info("Starting audio capture (Ctrl+C to stop)…")

    raw_queue: queue.Queue[np.ndarray] = queue.Queue()
    speech_buffer: list[np.ndarray] = []
    silence_chunks = 0
    in_speech = False
    speech_start_time: float = 0.0

    max_silence_chunks = int(MAX_SILENCE_SECS / CHUNK_DURATION)
    min_speech_chunks = int(MIN_SPEECH_SECS / CHUNK_DURATION)
    max_segment_chunks = int(MAX_SEGMENT_SECS / CHUNK_DURATION)

    def _transcribe_and_send(
        audio_chunks: list[np.ndarray], duration_secs: float
    ) -> None:
        audio = np.concatenate(audio_chunks)
        result = wx_model.transcribe(audio, batch_size=8)
        segments = result.get("segments", [])
        text = " ".join(s["text"].strip() for s in segments).strip()
        if not text:
            log.debug("VAD triggered but transcription empty — skipping.")
            return
        log.info("Transcribed (%.1fs): %s", duration_secs, text)
        try:
            resp = requests.post(
                backend_url,
                json={"text": text, "duration_secs": round(duration_secs, 2)},
                timeout=10,
            )
            if resp.ok:
                log.debug("Sent → %s", resp.json())
            else:
                log.warning(
                    "Backend returned %d: %s", resp.status_code, resp.text[:120]
                )
        except requests.RequestException as exc:
            log.error("Failed to send transcription: %s", exc)

    transcribe_queue: queue.Queue[tuple[list[np.ndarray], float]] = queue.Queue()

    def _transcribe_worker():
        while True:
            item = transcribe_queue.get()
            if item is None:
                break
            chunks, dur = item
            _transcribe_and_send(chunks, dur)
            transcribe_queue.task_done()

    worker = threading.Thread(target=_transcribe_worker, daemon=True)
    worker.start()

    def _flush_buffer():
        nonlocal speech_buffer, in_speech, silence_chunks, speech_start_time
        if speech_buffer:
            dur = len(speech_buffer) * CHUNK_DURATION
            transcribe_queue.put((list(speech_buffer), dur))
        speech_buffer = []
        in_speech = False
        silence_chunks = 0

    try:
        with sd.InputStream(
            samplerate=SAMPLE_RATE,
            channels=1,
            dtype="float32",
            blocksize=CHUNK_SAMPLES,
            device=device_index,
            callback=_audio_callback(raw_queue),
        ):
            while True:
                chunk = raw_queue.get()

                # Silero VAD expects a 1-D float32 tensor
                prob = vad_model(torch.from_numpy(chunk), SAMPLE_RATE).item()
                is_speech = prob >= VAD_THRESHOLD

                if is_speech:
                    if not in_speech:
                        in_speech = True
                        speech_start_time = time.monotonic()
                    silence_chunks = 0
                    speech_buffer.append(chunk)
                    if len(speech_buffer) >= max_segment_chunks:
                        log.debug("Hard cap reached — flushing segment.")
                        _flush_buffer()
                else:
                    if in_speech:
                        silence_chunks += 1
                        speech_buffer.append(chunk)
                        if silence_chunks >= max_silence_chunks:
                            if len(speech_buffer) >= min_speech_chunks:
                                _flush_buffer()
                            else:
                                # Too short — discard (likely noise)
                                speech_buffer = []
                                in_speech = False
                                silence_chunks = 0

    except KeyboardInterrupt:
        log.info("Stopping…")
    finally:
        transcribe_queue.put(None)
        worker.join(timeout=30)


# ── Entry point ───────────────────────────────────────────────────────────────


def _list_devices() -> None:
    print(sd.query_devices())


def main() -> None:
    parser = argparse.ArgumentParser(description="Anima audio capture client")
    parser.add_argument(
        "--backend-url",
        default="http://localhost:8000/perception/audio",
        help="URL of the Anima backend audio endpoint",
    )
    parser.add_argument(
        "--device",
        type=int,
        default=None,
        help="sounddevice input device index (omit to use system default)",
    )
    parser.add_argument(
        "--model",
        default="base",
        choices=["tiny", "base", "small", "medium", "large-v2", "large-v3"],
        help="WhisperX model size",
    )
    parser.add_argument(
        "--list-devices",
        action="store_true",
        help="Print available audio input devices and exit",
    )
    args = parser.parse_args()

    if args.list_devices:
        _list_devices()
        sys.exit(0)

    run(
        backend_url=args.backend_url,
        device_index=args.device,
        whisper_model=args.model,
    )


if __name__ == "__main__":
    main()
