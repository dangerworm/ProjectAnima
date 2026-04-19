# audio_client

TTS (`speak.py`) and STT (`capture.py`) clients for Project Anima. Both run on the host — Docker on
Windows cannot easily access audio hardware through the bridge network.

## Setup

```bash
cd audio_client
python -m venv .venv
source .venv/Scripts/activate   # Git Bash on Windows
python -m pip install -r requirements-tts.txt
python -m pip install -r requirements-stt.txt
```

## Activation (Git Bash)

Always use `source` with a forward-slash path — backslashes and `python activate` both fail:

```bash
# Correct
source .venv/Scripts/activate

# Wrong — backslashes don't work in Git Bash
.venv\Scripts\activate

# Wrong — activate is a shell script, not a Python file
python .venv/Scripts/activate
```

## speak.py — Text to Speech

Connects to the Anima WebSocket and speaks Anima's unsolicited surface expressions via Microsoft
edge-tts (neural quality).

```bash
python speak.py --list-devices          # show output device indices
python speak.py --list-voices           # show available neural voices
python speak.py --device 3              # use output device 3
python speak.py --voice en-GB-SoniaNeural
python speak.py --speak-all             # speak all LLM output (debug)
```

Default voice: `en-GB-RyanNeural` (set in `start.sh`; override via `TTS_VOICE` in `.env`).

## capture.py — Speech to Text

Pipeline: sounddevice → Silero VAD → faster-whisper → POST to `/perception/audio`.

```bash
python capture.py --list-devices                   # show input device indices
python capture.py --device 1                       # use microphone device 1
python capture.py --model small                    # whisper model size
```

Whisper model sizes (ascending accuracy/speed cost): `tiny`, `base`, `small`, `medium`, `large-v2`,
`large-v3`. Default: `base`.

### Important: STT device selection

By default `capture.py` uses the system default audio input, which on Windows is often the audio mix
(includes speaker output). If you run TTS through speakers without a headset, `capture.py` will pick
up Anima's own voice and feed it back as new input.

Fix: set `STT_DEVICE` in `.env` to the index of your physical microphone:

```bash
python capture.py --list-devices   # find your mic's index
# then in .env:
STT_DEVICE=1
```

## Launching via start.sh

`bash start.sh` from the repo root presents a startup TUI where TTS, STT, and Discord can each be
toggled before launch. Device and voice settings are read from `.env`.
