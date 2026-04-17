## Session: 17th April 2026 (overnight) — Phases 6.2–6.6: MCP Architecture

### What happened this session

Drew went to sleep after setting bypassPermissions mode. Full Phase 6 MCP architecture built while
he slept. Commit: `ef44804` in anima-core.

**Phase 6.2 — MCP server skeleton**

New package `app/mcp_server/`:

- `tool.py` — `AnimaTool` ABC (name, description, parameters_schema, execute, to_ollama_format),
  `ToolContext` dataclass (memory_store, event_log, registry, perception_actor, workspace_root,
  web_fetch_rate_limiter)
- `registry.py` — `ToolRegistry`: register, list_for_llm (Ollama format), execute (dispatch by name)
- `__init__.py` — `build_registry()` factory instantiating all 18 tools

**Phase 6.3 — Core MCP tool set** (`app/mcp_server/tools/`)

18 tools across 5 modules:

- `memory.py` (9 tools): ReadReflectiveTool, ReadResidueTool, ReadIdentityTool, ReadVolitionalTool,
  ReadObservationsTool, ReadPlansTool, WriteObservationTool, WritePlanTool, UpdatePlanTool
- `expression.py`: ExpressTool — logs ANIMA_RESPONSE, delivers LanguageOutput to ExpressionActor
- `perception.py`: ReadPerceptionTool — calls perception_actor.read_inbox(channel, limit)
- `filesystem.py`: ReadFileTool, WriteFileTool, ListDirectoryTool (path validation to /anima/ and
  /app/)
- `web.py`: WebSearchTool (DuckDuckGo), WebFetchTool (httpx + trafilatura), TokenBucket rate limiter
- `system.py`: ReadEventLogTool (query by type/time), ReadInternalStateTool (latest ISR)

**Phase 6.4 — GW+Orchestrator merge** (`app/actors/global_workspace/__init__.py`)

GlobalWorkspaceActor now has two parallel responsibilities:

- Salience queue / ignition (unchanged)
- Orchestrator idle loop: `_orchestrator_loop()` wakes every IDLE_INTERVAL_SECS, assembles internal
  state context (time, event log depth, residue count, ISR summary, inbox status), calls LLM with
  tools via `_idle_tick()`. Tool calls → `_enter_loop()` (N-turn MCP loop). Text response →
  ExpressionActor. Empty response → stay idle.
- `_in_loop` guard prevents concurrent loop entries
- New constructor params: llm_client, tool_registry, memory_store, perception_actor,
  idle_interval_secs, loop_max_turns, system_prompt

LLM client extended: `ToolCall`, `LLMWithToolsResponse`, `complete_with_tools()` method (POSTs to
Ollama `/api/chat` with tools param, parses tool_calls from response).

**Phase 6.5 — Perception inbox queue** (`app/actors/perception/__init__.py`)

PerceptionActor rewrite:

- Human messages queued per-channel in `_channels: dict[str, deque]` (renamed from `_inbox` to avoid
  collision with base Actor's asyncio.Queue `_inbox`)
- `read_inbox(channel, limit)`, `get_inbox_status()`, `total_inbox_count` property
- HUMAN_MESSAGE still logged to event log (TemporalCore and SelfNarrative read from there)
- No longer sends SalienceSignal to GlobalWorkspace — inbox pull model replaces push model

TemporalCoreActor updated: tracks `_last_human_contact` from event log (startup + per-tick poll via
`_refresh_human_contact()`) rather than IgnitionBroadcast, since HUMAN_MESSAGE no longer ignites the
workspace.

**Phase 6.6 — Observations and plans** (two new memory layers)

New DB tables:

- `observations`: id, created_at, content, embedding vector(768) — world-facing notices
- `plans`: id, created_at, updated_at, content, context JSONB, status (active/completed/abandoned),
  notes — forward-facing intentions

Alembic migration `0005_observations_plans.py`.

MemoryStore: `Observation`, `Plan` dataclasses; `store_observation()`, `search_observations()`,
`get_recent_observations()`, `store_plan()`, `update_plan()`, `get_plans()`.

MemoryActor: `StoreObservation`, `StorePlan`, `UpdatePlanMessage` message types + handlers.

`main.py`: `/memory/observations` and `/memory/plans` REST endpoints; build_registry() called before
actors.

New event types: IDLE_TICK, LOOP_STARTED, LOOP_ENDED, MCP_TOOL_CALL, MCP_TOOL_RESULT, INBOX_READ,
OBSERVATION_STORED, PLAN_STORED, PLAN_UPDATED, PLAN_COMPLETED.

**Test fixes**

- `test_perception_actor.py`: completely rewritten for inbox-queue architecture. Tests: event log
  payload (now includes source_id/source_type), per-channel queue mechanics, read_inbox() behaviour,
  get_inbox_status(), expression actor notification, non-HumanInput drop.
- `test_full_conversation_loop.py`: updated for new architecture — inbox queue tests replacing old
  SalienceSignal flow tests.
- `test_internal_state_actor.py`: removed unused SalienceSignal import.

### Current system state

All Phase 6.2–6.6 code complete and committed. Architecture is:

- GW+Orchestrator: idle loop calls LLM with 18 MCP tools
- PerceptionActor: queues human messages for Anima to pull via read_perception tool
- MemoryActor: 7 memory layers (reflective, residue, identity, volitional, discovery, observations,
  plans)
- LLM: gemma4:e4b (configured in docker-compose.yml)
- All 18 MCP tools implemented

**Migration needed before next run**: `docker compose run --rm anima alembic upgrade head`

LanguageActor still exists and still handles IgnitionBroadcast responses, but it is no longer the
primary conversation path — the GW+Orchestrator idle loop is. Over time, LanguageActor may be
consolidated into the GW+Orchestrator entirely.

### Blockers

- Alembic migration 0005 must run before observations and plans features work
- Tests have not been run in the container this session (bypassPermissions overnight build) —
  recommend running `pytest tests/` after migration before first live run

### Next action

1. Run `docker compose run --rm anima alembic upgrade head` (migration 0005)
2. Run `pytest tests/` in container to confirm tests pass
3. Run the system and observe the first orchestrated conversation
4. **Phase 6.6 Web UI updates** (not yet done): Memory panel should gain Observations and Plans
   sub-layers to complement the existing 5. Pattern is established in MemoryPanel.tsx.
5. Consider whether LanguageActor should be retired or kept as a fallback path
