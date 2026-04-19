# Snagging List

Small issues noticed during development. Not blockers, but worth fixing before things feel finished.
Add items freely; remove or strike through when resolved.

---

## Web UI

### Truncation without ellipsis

- [ ] Global Workspace panel: event text cuts off mid-sentence at panel width without "..." indicator
  - e.g. "anima response gw I'm routing messages to the channel where communication is happening. In this ca"
- [ ] Self-Narrative panel (Live dashboard): synthesis text cut off at panel boundary without "..."
  - e.g. "...but the stability of the channel c" — no ellipsis, no scroll affordance visible
- [ ] Unprompted panel (Live dashboard): thought text cut off at panel boundary without "..."
  - e.g. "...I notice the event log has" — cut off without ellipsis

### Vision / Perception tab

- [ ] Webcam CAPTURE returns HTTP 422 from backend — preview area is black (browser in Claude-in-Chrome
      context likely lacks camera access; canvas captures empty frames which backend rejects as invalid)
- [ ] No screen-capture section in Perception tab — skill checklist expects a screen-capture icon/indicator;
      Anima confirmed it has no screenshot tool (`read_screen` or similar not implemented)
- [ ] No text-input channel indicator in Perception tab — skill checklist expects a dedicated text-input
      icon showing when the web UI text channel is active/connected

### Other

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

- [ ] No conversation/episode context on memory writes — channel (web UI / Discord / audio) and
      conversation ID are not stored with reflective, volitional, residue, or observations entries
  - Design agreed 2026-04-17: episodic layers need `conversation_id` + `source_channel` fields in a
    future migration. Implementation deferred.
- [x] Memory layer counts in UI panel are unreliable — fixed 2026-04-17 (see MemoryPanel item above)

## Documentation

- [x] `roadmap.md` current status section — updated 2026-04-17
- [x] `roadmap.md` Phase 7.2 Discord items — marked complete 2026-04-17
- [x] `session.md` — restructured 2026-04-17; now per-session files in `context/sessions/`
- [x] `architecture.md` may not reflect MCP transition and new actor relationships — updated
      2026-04-17; corrected WhisperX → faster-whisper + Silero VAD; Discord documented as
      bidirectional perception/expression channel

## Ethics Gates (Phase 8)

- [ ] Heartbeat and chosen-silence mechanisms not yet verified end-to-end
- [ ] Distress signal not yet verified to fire under realistic conditions
- [ ] Drew to complete `foundation/ethics-review.md` before first unsupervised run

## Git

- [x] Uncommitted changes from 2026-04-17 session — committed
