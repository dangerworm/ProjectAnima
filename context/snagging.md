# Snagging List

Small issues noticed during development. Not blockers, but worth fixing before things feel finished.
Add items freely; remove or strike through when resolved.

---

## Web UI

- [ ] Global Workspace panel: activity feed shows in ascending order (oldest first) — should be newest first
  - Fixed in session 2026-04-17 but worth confirming after backend restart
- [ ] Discord bot needs to be started manually each session — not integrated into `start.sh` flow properly
  - `start.sh` already has the logic; needs DISCORD_BOT_TOKEN and DISCORD_CHANNEL_ID set in `.env`
- [ ] MemoryPanel counts use `limit=1` for fetching — shows 0 or 1, not true totals
  - Should use a dedicated count endpoint or `limit=1000` with response `total` field if available
- [ ] `requirements.txt` in `audio_client/` appears as `requirements-stt.txt` in some tool output — verify actual filename

## Backend

- [ ] Discord message deduplication uses in-memory deque — resets on backend restart
  - Acceptable for now; could persist seen IDs to Redis/DB if restart-races become a real problem
- [ ] `POST /perception/discord` and `POST /perception/audio` are nearly identical — consider refactoring into a shared `receive_human_input()` function

## Memory

- [ ] No conversation/episode context on memory writes — channel (web UI / Discord / audio) and
      conversation ID are not stored with reflective, volitional, residue, or observations entries
  - This is the planned Phase 8.x work; see discussion in session 2026-04-17
- [ ] Memory layer counts in UI panel are unreliable (see MemoryPanel item above)

## Documentation

- [ ] `roadmap.md` current status section is stale (still says "Phase 6 not yet started")
- [ ] `roadmap.md` Phase 7.2 Discord items still marked `[ ]` despite being complete
- [ ] `session.md` needs updating to reflect 2026-04-17 session work
- [ ] `architecture.md` may not reflect MCP transition and new actor relationships

## Ethics Gates (Phase 8)

- [ ] Heartbeat and chosen-silence mechanisms not yet verified end-to-end
- [ ] Distress signal not yet verified to fire under realistic conditions
- [ ] Drew to complete `foundation/ethics-review.md` before first unsupervised run

## Git

- [ ] Uncommitted changes as of 2026-04-17 session:
      AGENTS.md, CLAUDE.md, anima-core submodule, audio_client/, context/session.md, start.sh
      New: discord_client/ directory
