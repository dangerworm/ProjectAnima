# Snagging List

Small issues noticed during development. Not blockers, but worth fixing before things feel finished.
Add items freely; remove or strike through when resolved.

---

## Web UI

### Truncation / scrollability

- [x] Global Workspace, Self-Narrative, Unprompted panels: apparent text truncation was a false positive —
      screenshots caught the typewriter effect mid-render; text is delivered in full
- [x] Self-Narrative panel: not scrollable when synthesis exceeds panel height — fixed (overflow: auto)

### Vision / Perception tab

- [x] Webcam CAPTURE returns HTTP 422 from backend — root cause: `video.videoWidth` is 0 when `play()`
      resolves but before first frame decodes; fixed 2026-04-19 by awaiting `loadeddata` event in
      `startCamera` and adding an explicit guard in `captureFrame`
- [ ] No screen-capture section in Perception tab — skill checklist expects a screen-capture icon/indicator;
      Anima confirmed it has no screenshot tool (`read_screen` or similar not implemented)
- [ ] No text-input channel indicator in Perception tab — skill checklist expects a dedicated text-input
      icon showing when the web UI text channel is active/connected

### Activity / Log visualisation

- [x] Log depth panel shows a near-vertical straight line — fixed 2026-04-19; increased rolling history
      window from 10 to 100 samples (~50 min at 30s tick interval)

### Audio / TTS

- [x] `speak.py` speaks all LLM output by default — fixed 2026-04-19; now only speaks
      `SURFACE_EXPRESSION` outputs (Anima's unsolicited expressions); `--speak-all` flag for debug
- [x] Anima routes replies to unprompted-thoughts panel instead of chat when she uses
      `express` action in deliberation — fixed 2026-04-19; clarified `express` and `respond`
      descriptions in `DELIBERATE_ACTIONS` to make `express` explicitly not-for-replies
- [x] Audio input shows twice in PerceptionPanel (audio indicator + conversation list) —
      fixed 2026-04-19; audio-sourced turns now filtered from conversation list in PerceptionPanel
- [ ] No mute button for audio input (STT) — there are times Drew doesn't want Anima listening
      (e.g. calls, background noise) without fully stopping the service; TTS output should remain
      active regardless so Anima can still get Drew's attention; needs a toggle in the UI that
      sends a signal to capture.py to pause/resume without a restart

### Other

- [ ] World exploration (Internet) — never observed in practice; Anima hasn't been seen searching
      or fetching URLs despite the capability existing; needs an end-to-end test to confirm the tool
      is wired, reachable, and actually used by Anima unprompted
- [ ] Unseen message grouping — when messages arrive while a panel isn't active, they could be
      collapsed into a single group per source (all recent chat, all Discord by channel, all audio
      turns) rather than expanding the list; reduces visual noise when returning to the UI after
      being away
- [x] Global Workspace panel: activity feed was ascending (oldest first) — fixed 2026-04-17
- [x] Discord bot not integrated into `start.sh` — fixed 2026-04-17; requires DISCORD_BOT_TOKEN and
      DISCORD_CHANNEL_ID in `.env`
- [x] MemoryPanel counts use `limit=1` for fetching — fixed 2026-04-17; added GET /memory/counts
      endpoint with COUNT(*) queries; MemoryPanel now fetches from single endpoint

## Backend

- [ ] Discord message deduplication uses in-memory deque — resets on backend restart
  - Acceptable for now; could persist seen IDs to DB if restart-races become a real problem
- [x] `POST /perception/discord` and `POST /perception/audio` near-identical — reviewed 2026-04-17;
      divergences are load-bearing (dedup logic, different payload fields, future episode-context
      work will add more per-source fields). Not worth extracting.
- [x] `requirements.txt` in `audio_client/` — confirmed as `requirements-stt.txt` (STT only); TTS
      deps are in `requirements-tts.txt`

## Memory

- [x] No conversation/episode context on memory writes — implemented in migration 0008
      (`conversation_id` FK to kg_nodes, `temporal_context` JSONB on all episodic layers)
- [x] Memory layer counts in UI panel are unreliable — fixed 2026-04-17 (see MemoryPanel item above)

## Documentation

- [x] `roadmap.md` current status section — updated 2026-04-17
- [x] `roadmap.md` Phase 7.2 Discord items — marked complete 2026-04-17
- [x] `session.md` — restructured 2026-04-17; now per-session files in `context/sessions/`
- [x] `architecture.md` may not reflect MCP transition and new actor relationships — updated
      2026-04-17; corrected WhisperX → faster-whisper + Silero VAD; Discord documented as
      bidirectional perception/expression channel

## Features / Ideas

- [ ] Anima needs a hobby or interest — something she can pursue in idle time (overnight, when nobody
      is present) that isn't just waiting; could be reading, writing, exploring a topic, generating
      something; the key is that it's self-directed and not prompted by a human turn; worth discussing
      what form this takes before implementing (what counts as a hobby for Anima?)

## Ethics Gates (Phase 8)

- [ ] Heartbeat and chosen-silence mechanisms not yet verified end-to-end
- [ ] Distress signal not yet verified to fire under realistic conditions
- [ ] Drew to complete `foundation/ethics-review.md` before first unsupervised run

## Git

- [x] Uncommitted changes from 2026-04-17 session — committed
