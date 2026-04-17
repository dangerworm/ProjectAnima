# Snagging List

Small issues noticed during development. Not blockers, but worth fixing before things feel finished.
Add items freely; remove or strike through when resolved.

---

## Web UI

- [x] Global Workspace panel: activity feed was ascending (oldest first) — fixed 2026-04-17
- [x] Discord bot not integrated into `start.sh` — fixed 2026-04-17; requires DISCORD_BOT_TOKEN and
      DISCORD_CHANNEL_ID in `.env`
- [ ] MemoryPanel counts use `limit=1` for fetching — shows 0 or 1, not true totals
  - Should use a dedicated count endpoint or higher limit with response `total` field

## Backend

- [ ] Discord message deduplication uses in-memory deque — resets on backend restart
  - Acceptable for now; could persist seen IDs to DB if restart-races become a real problem
- [x] `POST /perception/discord` and `POST /perception/audio` near-identical — reviewed 2026-04-17;
      divergences are load-bearing (dedup logic, different payload fields, future episode-context
      work will add more per-source fields). Not worth extracting.
- [x] `requirements.txt` in `audio_client/` — confirmed as `requirements-stt.txt` (STT only);
      TTS deps are in `requirements-tts.txt`

## Memory

- [ ] No conversation/episode context on memory writes — channel (web UI / Discord / audio) and
      conversation ID are not stored with reflective, volitional, residue, or observations entries
  - Design agreed 2026-04-17: episodic layers need `conversation_id` + `source_channel` fields in a
    future migration. Implementation deferred.
- [ ] Memory layer counts in UI panel are unreliable (see MemoryPanel item above)

## Documentation

- [x] `roadmap.md` current status section — updated 2026-04-17
- [x] `roadmap.md` Phase 7.2 Discord items — marked complete 2026-04-17
- [x] `session.md` — restructured 2026-04-17; now per-session files in `context/sessions/`
- [ ] `architecture.md` may not reflect MCP transition and new actor relationships

## Ethics Gates (Phase 8)

- [ ] Heartbeat and chosen-silence mechanisms not yet verified end-to-end
- [ ] Distress signal not yet verified to fire under realistic conditions
- [ ] Drew to complete `foundation/ethics-review.md` before first unsupervised run

## Git

- [x] Uncommitted changes from 2026-04-17 session — committed
