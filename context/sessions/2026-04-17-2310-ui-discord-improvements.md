# Session Log

> Updated at the end of every Claude Code session. Read this before starting any implementation
> work. The most recent entry is at the top.

---

## Session: 17th April 2026 (UI improvements + Discord testing) — GW panel, truncation audit, deduplication

Drew active throughout. This session was a UI improvement pass and Discord bring-up session, running
after the Phase 7.1/7.2 infrastructure was already in place.

### GlobalWorkspacePanel — live activity feed

The GW panel previously showed a chip strip of salience signals that was almost always empty.
Replaced it entirely with a live activity feed drawn from `eventStreamEntries`:

- `GW_RELEVANT` set: filters to WORKSPACE_IGNITION, LOOP_STARTED/ENDED, MCP_TOOL_CALL/RESULT,
  ANIMA_RESPONSE, HUMAN_MESSAGE, DISCORD_MESSAGE, AUDIO_INPUT, INTERNAL_STATE_REPORT,
  DISTRESS_SIGNAL, MOTIVATION_SIGNAL, IDLE_TICK
- `entryColor()` and `actorShort()` helpers for compact display
- Feed shows most recent 12 events, newest first
- Horizontal layout fix: removed `ml: 'auto'` from timestamps (was pushing them to the far edge);
  snippet now fills the middle space as `flex: 1`
- Sort order fix: code used `.slice(-12).reverse()` but `eventStreamEntries` is already newest-first
  (prepended in reducer); corrected to `.slice(0, 12)`

### Truncation policy — systematic audit

Drew noticed text being clipped throughout the UI and requested a policy change: no truncation
anywhere on the UI except where genuinely unavoidable for layout reasons.

Removed `textOverflow: 'ellipsis'`, `WebkitLineClamp`, and `whiteSpace: 'nowrap'` (where causing
truncation) from all of the following files:

- `GlobalWorkspacePanel.tsx` — ignition type and snippet
- `UnsolicitedExpressionsPanel.tsx` — removed `WebkitLineClamp: 3`; removed `slice(0, 5)` cap so all
  expressions shown; container changed to `overflowY: 'auto'` with hidden scrollbar
- `PerceptionPanel.tsx` — audio input and conversation turns
- `LanguagePanel.tsx` — trigger label
- `WorldPerceptionPanel.tsx` — topic text
- `EventStreamPanel.tsx` — both event type and snippet in all view modes
- `NavBar.tsx` — tool call name (maxWidth widened from 180 → 320)
- `CentreCanvas.tsx` — signal label, ignition event type, tool args

All replaced with `whiteSpace: 'pre-wrap'`, `wordBreak: 'break-word'` and scrollable containers.

### Discord bring-up: .env fix and channel ID

Drew attempted to start the Discord bot and messages weren't getting through. Two issues found:

1. `discord.py` not installed — `pip install -r discord_client/requirements.txt` needed
2. `DISCORD_CHANNEL_ID` in `.env` was set to the full Discord URL path
   (`1490321921034948649/1490321921760428086`) instead of just the channel ID
   (`1490321921760428086`). Fixed in `.env`.

### Discord client relocation

`discord_client.py` was previously in `audio_client/` alongside the audio hardware scripts. Drew
questioned this — audio = hardware I/O, Discord = network integration. Moved to a dedicated
`discord_client/` directory at the repo root:

- `discord_client/discord_client.py` (was `audio_client/discord_client.py`)
- `discord_client/requirements.txt` (was `audio_client/requirements-discord.txt`)
- `start.sh` updated: `AUDIO_DIR` now only used for audio scripts; `DISCORD_DIR` added for Discord

### Discord duplicate messages

After fixing the channel ID, messages arrived twice — two instances of `discord_client.py` were
running from the debugging session. Also added server-side deduplication in case this happens again:

- `main.py`: added `import collections` and `_seen_discord_ids: collections.deque[str]` (maxlen=256)
- `POST /perception/discord`: returns early with `status: duplicate` if `message_id` already seen

### Memory architecture audit

Reviewed whether conversation/episode context is tracked. It is not: memory writes (reflective,
volitional, residue, observations) have no `conversation_id` or `source_channel` metadata.

Agreed episodic/semantic split in the UI is premature until the implementation exists. Design
agreed: episodic layers (reflective, volitional, residue, observations) will need `conversation_id`
and `source_channel` fields in a future migration. Implementation deferred — see snagging.md.

### Supporting changes

- `context/snagging.md` created: categorised list of small outstanding issues
- `planning/roadmap.md`: Phase 7.2 Discord tasks all marked `[x]`; "Current status" section
  rewritten (was stale — said "Phase 6 not yet started")
- `~/.claude/settings.json`: `effortLevel` changed from `"medium"` to `"high"`

### Current state

Phases 1–7 complete. Anima receives audio and Discord input, calls MCP tools autonomously, and has a
full Web UI. The activity feed in GlobalWorkspacePanel is now meaningfully populated.

Outstanding before next session:

- Backend restart needed for discord dedup fix and any `_emit_response` changes to take effect
- Episode/conversation context tracking: design agreed, not yet implemented (see snagging.md)
- Phase 8 ethics gates: heartbeat + distress signal end-to-end verification still needed
- Drew to complete `foundation/ethics-review.md` before first unsupervised run
