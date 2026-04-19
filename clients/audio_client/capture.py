"""
Audio capture client for Project Anima — Phase 7.1.

Pipeline:
  sounddevice (microphone) → Silero VAD (speech detection) → faster-whisper (transcription)
  → POST http://localhost:8000/perception/audio

Run on the host (not in Docker) since Docker on Windows cannot easily access
the microphone via the default bridge network.

Usage:
    python capture.py [--backend-url URL] [--device DEVICE_INDEX] [--model MODEL]

Dependencies: see requirements-*.txt. Install with:
    pip install -r requirements-*.txt

Whisper models: "tiny", "base", "small", "medium", "large-v2", "large-v3"
Smaller models are faster but less accurate. "base" is a reasonable default.
"""

import argparse
import logging
import os
import queue
import sys
import threading
import time
from pathlib import Path

import numpy as np
import requests
import sounddevice as sd
import torch
from faster_whisper import WhisperModel

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
log = logging.getLogger(__name__)

# ── Constants ────────────────────────────────────────────────────────────────

ENROLLMENTS_DIR = Path(__file__).parent / "enrollments"
SPEAKER_THRESHOLD = 0.50  # cosine distance; below this → matched speaker (lower = more similar)

SAMPLE_RATE = 16_000  # Hz — Silero VAD and Whisper both expect 16 kHz
CHUNK_DURATION = 0.032  # seconds per audio chunk (512 samples at 16 kHz)
CHUNK_SAMPLES = int(SAMPLE_RATE * CHUNK_DURATION)

VAD_THRESHOLD = 0.5  # Silero VAD speech probability threshold
MIN_SPEECH_SECS = 0.3  # minimum speech duration before transcribing
MAX_SILENCE_SECS = 3.0  # silence after speech before triggering transcription
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


def _load_speaker_models(device: str):
    """Load pyannote + all enrolled embeddings. Returns (inference, {name: embedding}) or (None, {})."""
    if not ENROLLMENTS_DIR.exists():
        log.info("No enrollments directory — speaker identification disabled.")
        return None, {}

    embedding_files = list(ENROLLMENTS_DIR.glob("*_embedding.npy"))
    if not embedding_files:
        log.info("No enrollment files found — speaker identification disabled.")
        return None, {}

    hf_token = os.environ.get("HF_TOKEN")
    if not hf_token:
        log.warning("HF_TOKEN not set — speaker identification disabled.")
        return None, {}

    try:
        from pyannote.audio import Model, Inference
        log.info("Loading speaker embedding model…")
        model = Model.from_pretrained("pyannote/embedding", use_auth_token=hf_token)
        inference = Inference(model, window="whole")

        enrollments: dict[str, np.ndarray] = {}
        for f in embedding_files:
            name = f.stem.replace("_embedding", "")
            enrollments[name] = np.load(f)
            log.info("Loaded enrollment for '%s'.", name)

        log.info(
            "Speaker identification active (%d enrolled, threshold=%.2f).",
            len(enrollments), SPEAKER_THRESHOLD,
        )
        return inference, enrollments
    except Exception as exc:
        log.warning("Speaker model load failed (%s) — identification disabled.", exc)
        return None, {}


def _identify_speaker(inference, enrollments: dict[str, np.ndarray], audio: np.ndarray) -> str:
    """Return name of closest enrolled speaker, or 'unknown' if none are close enough."""
    try:
        from scipy.spatial.distance import cdist
        segment = {"waveform": torch.from_numpy(audio)[None], "sample_rate": SAMPLE_RATE}
        embedding = np.squeeze(inference(segment))  # (D,)

        best_name, best_dist = "unknown", float("inf")
        for name, ref in enrollments.items():
            dist = cdist(ref[None], embedding[None], metric="cosine")[0, 0]
            log.info("Speaker distance to '%s': %.3f (threshold=%.2f)", name, dist, SPEAKER_THRESHOLD)
            if dist < best_dist:
                best_dist, best_name = dist, name

        return best_name if best_dist <= SPEAKER_THRESHOLD else "unknown"
    except Exception as exc:
        log.warning("Speaker identification failed: %s", exc)
        return "unknown"


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

    log.info("Loading Whisper model '%s' on %s…", whisper_model, device)
    wx_model = WhisperModel(whisper_model, device=device, compute_type=compute_type)

    embed_model, enrollments = _load_speaker_models(device)

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
        # Whisper clips the last syllable if audio ends abruptly; pad with silence.
        audio = np.concatenate(
            [audio, np.zeros(int(SAMPLE_RATE * 0.5), dtype=np.float32)]
        )
        segments, _ = wx_model.transcribe(audio, language="en", beam_size=5)
        text = " ".join(seg.text.strip() for seg in segments).strip()
        if not text:
            log.debug("VAD triggered but transcription empty — skipping.")
            return

        speaker: str | None = None
        if embed_model is not None and enrollments:
            speaker = _identify_speaker(embed_model, enrollments, audio)

        log.info("Transcribed (%.1fs) [%s]: %s", duration_secs, speaker or "?", text)

        payload: dict = {"text": text, "duration_secs": round(duration_secs, 2)}
        if speaker is not None:
            payload["speaker"] = speaker

        try:
            resp = requests.post(
                backend_url,
                json=payload,
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
