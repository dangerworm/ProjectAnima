# Session Log

> Updated at the end of every Claude Code session. Read this before starting any implementation
> work. The most recent entry is at the top.

---

## Session: 18th April 2026 — per-channel conversation nodes + Discord verification

### What was built

Two related features completing the conversation ID design Drew specified:

**1. Per-channel persistent conversation nodes** (`node_type='conversation'`, label = channel name)

Each input channel (web_ui, discord, audio, …) has exactly one `kg_nodes` row that never expires.
Replaces the previous per-loop conversation node, which was creating a new `node_type='conversation'`
row on every `_enter_loop` call (wrong shape — those are loop nodes, not channel identity).

- `MemoryStore.get_or_create_conversation_node(channel)` — idempotent via `INSERT ON CONFLICT DO NOTHING`
- Migration `0009_conversation_nodes_unique_index.py` — partial unique index on `kg_nodes(label) WHERE node_type = 'conversation'`
- Loop nodes renamed: `node_type='loop'`, `label=f"Loop {now_label}"` (one per `_enter_loop` call, as before)
- GW actor: `_conversation_cache: dict[str, UUID]` caches per-channel IDs across idle ticks
- GW actor: `_get_conversation_id(channel)` helper with cache + error suppression

**2. Historical perception query mode**

`read_perception` gained a `from_time` (ISO 8601) parameter. When set, switches to historical mode:
queries `HUMAN_MESSAGE` events in the event log for that channel at or after `from_time`. Messages
are not consumed — non-destructive replay. Anima can use this to pick up context from a channel
it hasn't touched recently.

- `EventLog.query()` extended: `payload_filter` (JSONB `@>` operator), `limit`, `order_desc`
- `ReadPerceptionTool`: split into `_live()` and `_historical()` submethods

**3. Idle context rewrite**

`_assemble_idle_context()` now queries HUMAN_MESSAGE events since the last LOOP_ENDED event and
formats per-channel metadata (not content) for Anima's system prompt:

```
3 perception(s) from 2 conversation(s) since last expression.
conversationId|source|time|count: 935e3c63|web_ui|...|2; f33f0b35|discord|...|1
```

Anima sees the stable per-channel conversation ID and can call `read_perception` with `from_time`
to pull the actual message content if it chooses.

### Files changed (commit e826704 in anima-core)

- `app/alembic/versions/0009_conversation_nodes_unique_index.py` — new migration
- `app/core/event_log/__init__.py` — `query()` extended
- `app/core/memory/__init__.py` — `get_or_create_conversation_node()` added
- `app/actors/global_workspace/__init__.py` — idle context rewrite, loop node rename, conversation cache
- `app/mcp_server/tools/perception.py` — historical mode added

### Verified live

- Migration 0009 applied (`alembic current` → `0009 (head)`)
- `web_ui` conversation node: `935e3c63` (auto-created on first idle tick after restart)
- `discord` conversation node: `f33f0b35` (auto-created when test messages arrived)
- 3 Discord HUMAN_MESSAGE events confirmed in event log with `source_id="discord"`
- Anima called `read_perception(channel="discord", limit=3)` and read all 3 messages
- Anima's unprompted expression (02:41:21) explicitly acknowledged the Discord test messages

### Current system state

- Phases 1–8 complete at the schema/tool layer
- Container running; DB at migration 0009 (head)
- Both `web_ui` and `discord` conversation nodes exist in `kg_nodes`
- 20 old `node_type='conversation'` timestamp-labelled rows remain (pre-rename loop nodes) —
  cosmetic only, no functional impact; they'll age out of relevance naturally

### What's deferred

- **Phase 8 ethics gates** — Gate 1 (heartbeat/chosen-silence e2e), Gate 2 (distress signal),
  Gate 3 (Drew's personal review) — all open; Drew needs to complete `foundation/ethics-review.md`
- **Phase 9 GitHub tools** — GITHUB_TOKEN, GITHUB_REPO, PR pipeline test
- **Cosmetic cleanup** — migrate old timestamp-labelled loop nodes from `node_type='conversation'`
  to `node_type='loop'` (low priority, no functional impact)
- **Memory actor pipeline** — `StoreObservation` etc. still don't pass `conversation_id` through
  the actor message path (MemoryStore accepts it, actor dataclasses don't carry it) — deferred
  from previous session, still outstanding
