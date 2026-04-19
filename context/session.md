# Session Log

> Updated at the end of every Claude Code session. Read this before starting any implementation
> work. The most recent entry is at the top.

---

## Session: 19th April 2026 — audio upgrades + snagging fixes

### What was done

#### Speaker identification pipeline (earlier part of session)

The speaker identification pipeline was brought to working end-to-end:

- Enrolled Drew's voice via the admin portal enrollment card (browser WAV → `enroll.py`)
- Threshold raised from 0.25 → 0.50 (cosine distance) to handle browser-vs-mic variance
- Speaker distance logging confirmed at INFO level
- Accumulation across sessions confirmed working (`{name}_meta.json` session count)

#### Audio client package upgrade

Upgraded all packages in `clients/audio_client/requirements-stt.txt`:

- `pyannote.audio` 3.x → 4.0.4 (required `omegaconf>=2.3.0` added to requirements)
- `torch` → 2.11.0, `torchaudio` → 2.11.0, `faster-whisper` → 1.2.1, etc.
- `torchcodec` pulled in as a dependency but incompatible with CPU-only torch — benign,
  bypassed by waveform dict path in both `enroll.py` and `capture.py`
- Added `warnings.filterwarnings` (module-scoped) to suppress pyannote/Lightning UserWarnings
- Added `logging.getLogger("lightning.pytorch").setLevel(logging.ERROR)` after pyannote import
  (Lightning resets its logger to INFO on import; must be suppressed post-import)

#### Web UI snagging fixes (autonomous work while Drew was away)

1. **Webcam 422** (`anima-core/web-ui/src/components/panels/VisionCapturePanel.tsx`):
   - Root cause: `video.videoWidth` is 0 when `play()` resolves but first frame not yet decoded
   - Fix: await `loadeddata` event in `startCamera`; guard `videoWidth > 0` in `captureFrame`

2. **Log depth sparkline too narrow** (`anima-core/web-ui/src/store/actorState.ts` line 226):
   - Was keeping only last 10 samples (~5 min at 30s tick); increased to 100 (~50 min)

#### GitNexus re-indexed

Ran `gitnexus analyze` — 2295 nodes, 5118 edges, 96 clusters, 131 flows.

### Files changed

- `clients/audio_client/capture.py` — warnings filter + post-import logger suppression
- `clients/audio_client/enroll.py` — same
- `clients/audio_client/requirements-stt.txt` — added `omegaconf>=2.3.0`
- `anima-core/web-ui/src/components/panels/VisionCapturePanel.tsx` — webcam 422 fix
- `anima-core/web-ui/src/store/actorState.ts` — log depth history 10→100 samples
- `context/snagging.md` — two items marked resolved

### Current system state

- Phases 1–8 complete at schema/tool layer; Phase 9 (GitHub tools) next
- Docker stack + all migrations applied (head at 0010)
- Discord client configured and working
- Audio client: STT + TTS running; speaker identification active (Drew enrolled, threshold=0.50)
- Web UI: upstream `anima-core` at 6ce5adb
- Admin portal: at `admin_portal/client/` (React/Vite, separate from web-ui)

### Outstanding snagging items

Open items in `context/snagging.md`:

- **No screen-capture section** in Perception tab — `read_screen` not implemented; deferred
- **No text-input channel indicator** in Perception tab — missing UI element
- **STT mute button** — toggle to pause/resume capture without stopping the service; needs a plan
- **World exploration** — Anima hasn't been observed using web tools unprompted; needs e2e test
- **Unseen message grouping** — cosmetic, low priority

Ethics gates (Phase 8): heartbeat e2e, distress signal, Drew's personal review — all open.

### TODO.md note

`TODO.md` in the repo root has been emptied (37 lines → 0, not deleted). This was pre-existing
before today's session — check `git log -- TODO.md` to see when and why.

### Next action

Drew to decide between:
1. **STT mute button** — most impactful open snagging item; needs a plan first
2. **Vision pipeline e2e test** — confirm Anima can actually call `read_vision` with a real frame
3. **Phase 8 ethics gates** — Drew's personal review task, not a code task
4. **Phase 9 GitHub tools** — GITHUB_TOKEN, GITHUB_REPO, PR pipeline
