"""
Voice enrollment for Project Anima speaker identification.

Extracts a speaker embedding from a WAV file and blends it into the stored
mean embedding for that name. Each call is one enrollment session; subsequent
sessions refine the centroid rather than replacing it.

Usage:
    python enroll.py --name drew --wav <path/to/recording.wav>

Requires HF_TOKEN environment variable set to a Hugging Face access token with
access to pyannote/embedding (accept usage conditions at huggingface.co/pyannote/embedding).
"""

import argparse
import json
import os
import re
import sys
import warnings

warnings.filterwarnings("ignore", module=r"pyannote\.audio")
warnings.filterwarnings("ignore", module=r"lightning\.pytorch")
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
    import logging as _logging
    _logging.getLogger("lightning.pytorch").setLevel(_logging.ERROR)

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
    return np.squeeze(embedding)


def accumulate(name: str, new_vec: np.ndarray) -> int:
    """Blend new_vec into the stored mean for name. Returns the new session count."""
    ENROLLMENTS_DIR.mkdir(exist_ok=True)
    emb_path  = ENROLLMENTS_DIR / f"{name}_embedding.npy"
    meta_path = ENROLLMENTS_DIR / f"{name}_meta.json"

    if emb_path.exists() and meta_path.exists():
        old_vec = np.load(emb_path)
        n = json.loads(meta_path.read_text())["sessions"]
        mean_vec = (old_vec * n + new_vec) / (n + 1)
        sessions = n + 1
    else:
        mean_vec = new_vec
        sessions = 1

    np.save(emb_path, mean_vec)
    meta_path.write_text(json.dumps({"sessions": sessions}))
    return sessions


def main() -> None:
    parser = argparse.ArgumentParser(description="Enroll a speaker for Anima voice identification")
    parser.add_argument("--name", required=True, help="Speaker name (alphanumeric, hyphens, underscores)")
    parser.add_argument("--wav", required=True, help="Path to WAV recording")
    args = parser.parse_args()

    if not _SAFE_NAME.match(args.name):
        print("ERROR: name must contain only letters, digits, hyphens, or underscores.", file=sys.stderr)
        sys.exit(1)

    wav_path = Path(args.wav)
    if not wav_path.exists():
        print(f"ERROR: file not found: {wav_path}", file=sys.stderr)
        sys.exit(1)

    vec = extract_embedding(wav_path)
    print(f"Embedding extracted: dim={vec.shape[0]}")

    sessions = accumulate(args.name, vec)
    print(f"Enrollment updated for '{args.name}' (session {sessions})")


if __name__ == "__main__":
    main()
