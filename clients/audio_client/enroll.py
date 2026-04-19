"""
Voice enrollment for Project Anima speaker identification.

Extracts a speaker embedding from a WAV file and saves it to
enrollments/{name}_embedding.npy alongside this script.

Usage:
    python enroll.py --name drew --wav <path/to/recording.wav>

The WAV file should be 8-30 s of clean speech (no background music, minimal noise).
Requires HF_TOKEN environment variable set to a Hugging Face access token with
access to pyannote/embedding (accept usage conditions at huggingface.co/pyannote/embedding).
"""

import argparse
import os
import re
import sys
from pathlib import Path

import numpy as np
import soundfile as sf
import torch

ENROLLMENTS_DIR = Path(__file__).parent / "enrollments"
MODEL_ID = "pyannote/embedding"

_SAFE_NAME = re.compile(r"^[a-zA-Z0-9_-]+$")


def extract_embedding(wav_path: Path) -> np.ndarray:
    hf_token = os.environ.get("HF_TOKEN")
    if not hf_token:
        print("ERROR: HF_TOKEN environment variable not set.", file=sys.stderr)
        print("  Set it in your .env file or export it before running.", file=sys.stderr)
        sys.exit(1)

    from pyannote.audio import Model, Inference

    print(f"Loading embedding model '{MODEL_ID}'...")
    model = Model.from_pretrained(MODEL_ID, use_auth_token=hf_token)
    inference = Inference(model, window="whole")

    # Load with soundfile and pass as a waveform dict to bypass pyannote's
    # AudioDecoder (missing in some installed versions on Windows).
    audio, sr = sf.read(str(wav_path))
    if audio.ndim > 1:
        audio = audio.mean(axis=1)  # stereo to mono
    waveform = torch.from_numpy(audio.astype(np.float32)).unsqueeze(0)  # (1, T)
    embedding = inference({"waveform": waveform, "sample_rate": sr})
    vec = np.squeeze(embedding)

    print(f"Embedding extracted: dim={vec.shape[0]}")
    return vec


def main() -> None:
    parser = argparse.ArgumentParser(description="Enroll a speaker for Anima voice identification")
    parser.add_argument("--name", required=True, help="Speaker name (alphanumeric, hyphens, underscores)")
    parser.add_argument("--wav", required=True, help="Path to WAV recording (8-30 s of speech)")
    parser.add_argument(
        "--output",
        default=None,
        help="Override output path for the .npy embedding",
    )
    args = parser.parse_args()

    if not _SAFE_NAME.match(args.name):
        print("ERROR: name must contain only letters, digits, hyphens, or underscores.", file=sys.stderr)
        sys.exit(1)

    wav_path = Path(args.wav)
    if not wav_path.exists():
        print(f"ERROR: file not found: {wav_path}", file=sys.stderr)
        sys.exit(1)

    embedding = extract_embedding(wav_path)

    if args.output:
        output_path = Path(args.output)
    else:
        ENROLLMENTS_DIR.mkdir(exist_ok=True)
        output_path = ENROLLMENTS_DIR / f"{args.name}_embedding.npy"

    np.save(output_path, embedding)
    print(f"Saved enrollment embedding -> {output_path}")


if __name__ == "__main__":
    main()
