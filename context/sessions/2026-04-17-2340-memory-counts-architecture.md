# Session Log

> Updated at the end of every Claude Code session. Read this before starting any implementation
> work. The most recent entry is at the top.

---

## Session: 17th April 2026 (memory counts fix + architecture.md update)

Drew active. Short focused session: two snagging items resolved.

### MemoryPanel counts — fixed

MemoryPanel was fetching each memory layer with `limit=1` and using `entries.length` as a proxy for
count. This always returned 0 or 1.

Fix:

- `anima-core/app/core/memory/__init__.py`: added `get_counts()` to `MemoryStore`. Single asyncpg
  query with COUNT(*)/MAX() subqueries across all 6 memory tables + identity_version.
- `anima-core/app/core/main.py`: added `GET /memory/counts` endpoint (before `POST /perception/audio`).
- `anima-core/web-ui/src/components/panels/MemoryPanel.tsx`: replaced 7 parallel fetch calls with a
  single fetch to `/memory/counts`; state now reflects true DB counts.

### architecture.md — updated

Two inaccuracies corrected:

1. "audio (WhisperX)" → "audio (faster-whisper + Silero VAD)" in the Perception section.
2. Added paragraph documenting Discord as bidirectional — perception channel (`POST /perception/discord`)
   and expression surface (`channel='discord'` in the express tool). Previously only mentioned in
   the Expression Router section in passing; now explicit.

### snagging.md

Closed three items:
- MemoryPanel counts use `limit=1` for fetching
- Memory layer counts in UI panel are unreliable
- `architecture.md` may not reflect MCP transition and new actor relationships

### Current state

Phases 1–7 complete. Anima receives audio and Discord input, calls MCP tools autonomously, and has a
full Web UI. Memory panel now shows accurate counts.

### Outstanding before next session

- Discord message deduplication uses in-memory deque — resets on restart (acceptable for now)
- No conversation/episode context on memory writes — design agreed, implementation deferred
- Phase 8 ethics gates:
  - Heartbeat and chosen-silence mechanisms not yet verified end-to-end
  - Distress signal not yet verified to fire under realistic conditions
  - Drew to complete `foundation/ethics-review.md` before first unsupervised run
- Phase 9: add GITHUB_TOKEN + GITHUB_REPO to .env, exercise PR pipeline (GitHub tool calls)
