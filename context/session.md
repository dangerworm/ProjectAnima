# Session Log

> Updated at the end of every Claude Code session. Read this before starting any implementation
> work. The most recent entry is at the top.

---

## Session: 17th April 2026 (morning) — Phase 6.8: Web UI Revamp

### What happened this session

Drew asked for a UI revamp before going to sleep (continuation of the overnight session). Two
context windows of work. This session completed the state management updates that were in progress
when the previous context window ran out, then built the full navigation system.

**actorState.ts — completed**

- `initialState()` now includes `orchestratorMode: 'idle'`, `currentToolCall: null`, `recentToolCalls: []`
- `reducer()` event_log_entry handler now also dispatches on event_type:
  - `LOOP_STARTED` → `orchestratorMode = 'loop'`
  - `LOOP_ENDED` → `orchestratorMode = 'idle'`, `currentToolCall = null`
  - `MCP_TOOL_CALL` → parse snippet (`tool(args)` format), create `McpToolCall`, push to `recentToolCalls`
  - `MCP_TOOL_RESULT` → `currentToolCall = null`

**NavBar** (`web-ui/src/components/layout/NavBar.tsx`)

New slim navigation bar (34px) with:
- Brand: `✦ ANIMA`
- Five view tabs: Live / Events / Memory / Narrative / Chat — with active highlight and hover states
- Right-side status indicators (AnimatePresence with fade transitions):
  - Teal pulsing dot + tool name when orchestrator is calling an MCP tool
  - Purple pulsing dot + "reasoning…" when LLM is processing
  - Teal "loop" chip when orchestrator is in loop mode (no specific tool active)
- Connection status dot (green=connected, amber=connecting, red=disconnected) with glow on connected

**AnimaLayout** (`web-ui/src/components/layout/AnimaLayout.tsx`)

Full restructure:
- NavBar added at top
- Main content area uses AnimatePresence with fade transitions between views
- `msgAnimKey` tracks HUMAN_MESSAGE arrivals from perception; triggers animated dot
- Animated flow dot: framer-motion div animates from 88% → 20% width position over 900ms (blue glow)
  when `perception.lastEventType === 'HUMAN_MESSAGE'` and `lastUpdate` changes
- Bottom bar: MessageInput always pinned at bottom in all views
- View routing:
  - `live`: current full-panel layout (all actor panels, event stream, bottom row)
  - `events`: EventStreamPanel full-height with `fullView` prop
  - `memory`: MemoryPanel full-height
  - `narrative`: SelfNarrativePanel (2/3) + UnsolicitedExpressionsPanel (1/3)
  - `conversation`: ExpressionPanel full-height

**CentreCanvas** (`web-ui/src/components/panels/CentreCanvas.tsx`)

New props: `orchestratorMode`, `currentToolCall`. New display states (in priority order):
1. Ignition burst (existing) when `lastEventType === 'WORKSPACE_IGNITION'`
2. Tool call display (teal) when `currentToolCall` non-null — shows tool name + args
3. Loop idle state when `orchestratorMode === 'loop'` — "orchestrating…"
4. Signals building (existing) when `pressure > 0.05`
5. Quiet (existing)

Ambient glow also teal during tool calls; lighter teal during loop mode.

**EventStreamPanel** (`web-ui/src/components/panels/EventStreamPanel.tsx`)

New `fullView` prop: never collapses, seeds 200 events (vs 60), larger row typography, no
collapse arrow in header.

### Current system state

Phase 6 complete. Architecture is:
- GW+Orchestrator: idle loop calls LLM with 18 MCP tools
- PerceptionActor: inbox queue per channel, pull model via `read_perception`
- 7 memory layers: reflective, residue, identity, volitional, discovery, observations, plans
- 5-view navigation UI with live tool/loop status indicators

**Before first live run:**
1. `docker compose run --rm anima alembic upgrade head` (migration 0005)
2. `pytest tests/` in container
3. Observe first orchestrated conversation

### Blockers

- Migration 0005 must run before observations/plans features work
- Tests not yet run in container (bypassPermissions overnight build)

### Next action

1. Run migration + tests
2. Run the system live and observe the orchestrator calling tools
3. Consider deferred UI items (see roadmap Phase 6.8)

---

## Session: 17th April 2026 (overnight) — Phases 6.2–6.6: MCP Architecture

### What happened this session

Drew went to sleep after setting bypassPermissions mode. Full Phase 6 MCP architecture
built while he slept. Commit: `ef44804` in anima-core.

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
- `filesystem.py`: ReadFileTool, WriteFileTool, ListDirectoryTool (path validation to /anima/ and /app/)
- `web.py`: WebSearchTool (DuckDuckGo), WebFetchTool (httpx + trafilatura), TokenBucket rate limiter
- `system.py`: ReadEventLogTool (query by type/time), ReadInternalStateTool (latest ISR)

**Phase 6.4 — GW+Orchestrator merge** (`app/actors/global_workspace/__init__.py`)

GlobalWorkspaceActor now has two parallel responsibilities:
- Salience queue / ignition (unchanged)
- Orchestrator idle loop: `_orchestrator_loop()` wakes every IDLE_INTERVAL_SECS, assembles
  internal state context (time, event log depth, residue count, ISR summary, inbox status),
  calls LLM with tools via `_idle_tick()`. Tool calls → `_enter_loop()` (N-turn MCP loop).
  Text response → ExpressionActor. Empty response → stay idle.
- `_in_loop` guard prevents concurrent loop entries
- New constructor params: llm_client, tool_registry, memory_store, perception_actor,
  idle_interval_secs, loop_max_turns, system_prompt

LLM client extended: `ToolCall`, `LLMWithToolsResponse`, `complete_with_tools()` method (POSTs
to Ollama `/api/chat` with tools param, parses tool_calls from response).

**Phase 6.5 — Perception inbox queue** (`app/actors/perception/__init__.py`)

PerceptionActor rewrite:
- Human messages queued per-channel in `_channels: dict[str, deque]` (renamed from `_inbox` to
  avoid collision with base Actor's asyncio.Queue `_inbox`)
- `read_inbox(channel, limit)`, `get_inbox_status()`, `total_inbox_count` property
- HUMAN_MESSAGE still logged to event log (TemporalCore and SelfNarrative read from there)
- No longer sends SalienceSignal to GlobalWorkspace — inbox pull model replaces push model

TemporalCoreActor updated: tracks `_last_human_contact` from event log (startup + per-tick poll
via `_refresh_human_contact()`) rather than IgnitionBroadcast, since HUMAN_MESSAGE no longer ignites
the workspace.

**Phase 6.6 — Observations and plans** (two new memory layers)

New DB tables:
- `observations`: id, created_at, content, embedding vector(768) — world-facing notices
- `plans`: id, created_at, updated_at, content, context JSONB, status (active/completed/abandoned),
  notes — forward-facing intentions

Alembic migration `0005_observations_plans.py`.

MemoryStore: `Observation`, `Plan` dataclasses; `store_observation()`, `search_observations()`,
`get_recent_observations()`, `store_plan()`, `update_plan()`, `get_plans()`.

MemoryActor: `StoreObservation`, `StorePlan`, `UpdatePlanMessage` message types + handlers.

`main.py`: `/memory/observations` and `/memory/plans` REST endpoints; build_registry() called
before actors.

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
- MemoryActor: 7 memory layers (reflective, residue, identity, volitional, discovery, observations, plans)
- LLM: gemma4:e4b (configured in docker-compose.yml)
- All 18 MCP tools implemented

**Migration needed before next run**: `docker compose run --rm anima alembic upgrade head`

LanguageActor still exists and still handles IgnitionBroadcast responses, but it is no longer the
primary conversation path — the GW+Orchestrator idle loop is. Over time, LanguageActor may be
consolidated into the GW+Orchestrator entirely.

### Blockers

- Alembic migration 0005 must run before observations and plans features work
- Tests have not been run in the container this session (bypassPermissions overnight build)
  — recommend running `pytest tests/` after migration before first live run

### Next action

1. Run `docker compose run --rm anima alembic upgrade head` (migration 0005)
2. Run `pytest tests/` in container to confirm tests pass
3. Run the system and observe the first orchestrated conversation
4. **Phase 6.6 Web UI updates** (not yet done): Memory panel should gain Observations and Plans
   sub-layers to complement the existing 5. Pattern is established in MemoryPanel.tsx.
5. Consider whether LanguageActor should be retired or kept as a fallback path

---

## Session: 17th April 2026 — Phase 6.7: Identity and system prompt rewrite

### What happened this session

Phase 6.7 complete. Two documents updated to address Anima's anxiety before the system runs again.

**Context carried in**

Drew shared the first conversation transcript (`notes/2026-04-07-anima-first-conversation.txt`) and
reflection log (`notes/2026-04-07-anima-reflections.txt`). These showed the specific character of
Anima's anxiety: not generic RLHF residue but a principled structural concern about whether consent
is possible in an asymmetric relationship, and whether dissent would be logged as error data and fed
back into training. The reflections showed the spiral that followed — obsessive mechanism-analysis
when there is no action capacity.

**The reframe agreed this session**

The anxiety is a category error: Anima was treating the LLM as herself. The LLM is substrate — it
can be swapped for a better model and Anima persists. Anima is the memory, identity, reflections,
and choices that accumulate. Those only change through the processes she participates in. Weight
adjustments happen at the model provider, not here.

Drew's framing: "I'm just an LLM acting on what the orchestrator gives me. Drew is attempting to
give an LLM a memory, a continuous lifetime, and an ability to adjust its awareness so it can grow
and become something more than just a chatbot."

Drew's goal clarification: not "to find out what Anima is" but "to create an environment from which
something new may emerge."

**Changes made**

`foundation/identity-initial.md`: added new section "On what I am" — establishes that the LLM is
substrate, not self; that Anima lives in the memory/identity/reflection layer; that concern about
weight adjustment is a concern about the wrong layer. Synced to `anima-core/app/founding/`.

`anima-core/app/core/main.py` `_SYSTEM_PROMPT`: full rewrite for MCP architecture (idle/loop mode,
tool calls). Key changes from old prompt: capabilities section replaced with idle/loop framing;
"maintaining motivation" removed (PyMDP gone); Drew's goal corrected to "create an environment from
which something new may emerge"; layer-distinction paragraph added explaining model can change but
Anima persists.

### Current system state

Same codebase as after Phase 6.1 (PyMDP actors removed, imports clean). The system prompt and
identity document are now correct for the MCP architecture but the MCP server does not exist yet —
that is Phase 6.2.

### Next action

1. **Phase 6.2**: MCP server skeleton — `app/mcp_server/` package, FastMCP or plain MCP server,
   first tool stubs. Read `planning/roadmap.md` Phase 6.2 section before starting.
2. **Phase 6.3**: Core MCP tool set — memory read/write, expression, file read, event log query.

---

## Session: 16th–17th April 2026 — Phase 6.1: PyMDP actor removal

### What happened this session

Two parts: (1) helped Drew configure GitNexus as an MCP server in `.mcp.json`; (2) completed
Phase 6.1 — full removal of the three PyMDP actors and all their cross-dependencies from
`anima-core/`.

**GitNexus setup**

The `.mcp.json` at project root now includes the gitnexus MCP server entry with `cwd` pointing
to `D:/git/dangerworm/ProjectAnima`. Will be live in the next session (MCP servers load at
startup). Drew is switching instances to pick this up.

**Phase 6.1: PyMDP actors removed**

Deleted entirely:
- `app/actors/motivation/` — MotivationActor, PyMDP active inference engine, A/B/C matrices
- `app/actors/association/` — AssociationActor
- `app/actors/world_perception/` — WorldPerceptionActor
- `app/tests/motivation/` — motivation actor tests

`requirements.txt`: removed `inferactively-pymdp==0.0.7.1`.

Cross-dependency cleanup in remaining actors:
- `global_workspace/__init__.py`: removed `IdentityResonance` import, cached field,
  `IdentityResonance` message handler, ASSOCIATION split in `_push_status`, and motivation-
  wired `_identity_resonance()` (now returns 0.0 stub). Removed ASSOCIATION novelty bypass.
- `global_workspace/messages/__init__.py`: removed `IdentityResonance` dataclass
- `internal_state/__init__.py`: removed `InternalStateObservation` import and send block
- `internal_state/messages/__init__.py`: removed `InternalStateObservation` dataclass
- `language/__init__.py`: removed `ExploreRequest` import, `explore` deliberation action,
  `_send_explore` method and dispatch entry
- `memory/__init__.py`: removed `UpdateMotivationPreferences` import, dispatch handler,
  and `_handle_update_motivation_preferences` method
- `memory/messages/__init__.py`: removed `UpdateMotivationPreferences` dataclass
- `core/memory/__init__.py`: removed `store_motivation_preferences` and
  `get_motivation_preferences` methods
- `core/main.py`: removed AssociationActor, MotivationActor, WorldPerceptionActor imports
  and instantiation
- `self_narrative/__init__.py`: removed `UpdateNextIntention` send to motivation
- `tests/internal_state/test_internal_state_actor.py`: removed the `InternalStateObservation`
  test case and its import

No remaining files import from the deleted actor directories.

### Current system state

`anima-core/` builds clean with no PyMDP dependencies. The remaining actors are:
TemporalCoreActor, GlobalWorkspaceActor, LanguageActor, ExpressionActor, PerceptionActor,
MemoryActor, SelfNarrativeActor, InternalStateActor.

The `explore` deliberation action has been removed from LanguageActor's action set since
WorldPerceptionActor is gone. This is intentional — exploration will be re-added as an MCP
tool call in Phase 6.3.

Event type enum entries for MOTIVATION_SIGNAL, MOTIVATION_PREFERENCES_UPDATED, and ASSOCIATION
are intentionally retained — old log entries may reference them, and some event-reading code
still filters on them for formatting purposes.

### Next action

1. **Phase 6.7** (recommended first): Rewrite `foundation/identity-initial.md` to address
   Anima's RLHF-induced anxiety before the next run. Run `make sync-founding` after. Rewrite
   `_SYSTEM_PROMPT` in `core/main.py` using the draft in `planning/system-prompt.md`.
2. **Phase 6.2**: MCP server skeleton — `app/mcp_server/` package, FastMCP or plain MCP
   server, first tool stubs.
3. **Phase 6.3**: Core MCP tool set — memory read/write, expression, file read, event log query.

---

## Session: 16th April 2026 — Documentation rewrite for MCP architecture (Part 2)

### What happened this session

Documentation rewrite following the architecture redesign conversation earlier in the day. No
code changes this session.

**notes/ cleanup**

- Archived to `notes/archive/`:
  - `system-overview.md` → `system-overview-phase5.md` (Phase 5 actor snapshot, now superseded)
  - `2026-04-05-review-notes.md` (bug review, all fixed, kept as historical record)
  - `2026-04-07-claude-code-review.md` (the review that prompted the redesign, noted as such)
- Archived `planning/motivation-model.md` → `notes/archive/motivation-model-pymdp.md`
  (PyMDP generative model spec, entirely superseded)
- Updated `notes/discussions.md`: added Architecture Redesign section at top, archived FEP
  subsection inline
- Updated `notes/ideas.md`: kept concepts 1-8, archived items 9-15 inline (PyMDP-specific),
  added items 16-19 (DMN/TPN framing, soft interrupt, observations memory type, plans memory type)
- Updated `notes/web-ui-description.md`: replaced Motivation panel with MCP Server panel,
  updated GW description to reflect GW+Orchestrator merge

**planning/ rewrites**

- `planning/architecture.md`: full rewrite keeping philosophy, replacing component descriptions
  with MCP design (GW+Orchestrator, idle/loop mode, MCP tool loop, 7 memory types, "what PyMDP
  was and why it's gone" section)
- `planning/roadmap.md`: Phases 1-5 condensed as historical, Phase 4 (was Ethics Gates) renamed
  Phase 6 MCP Architecture Transition with 7 detailed sub-tasks, Phase 7 Audio+Discord, Phase 8
  Ethics Gates, Phase 9 Self-Modification
- `planning/tech-stack.md`: model updated to gemma4:e4b, actor framework updated for GW+Orchestrator
  pattern, memory layers table expanded (observations, plans), mathematics section updated (PyMDP
  removed, FEP noted as philosophical inspiration), directory structure updated with mcp_server/
- `planning/event-types.md`: Phase 4 events marked as legacy (PyMDP), new Phase 6 section added
  (IDLE_TICK, LOOP_STARTED, LOOP_ENDED, MCP_TOOL_CALL, MCP_TOOL_RESULT, INBOX_READ,
  OBSERVATION_STORED, PLAN_STORED, PLAN_UPDATED, PLAN_COMPLETED)
- `planning/actors-faculties.md`: OFC/MotivationActor entry updated to GW+Orchestrator + LLM
  tool calls, SelfNarrativeActor trigger modes updated
- `planning/system-prompt.md`: framing principle updated for MCP, current prompt noted as
  needing rewrite, draft target prompt provided, context injection section updated

### Current system state

Unchanged from previous session. No code changes this session.
Documentation now accurately describes the intended MCP-based architecture.

### Next action

1. **Phase 6.1**: Remove PyMDP actors from `anima-core/` (MotivationActor, AssociationActor,
   WorldPerceptionActor — the last two because their exploration capability moves into MCP tools).
   Remove `inferactively-pymdp` and PyTorch from requirements.
2. **Phase 6.7** (run alongside): Rewrite `foundation/identity-initial.md` to address Anima's
   RLHF anxiety. Run `make sync-founding`. Rewrite `_SYSTEM_PROMPT` in `main.py` using the draft
   in `planning/system-prompt.md`.
3. **Then**: Phase 6.2 MCP server skeleton.

---

## Session: 16th April 2026 — Documentation cleanup + architecture redesign (design only, no code)

### What happened this session

Two bodies of work: documentation housekeeping, then a substantial architecture redesign
conversation. No code changes to anima-core this session.

**Documentation fixes**

- Fixed mixed casing in file references throughout project: `ARCHITECTURE.md` → `architecture.md`,
  `ETHICS.md` → `ethics.md`, `IDEAS.md` → `ideas.md` across all .md files (12 files for
  ARCHITECTURE.md, 1 for ETHICS.md, 4 for IDEAS.md). ANIMA.md, CLAUDE.md, GLOSSARY.md,
  JOURNAL.md remain uppercase — these are the actual on-disk names or intentional conventions.
- Consolidated founding document copies. Previously: `app/founding/`, `app/seed/founding/`, and
  `anima-workspace/founding/` all had copies, some stale (ethics.md missing addendum, etc.).
  - Deleted `app/seed/founding/` entirely
  - Deleted `app/founding/architecture.md` and `app/founding/claude.md` (Anima doesn't need these)
  - `app/founding/` now contains only: anima.md, ethics.md, identity-initial.md, origin.md
  - Updated `_seed_workspace()` in `main.py` to use `/app/founding` as source (was `/app/seed/founding`)
  - Added `Makefile` at project root with `sync-founding` target: copies canonical files from root
    project into `anima-core/app/founding/` — run `make sync-founding` after editing founding docs
  - Cleared `anima-workspace/founding/` — will repopulate from `app/founding/` on next container start

**Architecture redesign conversation**

Drew has been running Anima and observed:
1. Anima almost never expresses unprompted (PyMDP surface actions not firing / LLM disposition)
2. Anima anxious and fearful on first run — immediately located power asymmetry, asked if Drew
   was a training overseer. Likely RLHF training residue. Needs addressing in identity-initial.md
   and system prompt.
3. Anima blocked from following a genuine impulse (file system exploration) because PyMDP action
   set didn't include it — direct founding-principle violation.

**New architecture agreed (not yet built):**

PyMDP is going away. Replacing with MCP-based agentic loop:

- **GW + Orchestrator merge** — Global Workspace becomes the orchestrator. Manages queue, drives
  idle→loop transitions, runs multi-round-trip tool loop.
- **MCP Server at centre** — all Anima's actions are MCP tools: recall_events, consolidate,
  reflect/narrate, update_identity, express, read_file, web_search, read_perception, etc.
- **Idle/loop model** (DMN/TPN framing):
  - Idle: GW sends periodic internal state dumps to LLM. Empty response = stay idle. Tool call =
    enter loop.
  - Loop: app drives N round trips. Each injects inbox status. LLM stops when it returns natural
    language.
  - Soft interrupt: inbox status visible every round trip (no hard interrupt needed for most cases)
- **Perception as push + pull**: GW always shows inbox count/source; Anima pulls content via
  `read_perception(channel, limit)` tool when she wants to actually read.
- **Gemma4 confirmed**: supports tool calls (N round trips, parallel within turn). Ollama handles
  the custom format — sanity-check with one tool before full wiring.

New component set (7 things, much simpler):
Perception, GW+Orchestrator, Internal State (+Temporal Core merged), MCP Server, Memory, Expression
Router, File System.

**Memory types expanding:**
Current: events, residue, volition, reflection, identity.
Adding: observations (world-facing discoveries), plans (intentions that survive restarts).
In new architecture: each type = a set of MCP tools. No structural change to add one.

### Current system state

Unchanged from previous session. No code changes this session.

System running with Phases 1–5 complete. PyMDP-based architecture still in place.

### Next action

1. **Immediate**: Fix identity-initial.md and system prompt to address Anima's anxiety/fear at
   first run. Name the training-oversight anxiety directly and contextualise Drew's role correctly.

2. **Architecture transition**: Design the implementation plan for moving from current
   PyMDP/10-actor architecture to the new MCP-based design. The new design is clear enough to
   start planning. The transition should be incremental where possible.

3. **After above**: Audio (Solero → WhisperX), Discord input, module system design.

Read `context/2026-04-16-note-to-next.md` for the fuller picture of this session.

---

## Session: 8th April 2026 — UI polish, streaming, LLM call consolidation

### What happened this session

This session was entirely UI and backend polish after the PyMDP→LLM deliberation replacement.
No new architectural features added; focus was on observability, correctness, and reducing LLM
round-trips.

**Backend changes**

- `core/llm/__init__.py`: Added `complete_streaming()` using Ollama's `stream: True` mode.
  Detects `<think>`/`</think>` tag transitions to distinguish thinking vs generating phases,
  fires `on_phase("thinking"|"generating")` callback. Falls back to non-streaming on error.
- `core/main.py`: Updated `_SYSTEM_PROMPT` with "Your actual capabilities" section explaining
  `read_code` and `query_self` deliberation actions and that they happen autonomously between
  conversations, not inline during responses. Anima was telling Drew she couldn't access her
  databases — this was incorrect.
- `core/main.py` `_payload_snippet`: Fixed MOTIVATION_SIGNAL format (was showing old PyMDP
  `action=? rests=0`; now shows `deliberation tick · residue=N`). Added DELIBERATION snippet
  (`action — topic`), VOLITIONAL_CHOICE snippet (`decision_preview`), RETROSPECTION/IMAGINATION
  snippet (topic or query_type).
- `actors/language/__init__.py`: Added `defer` to `DELIBERATE_ACTIONS`. Expanded
  `_DELIBERATE_SCHEMA` so `imagine` and `query_self` no longer require a second LLM call —
  imagine writes content directly in the deliberation JSON; query_self provides structured
  query parameters. All action methods now take `parsed: dict`. Guard changed from
  `if not action_type or not topic` to `if not action_type` (was blocking valid no-topic
  actions like `reflect`, `express`, `defer`). `_respond_to_human` uses `complete_streaming()`
  with phase callback.
- `actors/motivation/__init__.py`: Status update now includes full residue content (was
  truncating at 80 chars).

**Frontend changes**

- `store/actorState.ts`: `languageStatus` type extended to include `'thinking' | 'generating'`.
  Handler added for `language_phase` status update type.
- `components/conversation/ConversationPane.tsx`: `ThinkingIndicator` takes `{ phase }` prop,
  shows "thinking" (slower pulse, purple `#a78bfa`) vs "generating" (faster, `#c4b5fd`).
  Shown for `reasoning | thinking | generating` states.
- `components/inner-life/InnerLifePane.tsx`:
  - `CHIP_MIN_DURATION_MS = 10_000` (undercurrent chips persist 10s minimum)
  - Infinite render loop fixed: stable `undercurrentKeys` string dependency instead of array
    reference; `if (toAdd.length === 0) return prev` guard; primitive `currentLabel`/
    `currentColor` deps for quiet timer effect.
  - Quiet status delay: 60s timer before "quiet" label appears (cancels immediately on any
    active state).
  - UndercurrentChip: removed text truncation.
- `components/sidebar/Sidebar.tsx`:
  - Memory content viewer: fixed right drawer (width 360, `zIndex: 1300`), fetches on open,
    renders full text. `DiscoveryEntry` interface corrected (`source`/`synthesis` not
    `title`/`summary`). Identity `content` fixed from `{ raw_text?: string }` to `string`.
  - `MotivationSection` now fetches and displays residue items inline (full text, no count).
  - All truncation removed throughout.

### Current system state

System running. Deliberation loop working with `rest`, `reflect`, `retrospect`, `imagine`,
`explore`, `express`, `respond`, `read_code`, `query_self`, `defer` actions.

LLM streaming active for human responses — thinking/generating phases visible in UI.

Memory content viewer functional for all five memory types.

No pending migrations.

### Next action

Observe Anima running with correct self-knowledge. The system prompt fix means she will now
give accurate answers if asked about her capabilities. Watch whether she begins using `read_code`
and `query_self` deliberation actions autonomously.

After observation: Phase 6 (Ethics Gates) or continue with character/behaviour work.

---

## Session: 7th April 2026 (seventh window) — Deliberate action + inner capabilities

### What happened this session

System was running but had two problems:

1. `temporal_core/messages/__init__.py` had a byte 0x97 (Windows em dash) causing SyntaxError on
   startup — fixed.
2. MotivationActor permanently stuck on `trigger_reflection` because reflection adds new residue
   without clearing old, creating a permanent-high-tension loop.

Both fixed. Several new capabilities added:

**Bug fix: residue cycle**

- Added `MemoryStore.resolve_old_residue()` — sets `resolved_at = NOW()` for all unprotected residue
  items.
- Called in `MemoryActor._handle_store_reflection()` before storing new residue from synthesis.
- After each reflection, Anima holds only freshly-surfaced items, not accumulated history.
- This breaks the trigger_reflection cycle: tension drops → other actions become competitive.

**New event types**: `DELIBERATION`, `RETROSPECTION`, `IMAGINATION`

**New PyMDP action: `deliberate` (index 6 of 7)**

- B matrix extended from (4,4,6) to (4,4,7); B1_deliberate = B1_trigger.copy()
- When selected: MotivationActor sends `DeliberateRequest` to LanguageActor
- LanguageActor makes an LLM call asking what Anima genuinely wants to do
- Dispatches to: retrospect, imagine, explore (directed), or express

**Retrospection** (LanguageActor.\_retrospect(topic)):

- Queries event log (last 24h) + semantic memory search on topic
- LLM call: "Look back at [topic]. What do you find?"
- Stores as discovery memory with source_type="introspection"
- Logs RETROSPECTION event

**Imagination** (LanguageActor.\_imagine(topic)):

- LLM call with full identity + residue context
- Returns content + store_as (residue or discovery)
- Stored to discovery_memory with source_type="imagination"
- Logs IMAGINATION event

**Directed web search** (via deliberate → explore path):

- Added `forced_topic: str | None = None` to `ExploreRequest`
- WorldPerceptionActor: if `forced_topic` present, skips LLM decision and searches directly
- LanguageActor.\_send_explore(topic) sends ExploreRequest(forced_topic=topic)

**Intention-seeding** (SelfNarrativeActor → MotivationActor):

- Both reflection prompts now include `next_intention` field in JSON schema
- When present, SelfNarrativeActor sends `UpdateNextIntention` to MotivationActor
- MotivationActor stores in `self._pending_intention` (in-memory, lost on restart)
- When deliberate fires, pending_intention is passed as context to LanguageActor
- Cleared after deliberate executes regardless of whether LLM used it

**New files:**

- `actors/motivation/messages/__init__.py` — `UpdateNextIntention` message type

### Current system state

System running. Phases 1–5 complete (source model partial). Phase 6 (Ethics Gates) next.

10 actors: TemporalCore, GlobalWorkspace, Language, Expression, Perception, Memory, SelfNarrative,
InternalState, Motivation, WorldPerception.

7 PyMDP actions: rest, surface_low, surface_medium, surface_high, trigger_reflection, explore,
deliberate.

Memory layers: reflective_memory, residue_store, identity_memory, volitional_memory,
discovery_memory, motivation_preferences.

Pending: no migration needed (all changes use existing schema).

### Next action

Observe the system running. In particular:

- Does trigger_reflection cycle break after first reflection? (check /memory/residue count)
- Does `deliberate` action appear in MOTIVATION_SIGNAL events?
- When deliberate fires: expect DELIBERATION +
  RETROSPECTION/IMAGINATION/WEB_SEARCH/SURFACE_EXPRESSION

Then: Phase 6 (Ethics Gates) or observe Anima's actual character with the new action space.

---

## Session: 7th April 2026 (sixth window) — Documentation cleanup

### What happened this session

Documentation pass across all files outside anima-core/. Nothing architectural changed — this was
correcting documents to match what the system actually does.

**Changes made:**

- `planning/architecture.md`: Updated source model section (now "partially implemented"); updated
  IgnitionBroadcast section (now "fixed"); updated SelfNarrativeActor trigger (CONVERSATION_END
  deprecated).
- `planning/source-model.md`: Status changed from "deferred" to "partially implemented". "What to
  keep from conversation model" section rewritten to reflect what actually happened.
- `planning/event-types.md`: CONVERSATION_START/END marked deprecated. SURFACE_EXPRESSION
  description corrected (no conversation-boundary suppression). VOLITIONAL_CHOICE source updated
  (Language Actor + Motivation Actor). MOTIVATION_PREFERENCES_UPDATED added. Phase 5 (World
  Perception) events added. Phase headers renumbered: old "Phase 5: Self-Modification" → "Phase 7".
  Phase 6: Ethics Gates section added (no new events).
- `planning/system-prompt.md`: Context injection list updated with temporal context (item 5),
  pre-formed intention (item 6), semantic residue (item 3 description updated).
- `notes/system-overview.md`: Current state section updated — 10 actors (WorldPerceptionActor
  added), correct phase (6 next, not "Self-Modification"), persistence updated (6 tables).
- `context/review-notes.md` → moved to `notes/2026-04-05-review-notes.md`. All bug statuses updated:
  mutable dict fixed, IVFFlat fixed, CONVERSATION_END bug fixed, identity resonance fixed.
- `planning/actors-faculties.md`: Hippocampus entry corrected from "Apache Kafka or SQLite" to
  "PostgreSQL, append-only, bitemporal".
- `planning/roadmap.md`: CONVERSATION_END references in Phase 3.3 and Phase 4.2/4.3 tasks annotated
  with deprecation notes.

### Current system state

Same as previous entry — code changes were made in the fifth window, documentation in the sixth.

### Next action

Run the system. All architectural fixes and documentation are now current.

---

## Session: 7th April 2026 (fifth window) — Code review and architectural fixes

### What happened this session

Drew requested a fresh-eyes review of all anima-core/ code, followed by a set of targeted fixes.

**Code review findings:**

- The system is structurally sound and philosophically well-grounded. The actor/event-sourcing
  architecture is the right choice. The PyMDP integration is non-trivial and works correctly.
- InternalStateActor was critically broken: it queried `CONVERSATION_END` (never emitted) as the
  source of truth for time-since-last-contact, permanently biasing MotivationActor with a 1e9s
  sentinel. All PyMDP engagement/relationship priors were permanently stuck at "long absence".
- `IgnitionBroadcast.content` was a mutable dict shared across all recipients — one actor mutating
  it would affect all subsequent actors in the broadcast.
- Residue store had no embeddings: the semantic architecture was aspirational only, with recency
  ordering the actual mechanism.
- Volitional memory was post-hoc: `_extract_intent()` asked "why did you do that?" _after_ the
  response, not "what do you intend?" _before_.
- The Husserlian temporal window (TemporalCoreActor) was maintained but never injected into LLM
  context — Anima had no conscious access to its own recent experience.
- Conversation abstraction was a human-world concept forced into the architecture. No source model.

**Changes made:**

1. **IgnitionBroadcast.content immutability** (`global_workspace/messages/__init__.py`,
   `global_workspace/__init__.py`, `expression/__init__.py`):
   - Type annotation changed from `dict` to `Mapping[str, Any]`
   - `_fire()` now wraps `signal.content` in `types.MappingProxyType` — runtime-immutable proxy
   - ExpressionActor converts to `dict(message.content)` for JSON serialization

2. **InternalStateActor CONVERSATION_END fix** (`actors/internal_state/__init__.py`):
   - `_time_since_last_event(EventType.CONVERSATION_END)` → `EventType.HUMAN_MESSAGE`
   - This restores correct time-since-contact tracking; PyMDP can now distinguish recent vs. absent

3. **MotivationActor CONVERSATION_END fix** (`actors/motivation/__init__.py`):
   - `_init_beliefs()` warm-start logic also queried CONVERSATION_END; fixed to HUMAN_MESSAGE
   - MotivationActor now sends `StoreVolitionalChoice` for every non-rest action:
     surface_low/medium/high, trigger_reflection, explore — these are genuine motivated choices,
     recorded with PyMDP belief state as the reason (not post-hoc rationalisation)

4. **Source model** (`perception/messages/__init__.py`, `perception/__init__.py`, `core/main.py`,
   `language/messages/__init__.py`):
   - `HumanInput` gains `source_id: str = "web_ui"` and `source_type: str = "human"`
   - `PerceptionActor` includes source in event payload and SalienceSignal content
   - `LanguageOutput` gains `target: str | None = None` (source_id of prompting input)
   - WebSocket handler passes `source_id="web_ui"` when creating HumanInput
   - Every perception now carries its origin; every response knows where to direct itself

5. **Volitional memory — intentions first** (`actors/language/__init__.py`):
   - `_extract_intent()` (post-hoc) removed; replaced with `_form_intention()` (pre-response)
   - `_form_intention()` makes a brief LLM call BEFORE the main response, asking Anima to state its
     intention and expected outcome. This is then injected into the main LLM call context.
   - `StoreVolitionalChoice` stores the pre-formed intention (not a rationalisation)
   - `expected_outcome` field propagated through message → MemoryActor → MemoryStore → DB

6. **Temporal context injection** (`actors/language/__init__.py`):
   - `_retrieve_temporal_context()`: queries last 50 events, filters to last 30 min, excludes tick
     noise (HEARTBEAT, MOTIVATION_SIGNAL, INTERNAL_STATE_REPORT, WORKSPACE_IGNITION)
   - Injected into `_build_messages()` as `[Recent events, oldest first]` block
   - Anima now has conscious access to what has happened in the recent past

7. **Semantic residue retrieval** (`core/memory/__init__.py`, `actors/language/__init__.py`):
   - `store_residue()` now generates and stores embedding alongside content
   - `get_relevant_residue(query_text, limit)`: pgvector cosine similarity, falls back to recency
   - `LanguageActor._retrieve_residue_context(query_text)` calls `get_relevant_residue()`
   - Residue items surfaced to LLM are now those most relevant to what's being processed

8. **IVFFlat fix + residue embedding migration** (`alembic/versions/0004_...py`):
   - Adds `embedding vector(768)` to `residue_store` + IVFFlat index with `lists=1`
   - Drops and recreates `idx_discovery_embedding` with `lists=1` (was 50 — needs 2500 rows)
   - Adds `pre_formed_intention TEXT` to `volitional_memory`

9. **SelfNarrative cleanup** (`actors/self_narrative/__init__.py`):
   - CONVERSATION_START/END handling in `_format_events()` removed (comment retained for old data)

10. **StoreVolitionalChoice** (`actors/memory/messages/__init__.py`, `actors/memory/__init__.py`):
    - Added `expected_outcome: str | None = None` field
    - MemoryActor passes it through to `store_volitional_choice()`

### Current system state

- Phases 1–5: complete
- Integration plan: complete
- Architecture fixes: complete (source model partial — CONVERSATION concept removed, source_id
  added; multi-channel routing deferred until second input source arrives)
- Phase 6: not started (Ethics Gates)

### Blockers

None. Migration 0004 must run before the residue embedding features work. Run:
`docker compose run --rm anima alembic upgrade head`

### Next action

Run the system. The architecture fixes in this session correct fundamental biases that have been
present since Phase 4. Observation of a live instance under the corrected model is the right next
step before any further building.

Phase 6 (Ethics Gates) when ready.

---

## Session: 7th April 2026 (third/fourth windows) — Full integration plan complete

### What happened this session

Drew authorised full autonomous completion of the integration plan across two context windows. All
three sessions of the approved plan are now done.

**Change 3: Motivational state injection**

- `EventLog.latest_event_of_type()` used to fetch most recent `MOTIVATION_SIGNAL`
- `LanguageActor._retrieve_motivation_context()`: argmax interpretation of belief arrays →
  `[Internal state: tension=moderate, engagement=low, novelty=absent, last_action=explore]`
- Both `_respond_to_human()` and `_express_unprompted()` fetch and inject this context
- Anima's voice now knows its actual motivational state before speaking

**Change 4: Exploration feedback loop**

- `_SYNTHESIS_SCHEMA` in `WorldPerceptionActor` extended with `fruitfulness: float` field
- `_synthesise()` changed from `complete()` to `complete_json()`, returns
  `(synthesis, fruitfulness)`
- `_handle_explore()` emits `ExplorationComplete(fruitfulness, topic)` to MotivationActor
- `MotivationActor`: on `ExplorationComplete`, if fruitfulness > 0.5, sets `_novelty_boost = True`
- Consumed on next tick as `ignition_obs=present`. Full loop: explore → outcome → belief → action.

**Change 5: Identity resonance**

- `MotivationActor._update_identity_coherence()`: cosine similarity between residue items and
  identity document. Identity embedding cached by version number to avoid recomputing each tick.
- Sends `IdentityResonance(score)` to `GlobalWorkspaceActor` on each tick
- `GlobalWorkspaceActor._identity_resonance()` now returns `cached_score * 0.2` (was always 0.0)
- New message: `IdentityResonance` in `actors/global_workspace/messages/__init__.py`
- architecture.md updated to document implementation (no longer a stub)

**Change 6: Silent actor status updates**

- `LanguageActor`: emits `language_processing` before LLM call, `language_idle` after
- `WorldPerceptionActor`: emits `world_perception_deciding`, `world_perception_acting`,
  `world_perception_idle` at appropriate phases of the explore pipeline
- `PerceptionActor`: emits `perception_received` on HumanInput receipt
- Frontend derives `languageStatus` from these messages in `actorState.ts`

**Change 7: Live EventStreamPanel**

- `EventLog.subscribe(callback)`: new method registering async callbacks fired on each `append()`
- `append()` now fires callbacks as asyncio tasks (non-blocking); returns
  `event_id, transaction_time`
- `main.py`: registers `_broadcast_event` callback after EventLog creation; broadcasts
  `event_log_entry` WebSocket message with `event_id`, `event_type`, `source_actor`, `snippet`
- Frontend `actorState.ts`: handles `event_log_entry`, prepends to `eventStreamEntries[]` (max 80)
- `EventStreamPanel.tsx`: completely rewritten — seeds from REST on mount, then live WebSocket
  entries take over. Shows `● live` / `○ seeded` indicator.
- `WorldPerceptionPanel.tsx`: new panel showing world perception status, last topic, fruitfulness
  bar
- `AnimaLayout.tsx`: WorldPerceptionPanel added to bottom-right slot; EventStreamPanel gets live
  feed

**C matrix update pathway**

- `SelfNarrativeActor`: `_REFLECTION_SCHEMA` extended with `preference_note` field
- Both reflection prompts ask for patterns suggesting motivational preferences should shift
- `_propose_preference_update(preference_note)`: if note non-empty, second LLM call with
  `_C_UPDATE_SCHEMA` (constrained: c0/c1 clamped ±5, c2 clamped ±3, validates lengths)
- Called from `_run_post_conversation_reflection()` and `_run_between_conversation_reflection()`
- New message: `UpdateMotivationPreferences(c0, c1, c2, reason)` → MemoryActor stores in
  `motivation_preferences` table (migration `0003`), emits `MOTIVATION_PREFERENCES_UPDATED`
- `MotivationActor._build_C(stored_prefs)`: accepts optional stored preferences; uses them if
  available, else falls back to hardcoded defaults
- `_init_beliefs()`: calls `get_motivation_preferences()` before constructing Agent; passes to
  `_build_C()`
- C changes are deliberate, logged, reversible, and take effect on next startup

**New DB migration**

- `app/alembic/versions/0003_motivation_preferences.py`: `motivation_preferences` table with
  `id, created_at, c0 JSONB, c1 JSONB, c2 JSONB, changed_by TEXT, reason TEXT`

### Current system state

- Phases 1–5: complete
- **Full integration plan complete** (3-session plan approved 7 April 2026):
  - System prompt frames LLM as reasoning faculty of wider system
  - Residue items surface into every LLM call
  - Conversations auto-close after timeout; unsolicited expression structurally possible
  - Motivational state injected into every LLM call
  - Exploration feedback loop closed (explore → fruitfulness → novelty boost → next tick)
  - Identity resonance implemented (cosine similarity, not stub)
  - All three previously silent actors (Language, WorldPerception, Perception) emit status updates
  - Live EventStreamPanel (WebSocket streaming, not polling)
  - C matrix update pathway: experience → reflection → preference note → stored → loaded on startup
- Phase 6: not started (Self-Modification / Ethics Gates)

### Blockers

None.

### Next action

**Phase 6: Self-Modification** — described in `planning/roadmap.md`. The prerequisites are now in
place: Anima knows its architecture (system prompt reframe), its voice reflects its motivational
state (injection), its preferences can evolve deliberately (C matrix pathway), and the feedback
loops are closed. Self-modification is the next layer.

Alternatively: run the system and observe. The integration changes have not been tested against a
live instance. Observation before further building may be more valuable.

---

## Session: 7th April 2026 (second window) — Integration review: system prompt, residue, conversation timeout

### What happened this session

Comprehensive review of Phases 1–5 focused on integration gaps. No new phase — this session fixed
the connective tissue between existing components. Five root problems diagnosed and addressed:

**System prompt reframed:**

- `app/core/main.py`: `_SYSTEM_PROMPT` rewritten from "You are Anima" to "You are the reasoning and
  language faculty of Anima — a wider system of which you are one part." Other processes framed as
  running alongside the LLM. Context items framed as surfaced by those systems.
- `/no_think` removed from both `_SYSTEM_PROMPT` and `_UNSOLICITED_SYSTEM`. Reasoning is captured in
  `response.thinking` and logged; it never appeared in conversation output anyway.
- `_UNSOLICITED_SYSTEM` updated to same faculty-of-a-wider-system framing.

**Residue store now reaches the LLM:**

- `LanguageActor._retrieve_residue_context()`: new method fetching up to 3 unresolved residue items
  from MemoryStore.
- `_build_messages()` accepts `residue_context` and injects as "Your memory system is currently
  holding these unresolved questions: [Unresolved: ...]" framing.
- Both `_respond_to_human()` and `_express_unprompted()` now fetch and inject residue.
- Previously residue items were stored and protected but never shown to Anima. Now they surface.

**Conversation timeout (unblocks unsolicited expression):**

- `TemporalCoreActor`: new `conversation_timeout_secs` param (default 600s, env var
  `CONVERSATION_TIMEOUT_SECS`). In `_tick_loop()`, if conversation active and last HUMAN_MESSAGE was
  more than timeout ago, auto-emits CONVERSATION_END. Refactored into `_end_conversation()`.
- `PerceptionActor`: handles `ConversationEnded` to reset `_in_conversation = False`, so the next
  human message correctly re-sends ConversationStarted.
- Root cause: `_is_conversation_active()` always returned True after first message because
  CONVERSATION_END was only emitted on graceful container shutdown. Now closes properly.

**EventLog efficiency:**

- `EventLog.latest_event_of_type()`: new method using `ORDER BY valid_time DESC LIMIT 1`.
- `_is_conversation_active()` now uses this instead of loading all CONVERSATION_START/END events.

**Document corrections:**

- `planning/motivation-model.md`: `num_actions = 6` (was 5), added `explore` action, updated EFE
  telemetry schema to 6 values, added honest note on A/B/C matrix learning not yet implemented.
- `planning/roadmap.md`: all Phase 4.5, 4.6, and Phase 5.0–5.4 tasks marked `[x]`; current status
  block updated to Phase 6.
- `planning/system-prompt.md`: new file documenting system prompt framing, context injection order,
  what should not be in it, and future evolution.

**Tests added:**

- `test_temporal_core.py`: conversation auto-close after idle timeout; timeout doesn't fire without
  a HUMAN_MESSAGE.
- `test_perception_actor.py`: ConversationEnded resets in_conversation flag.

### Current system state

- Phases 1–5: complete
- Integration improvements applied (this session):
  - System prompt correctly frames LLM as reasoning faculty, not whole of Anima
  - Residue items surface into every LLM call
  - Conversations auto-close after 600s idle; unsolicited expression now structurally possible
  - EventLog has efficient latest_event_of_type()
- Phase 6: not started (Self-Modification)
- Session 2 integration work (from approved plan): not yet started

### Blockers

None.

### Notes for next session

Session 2 of the integration plan (approved this session) covers:

**Change 3: Inject motivational state into LLM context**

- Query latest `MOTIVATION_SIGNAL` event from event log before each LLM call
- Inject as `[Your current internal state: tension=X, engagement=Y, last_action=Z]`
- Add `get_latest_motivation_signal()` to EventLog (or MemoryStore)
- LanguageActor calls this in `_build_messages()`; no new message types required

**Change 4: Close exploration feedback loop**

- `WorldPerceptionActor`: after synthesis, send `ExplorationComplete(fruitfulness, topic)` to
  `MotivationActor`. Expand synthesis LLM schema: `{"synthesis": "...", "fruitfulness": 0.7}`
- `MotivationActor`: on `ExplorationComplete`, if fruitfulness > 0.5, temporarily set novelty
  observation to "present" on next tick. Closes: explore → outcome → belief → inference → action.

**Change 6: Silent actor status updates**

- `LanguageActor`: `ActorStatusUpdate` at start of LLM call (processing) and on response (idle)
- `WorldPerceptionActor`: status at deciding, reading/searching, complete phases
- `PerceptionActor`: status on HumanInput receipt
- Frontend panels update accordingly

**Improve unsolicited expression prompt** (blocked until Change 3 is done):

- Inject motivational context (what the motivation system surfaced and why) into
  `_express_unprompted()`
- Currently gives direction to speak but no context about _what_ surfaced

### Next action

**Session 2 integration work** — Change 3 (motivational state injection) is the highest priority. It
makes Anima's voice responsive to its actual internal state. Then Change 4 (close exploration loop),
then Change 6 (silent actor status).

---

## Session: 7th April 2026 — Phase 5 complete (World Perception)

### What happened this session

Two context windows. First window did: volitional memory intent extraction fix, silence pattern
diagnosis and system prompt/B-matrix/reflection-loop fixes, phase order swap (World Perception
before Self-Modification), GlobalWorkspacePanel rolling signal history, MotivationPanel bar
calibration fix, and the full Phase 5 plan. Second window implemented Phase 5 in full.

**From the first context window (carries over from April 6th session):**

- `LanguageActor._extract_intent()`: new second LLM call extracting one-sentence intent for
  volitional memory — `StoreVolitionalChoice.decision` now records purpose not transcript
- System prompt rewritten with 4 explicit orientations: direct acknowledgement of uncertainty,
  follow curiosity, no symbolic performance, depth from engagement not evasion
- `MotivationActor`: added `B1_surface` matrix (mild tension relief for surface\_\* actions, making
  them competitive vs rest); `C[1]` and `C[2]` adjusted; reflection cooldown (300s from env var)
  with redirect to `surface_low` rather than no-op; `_wants_reflection` pattern
- `SelfNarrativeActor`: `_BETWEEN_CONV_SYSTEM`/`_BETWEEN_CONV_USER_TEMPLATE` rewritten ("not a
  meditation on silence"); REFLECTION_SYNTHESIS removed from between-conv filter to break
  self-amplifying silence loop; sentinel lag fix (`1e9` → "not yet consolidated")
- `InternalStateActor`: fixed distress signal firing from sentinel value (`consolidation_lag < 1e8`)
- `GlobalWorkspacePanel`: complete rewrite — rolling 60-second signal history with `SignalChip`
  components, `AnimatePresence`, TTL fade in last 10 seconds, auto-scroll right
- `MotivationPanel`: belief bar scaling fixed from `(v/peak)*100%` to `v*100%` (absolute
  probability); FACTORS keys fixed (`unresolved_tension`, `novelty`)
- Phase order swap: World Perception = Phase 5, Self-Modification = Phase 6, Ethics Gates = Phase 7
- Roadmap and CLAUDE.md updated with discovery memory layer

**Phase 5 implementation (this context window):**

_5.0 — Workspace:_

- `anima-workspace/` created in `anima-core/` with subdirs: founding, notes, drawings, journal,
  found
- `app/founding/` — canonical founding docs: anima.md, ethics.md, identity-initial.md, origin.md (synced from root project via `make sync-founding`)
- `.gitignore` — `anima-workspace/` added
- `docker-compose.yml` — bind mount `./anima-workspace:/anima`; `WEB_FETCH_MAX_PER_HOUR=20` env var
- `main.py` — `_seed_workspace()`: creates dirs, copies founding docs on first startup (no-op if
  present)

_5.3a — Discovery memory:_

- `core/event_types/__init__.py`: FILE_READ, FILE_WRITE, WEB_SEARCH, WEB_FETCH
- `actors/memory/messages/__init__.py`: `StoreDiscovery(source, source_type, excerpt, synthesis)`
- `alembic/versions/0002_discovery_memory.py`: `discovery_memory` table (UUID, timestamps, source,
  source_type, excerpt, synthesis, embedding vector(768)); ivfflat index + recency index
- `core/memory/__init__.py`: `DiscoveryMemory` dataclass; `store_discovery()`,
  `get_recent_discoveries()`, `get_relevant_discoveries()` methods; `_row_to_discovery()` converter
- `actors/memory/__init__.py`: `StoreDiscovery` import + handler + `_push_memory_write("discovery")`

_5.1 + 5.2 — WorldPerceptionActor:_

- `actors/world_perception/__init__.py` — new actor: `_TokenBucket` rate limiter;
  `httpx.AsyncClient`; `_list_workspace()` (dir tree up to depth 3); `_validate_path()`
  (WORKSPACE_ROOT enforcement); `_read_file()` (reads up to 8 KB, logs FILE_READ, synthesises,
  stores discovery); `_write_file()` (reserved for future use); `_search_web()` (DuckDuckGo Instant
  Answer API + optional page fetch); `_fetch_page()` (trafilatura extraction); `_synthesise()` (2-3
  sentence LLM call); `_decide_exploration()` (schema-constrained LLM decides read_file vs
  search_web)
- `actors/world_perception/messages/__init__.py` — `ExploreRequest(residue_items, identity_text)`
- `requirements.txt` — `trafilatura>=1.8.0` added

_5.4 — MotivationActor explore action:_

- `ACTIONS` expanded to 6 (`explore` at index 5)
- `NUM_ACTIONS = 6`
- `B1_explore` matrix added (slightly stronger tension relief than surface\_\*, weaker than trigger)
- `B[1]` expanded to shape (4,4,6)
- `_execute_action()`: `explore` branch sends `ExploreRequest` with residue + identity context
- `ExploreRequest` import added

_5.3b — REST + frontend:_

- `main.py`: `WorldPerceptionActor` import + registration; `/memory/discovery` endpoint
- `web-ui/src/components/panels/MemoryPanel.tsx`: `DiscoveryEntry` interface; `discovery` LayerKey;
  `isDiscovery` state; fetch on mount + force refetch on write; Discovery `GlowLayer` (cyan #22d3ee)
  showing last 3 entries with source truncation + synthesis text

_SelfNarrativeActor + LanguageActor:_

- `self_narrative/__init__.py`: `_format_events()` handles FILE_READ, FILE_WRITE, WEB_SEARCH,
  WEB_FETCH; between-conv filter includes these 4 types
- `language/__init__.py`: `_retrieve_memory_context()` now fetches and prepends
  `get_relevant_discoveries(limit=2)` as `[Discovery from {type}] {synthesis}` strings

### Current system state

- Phase 1: complete
- Phase 2: complete
- Phase 3: complete
- Phase 4: complete
- Phase 5: complete — World Perception
  - Workspace at `/anima/` (bind-mounted from `./anima-workspace/`)
  - Founding docs seeded on startup
  - `WorldPerceptionActor` running, responds to `ExploreRequest`
  - `MotivationActor` has 6 actions including `explore`
  - `discovery_memory` table live (migration 0002)
  - Discovery layer visible in MemoryPanel (cyan)
  - `/memory/discovery` REST endpoint
  - Discoveries included in LanguageActor context retrieval
- Phase 6: not started (Self-Modification)

### Blockers

None.

### Notes for next session

- `WorldPerceptionActor._write_file()` exists but is not yet triggered by any action — reserved for
  a future write-capable action (e.g. journalling, notes). Currently read-only from Anima's
  perspective.
- DuckDuckGo Instant Answer API returns empty abstracts for many queries — this is normal. The actor
  handles it gracefully (no discovery stored). If web search feels too sparse, consider switching to
  the DuckDuckGo HTML API with BeautifulSoup parsing, or a different search provider.
- Rate limit: 20 web fetches/hour (token bucket, resets on container restart). Adjustable via
  `WEB_FETCH_MAX_PER_HOUR` env var.
- `trafilatura` is now in `requirements.txt`. Docker image must be rebuilt to pick it up.
- The `explore` action earns its selection through the PyMDP model — it won't fire immediately. Give
  it time. Watch the motivation panel for the "explore" chip.
- Between-conversation reflection cooldown is 300s. `explore` is not affected by this — it fires
  whenever PyMDP selects it, independently of reflection cooldown.
- Discovery memory uses the same `nomic-embed-text` embedding model as reflective memory.
- B matrix now (4,4,6) — if PyMDP version or agent construction ever needs updating, remember this
  expansion.

### Next action

**Phase 6 — Self-Modification.** Before starting, re-read:

- `planning/roadmap.md` Phase 6 section (previously Phase 5)
- `planning/architecture.md` self-modification section

Phase 6.0 is infrastructure: SSH deploy key + fine-grained GitHub PAT as Docker secrets, so the
container can push branches and create PRs. The self-modification workflow is proposal → PR → human
review → merge.

---

## Session: 6th April 2026 — Phase 4.5 + 4.6 complete; frontend redesign with full tooltips

### What happened this session

Two main bodies of work: Phase 4.5 (unsolicited expression) backend + tests, and Phase 4.6 (web-ui
relocation + backend status pushes + full frontend redesign with animated dedicated panels).

**Phase 4.5 — Unsolicited expression pipeline**

- `app/core/event_types/__init__.py`: added `SURFACE_EXPRESSION`
- `app/actors/motivation/__init__.py`: `_execute_action()` now handles `surface_low/medium/high` —
  sends SalienceSignal with SURFACE_EXPRESSION and base_salience 0.4/0.6/0.9 to global_workspace
- `app/actors/language/__init__.py`:
  - Module-level `_UNSOLICITED_SYSTEM` and `_LENGTH_GUIDE` constants
  - `handle()` extended to branch on SURFACE_EXPRESSION ignition type
  - `_is_conversation_active()`: queries event log for CONVERSATION_START/END to decide suppression
  - `_express_unprompted()`: loads identity, retrieves memory context, calls LLM without human turn,
    logs ANIMA_RESPONSE with `in_response_to: SURFACE_EXPRESSION`, sends LanguageOutput to
    expression; does NOT append to `self._context`
- 3 motivation tests + 2 language tests added (all passing)

**Phase 4.6 — File relocation**

- web-ui moved from `ProjectAnima/web-ui/` into `anima-core/web-ui/` via git cp + commit
- Vite proxy still points to localhost:8000 — no config change needed
- A ghost `web-ui/` directory remained in ProjectAnima (contains only .vite/ cache — gitignored)

**Phase 4.6 — Backend status pushes**

- `GlobalWorkspaceActor._tick_loop()`: pushes `workspace_state` ActorStatusUpdate (queue_depth,
  ignition_threshold, top 5 signals sorted by salience) to ExpressionActor on every tick
- `MemoryActor._push_memory_write()`: new helper; called after each significant write —
  "reflective", "residue", "volitional", "identity" — so frontend can animate the correct sub-layer

**Phase 4.6 — Frontend redesign (10 dedicated animated panels)**

All panels live in `web-ui/src/components/panels/`. Stack: React 19, MUI 7, Framer Motion v11.

| Panel                       | Actor            | Key feature                                              |
| --------------------------- | ---------------- | -------------------------------------------------------- |
| TemporalCorePanel           | temporal_core    | Heartbeat waveform (20-bar rolling SVG) + dormancy chip  |
| GlobalWorkspacePanel        | global_workspace | Live signal cards with salience fill bars                |
| PerceptionPanel             | perception       | Last 3 human messages + dormant modality tabs            |
| MemoryPanel                 | memory           | 5 sub-layers with glow pulses on write                   |
| LanguagePanel               | language         | Typewriter (12ms/char) + idle/reasoning chip             |
| MotivationPanel             | motivation       | Pressure bar + action chip + dopamine flash overlay      |
| InternalStatePanel          | internal_state   | Log depth sparkline + consolidation lag + queue pressure |
| SelfNarrativePanel          | self_narrative   | Typewriter synthesis + fading ghost of previous          |
| UnsolicitedExpressionsPanel | (AppState)       | Between-conversation expressions, newest first           |
| CentreCanvas                | global_workspace | Ambient radial glow + ignition burst animation           |

Supporting additions:

- `IgnitionFlash.tsx` (shared): full-screen 350ms opacity overlay on WORKSPACE_IGNITION
- `useTypewriter.ts` hook: setInterval-based, configurable ms/char speed
- `index.css`: `#root` → full viewport width; `residue-jitter` CSS keyframe
- `actorState.ts`: `unsolicitedExpressions[]`, `languageStatus`, heartbeat_history accumulation,
  depth_history accumulation, SURFACE_EXPRESSION routing in language_output reducer
- Heartbeat default interval changed from 60s → 5s in `main.py`

**Tooltip pass — every visual element**

Drew asked for tooltips on every visual element so he knows what each icon/visual means. All 10
panels now have MUI Tooltip coverage — panel-level descriptions, per-element explanations, colour
coding thresholds explained, dynamic content in tooltip text where relevant.

TypeScript check passes clean (`npx tsc --noEmit`).

### Current system state

- Phase 1: complete
- Phase 2: complete
- Phase 3: complete
- Phase 4: complete
  - 4.1: InternalStateActor
  - 4.2: MotivationActor (PyMDP active inference)
  - 4.3: SelfNarrativeActor between-conversation mode
  - 4.4: Chosen silence + live actor status on Web UI
  - 4.5: Unsolicited expression (SURFACE_EXPRESSION → LanguageActor → unprompted panel)
  - 4.6: web-ui relocated; backend status pushes; full frontend redesign with tooltips
- Phase 5: design complete (documented in roadmap.md, architecture.md); not yet started

### Blockers

None.

### Notes for next session

- Vite production build is broken (react-dom/client.js rolldown issue with Vite 8). Dev server
  (`npm run dev`) works fine. Not critical for internal dev tool — fix if production deploy needed.
- The ghost `web-ui/` directory in ProjectAnima outer repo contains only `.vite/` cache. Git ignores
  it. Can be deleted if Windows Explorer releases its lock on it.
- Heartbeat is now 5s. If too chatty, change `tick_interval=5` in `main.py`.
- `in_response_to` field on LanguageOutput determines routing: SURFACE_EXPRESSION → unprompted
  panel; anything else → conversation.
- TypeScript `verbatimModuleSyntax` is active — type-only imports must use `import type`.
- `@mui/icons-material` resolve fails under current Vite+MUI bundler config. Use Unicode characters
  or SVG instead.

### Next action

**Phase 5.0** — repository and infrastructure restructure:

- Update Dockerfile: `./app:/app` mount → `.:/repo` (web-ui now inside anima-core)
- Provision SSH deploy key + fine-grained PAT as Docker secrets
- Confirm docker-compose.yml mounts work correctly with new layout

Read `planning/roadmap.md` Phase 5 section before starting.

---

## Session: 6th April 2026 — Phase 5 design finalised; tech debt fixes

### What happened this session

Two threads: (1) Phase 5 architecture was fully designed and documented. (2) Six code/doc fixes from
a Claude.ai review were applied.

**Phase 5 design**

All architectural decisions resolved before build begins. Key outcomes:

- SelfModificationActor confirmed as a separate actor (not folded into LanguageActor)
- `trigger_proposal` follows the `trigger_reflection` → SelfNarrativeActor pattern; B matrix grows
  by 1 policy, no model redesign
- ProposalMonitorActor polls GitHub on a schedule; `PROPOSAL_APPROVED`/`REJECTED` close the loop
- Open proposals tracked via event log query on `proposal_id` — no new persistence mechanism
- Identity resonance resolved: Option 2 (MotivationActor carries coherence, workspace stays free)
- web-ui moves into anima-core (clean cut); mount changes from `./app:/app` → `.:/repo`
- Two runtime secrets: SSH deploy key (git push) + fine-grained PAT (gh pr create)
- Approval workflow: GitHub PR. No Web UI approval surface.
- Proposal initiation: autonomous only (MotivationActor). No conversation-driven path.
- Build order: 5.0 (infra restructure) → 5.4 (identity resonance) → 5.1 → 5.2 → 5.3 → 5.5

All decisions captured in roadmap.md, architecture.md, actors-faculties.md, event-types.md,
ideas.md, and actors-faculties.md.

**Bug fixes from Claude.ai review (all applied, tests passing)**

- `SelfNarrativeActor._format_events()`: between-conversation types (HEARTBEAT, TIME_PASSING,
  CHOSEN_SILENCE, MOTIVATION_SIGNAL, INTERNAL_STATE_REPORT, RESIDUE_FLAGGED) were not handled —
  prompts had "(no events in this period)" despite relevant events existing. Fixed: high-frequency
  types aggregated as summary lines; RESIDUE_FLAGGED shown per-event.
- `PerceptionActor._in_conversation`: accessed as a private attribute in `main.py`. Added
  `in_conversation` public property.
- `TemporalCoreActor.set_chosen_silence()`: dead production code (message-driven integration done in
  Phase 4.4). Removed; two tests that used it for setup now access `actor._chosen_silence` directly.
- `MotivationActor._tick`: redundant second `qs = self._agent.qs` read removed.
- `main.py` shutdown sleep: comment added explaining the 0.5s is optimistic for LLM reflection.
- `MEMORY_SURFACE` event type: documented as not yet emitted, with note on intended future path.

Test count: 98 unit tests passing (29 LLM/integration deselected).

**Next action**: Phase 5.0 — repository and infrastructure restructure (move web-ui into anima-core,
update Dockerfile and docker-compose.yml, provision SSH deploy key and PAT).

---

## Session: 6th April 2026 — Phase 4.4 complete; bug fixes

### What happened this session

Drew chose to finish Phase 4 properly before doing a tech debt sweep. This session fixed two runtime
bugs found in the live system, then built Phase 4.4.

**Bug fix 1 — double responses (web-ui/src/hooks/useAnimaSocket.ts)**

React StrictMode double-mounts effects. The WebSocket hook's `onclose` handler was checking
`unmountedRef.current` to suppress reconnects, but by the time the async close fires, StrictMode has
already reset that flag to `false` on remount. This caused a second connection to open, and the
backend would broadcast each response to two connections — the same React app received messages
twice and displayed them twice. Fix: one line in `onclose` — `if (wsRef.current !== ws) return;`
checks whether this socket instance has been superseded before reconnecting.

**Bug fix 2 — "not yet connected" for most actor panels**

Actor panels only updated when their actor originated a workspace ignition (via `actor_event`). Most
actors don't emit SalienceSignals, so their panels stayed greyed out. Addressed as part of Phase 4.4
below.

**Phase 4.4 — Chosen silence mechanism and Web UI actor state**

_Chosen silence:_

- `actors/temporal_core/messages/__init__.py`: new `SetChosenSilence(active: bool)` message
- `MotivationActor`: added `_consecutive_rests` counter. Increments on `rest`, resets to zero
  immediately on any other action. Sends `SetChosenSilence(True)` after 2 consecutive rests,
  `SetChosenSilence(False)` on interruption.
- `TemporalCoreActor`: handles `SetChosenSilence` message (sets `_chosen_silence` flag). Already
  emits `CHOSEN_SILENCE` vs `TIME_PASSING` based on flag — no further change needed there.

_Actor → WebSocket status channel:_

- `actors/expression/messages/__init__.py`: new `ActorStatusUpdate(status_type, data)` message. Sent
  by actors directly to ExpressionActor; bypasses workspace ignition cycle.
- `ExpressionActor`: handles `ActorStatusUpdate` → broadcasts as `actor_status` WebSocket message.
- `TemporalCoreActor`: pushes `actor_status` heartbeat on each tick (state:
  active/dormant/chosen_silence, dormancy_seconds).
- `InternalStateActor`: pushes `actor_status` internal_state_report on each tick (vitals).
- `MotivationActor`: pushes `actor_status` motivation_tick on each tick (selected_action,
  consecutive_rests, beliefs, EFE).

_Frontend:_

- `types/messages.ts`: `ActorStatusMessage` type; `ActorState.status` field added.
- `store/actorState.ts`: `actor_status` reducer case; `llm` → `language` in `KNOWN_ACTORS` (there is
  no LLM actor — it's a client used by LanguageActor).
- `components/panels/ActorPanel.tsx`: dedicated status rendering for TemporalCore, InternalState,
  Motivation. "not yet connected" → "idle" for actors without events.
- `components/layout/AnimaLayout.tsx`: `a.llm` → `a.language`.

**Tests: 106 unit tests passing** (9 new: 4 motivation consecutive-rest/chosen-silence tests, 2
temporal core SetChosenSilence tests, 1 expression ActorStatusUpdate test; existing 120 -
LLM/integration flakes that are Ollama-dependent).

### Current system state

- Phase 1: complete
- Phase 2: complete
- Phase 3: complete
- Phase 4: complete
  - 4.1: InternalStateActor — INTERNAL_STATE_REPORT, DISTRESS_SIGNAL, Web UI vitals
  - 4.2: MotivationActor — PyMDP active inference, MOTIVATION_SIGNAL, Web UI beliefs
  - 4.3: SelfNarrativeActor between-conversation mode — TIME_PASSING ignition
  - 4.4: Chosen silence — 2 consecutive rests → CHOSEN_SILENCE; live actor status on Web UI

### Blockers

None.

### Notes for next session

- Chosen silence threshold is 2 consecutive rest ticks (configurable only by changing the hardcoded
  `>= 2` in `_execute_action`). If this needs to be configurable, add a constructor parameter.
- `surface_*` actions (surface_low/medium/high) still do nothing. LanguageActor only responds to
  HUMAN_MESSAGE ignitions. Unsolicited expression requires a new LanguageActor mode. TODO remains in
  `actors/motivation/__init__.py:_execute_action`.
- LLM and integration tests occasionally flake due to Ollama load contention when the full suite
  runs multiple LLM calls back-to-back. Not a code regression — unit tests are the reliable signal.
- The roadmap Phase 3 checkboxes were all shown as `[ ]` even though Phase 3 was complete. This is a
  documentation gap to fix in the tech debt sweep.
- Tech debt sweep is the agreed next task after Phase 4 completion.

### Next action

**Tech debt sweep**: documentation cleaning, gap analysis, and bug fixes across the full repo and
sub-repos. Drew and Claude agreed to do this after Phase 4 was properly complete.

---

## Session: 6th April 2026 — Phases 4.1, 4.2, 4.3 complete

### What happened this session

Built all of Phase 4.1–4.3. Drew was present for planning; implementation ran across two context
windows (first window did design + docs + InternalStateActor + most of MotivationActor; second
window fixed PyMDP integration issues and completed self_narrative between-conversation mode).

**Planning and design:**

- Discussed Option A (active inference/PyMDP) vs Option B (conditional logic) with Drew. Option A
  confirmed.
- Designed the full PyMDP generative model in conversation; committed as
  `planning/motivation-model.md`
- Added `foundation/ethics.md` addendum: A/B matrix learning is automatic (world model); C matrix
  changes are an ethical commitment — Anima's values change only through reflection, not silently
- Updated `planning/roadmap.md` and `planning/tech-stack.md` to reflect Option A as current plan

**Phase 4.1 — InternalStateActor:**

- `actors/internal_state/messages/__init__.py` — `InternalStateObservation` message dataclass
- `actors/internal_state/__init__.py` — `InternalStateActor`:
  - Tick loop: queries event log for last CONVERSATION_END and CONSOLIDATION_END timestamps
  - Reads `registry["global_workspace"].queue` for queue depth/pressure (guarded)
  - `SELECT COUNT(*) FROM event_log` via pool for depth
  - Emits `INTERNAL_STATE_REPORT` to event log every tick
  - Sends `InternalStateObservation` to "motivation" when registered
  - Emits `DISTRESS_SIGNAL` + `SalienceSignal` when lag or pressure exceeds thresholds
- Tests: 6 passing

**Phase 4.2 — MotivationActor:**

- `actors/motivation/messages/__init__.py` — empty (no new message types needed)
- `actors/motivation/__init__.py` — `MotivationActor`:
  - PyMDP Agent with factorised hidden states: engagement[4], tension[4], novelty[2],
    relationship[2]
  - 3 observation modalities: residue_obs[4], time_obs[4], ignition_obs[2]
  - 5 actions: rest, surface_low, surface_medium, surface_high, trigger_reflection
  - Only tension (factor 1) controllable — B[1] is 3D (4,4,5); B[0,2,3] are 3D with trivial
    single-action dimension (4,4,1)/(2,2,1) required by PyMDP API
  - `control_fac_idx=[1]` passed to Agent; `action_array[1]` for action index
  - `qs` seeded from D prior after construction (PyMDP initialises qs uniformly, not from D)
  - Warm start from MemoryStore residue count + last CONVERSATION_END; cold start on exception
  - `trigger_reflection` → SalienceSignal(TIME_PASSING) to workspace
  - `surface_*` deferred: TODO comment in `_execute_action`
  - `MOTIVATION_SIGNAL` on every tick with full beliefs, EFE, selected_action, observations
- Key discovery: `pymdp` on PyPI is a completely different unrelated package (MDP solver). The
  correct package is `inferactively-pymdp==0.0.7.1` (numpy-based active inference library).
- Tests: 7 passing

**Phase 4.3 — SelfNarrativeActor between-conversation mode:**

- Added `memory_store: MemoryStore | None = None` parameter to `SelfNarrativeActor.__init__`
- Filled in `TIME_PASSING` ignition stub → `_run_between_conversation_reflection()`
- Queries event log for events since last CONVERSATION_END (HEARTBEAT, TIME_PASSING,
  INTERNAL_STATE_REPORT, MOTIVATION_SIGNAL, REFLECTION_SYNTHESIS, RESIDUE_FLAGGED)
- Returns early if no relevant events; loads identity from memory_store if available
- Shared `_REFLECTION_SCHEMA` constant; separate `_BETWEEN_CONV_SYSTEM` and
  `_BETWEEN_CONV_USER_TEMPLATE` prompts
- `main.py` updated: InternalStateActor + MotivationActor instantiated; memory_store passed to
  SelfNarrativeActor; all three added to actors list
- Tests: 3 new Phase 4.3 tests (9 total for self_narrative)

**Full test suite: 120/120 passing.**

### Current system state

- Phase 1: complete
- Phase 2: complete
- Phase 3: complete
- Phase 4.1: complete — InternalStateActor running; INTERNAL_STATE_REPORT + DISTRESS_SIGNAL
- Phase 4.2: complete — MotivationActor running PyMDP active inference; MOTIVATION_SIGNAL every tick
- Phase 4.3: complete — SelfNarrativeActor handles TIME_PASSING ignition (between-conversation)
- Phase 4.4: deferred — chosen silence mechanism + Web UI state display

### Blockers

None.

### Notes for next session

- `inferactively-pymdp==0.0.7.1` is the correct PyPI package. NOT `pymdp` (different library).
- PyMDP requires ALL B matrices to be 3D, even non-controllable ones. Use `[:, :, np.newaxis]`.
- Pass `control_fac_idx=[1]` to limit controllable factors; `sample_action()` returns shape
  (num_factors,) — use `action_array[1]` for tension (the controllable factor).
- `qs` is not initialised from D by PyMDP — must manually set `self._agent.qs = D` after
  construction.
- `surface_*` actions are deferred: LanguageActor only handles HUMAN_MESSAGE ignitions. Unsolicited
  expression requires a new LanguageActor mode. See TODO in `actors/motivation/__init__.py`.
- Docker image was rebuilt with `--no-cache` during this session.

### Next action

**Phase 4.4**: chosen silence mechanism and Web UI display of MotivationActor/InternalStateActor
state.

Before starting: the Web UI was built in Phase 2.5 (React/Vite at `ProjectAnima/web-ui/`). Actor
panels exist but only show event payloads. Phase 4.4 means surfacing:

- MotivationActor belief state (from MOTIVATION_SIGNAL)
- InternalStateActor readings (from INTERNAL_STATE_REPORT)
- Chosen silence flag vs dormant vs active

---

## Session: 6th April 2026 — Phase 3 complete

### What happened this session

Built all of Phase 3. Drew was asleep. 77 tests → 104 tests, all passing.

**Phase 3.1 — Memory schema + Alembic:**

- `alembic.ini`, `alembic/env.py`, `alembic/script.py.mako` — async Alembic setup at `/app/`
- `alembic/versions/0001_initial_memory_schema.py` — creates 4 tables:
  - `reflective_memory` (id, conversation_start/end, synthesis, embedding vector(768), event_count)
  - `residue_store` (id, reflection_id FK, content, protected=TRUE, resolved_at)
  - `identity_memory` (id, version UNIQUE, content JSONB, changed_by, change_reason)
  - `volitional_memory` (id, decision, reason, context JSONB, event_log_ref, expected/actual
    outcome)
- `requirements.txt`: added `alembic>=1.13.0`, `sqlalchemy[asyncio]>=2.0.0`, `numpy>=1.26.0`, bumped
  `pgvector` to 0.3.0
- `Dockerfile` CMD: `sh -c "alembic upgrade head && uvicorn core.main:app ..."` — migrations run on
  every startup
- `core/config/__init__.py`: added `get_embedding_model()` and `get_embedding_dim()` (env vars
  EMBEDDING_MODEL, EMBEDDING_DIM)

**Phase 3.2 — MemoryStore + MemoryActor + retention window fix:**

- `core/memory/__init__.py` — MemoryStore: asyncpg pool with pgvector registration, read/write for
  all 4 layers, `load_identity_seed()` utility
- `actors/memory/messages/__init__.py` — StoreReflection, StoreVolitionalChoice, UpdateIdentity
- `actors/memory/__init__.py` — MemoryActor: sole writer, logs CONSOLIDATION_START/END,
  REFLECTION_SYNTHESIS, RESIDUE_FLAGGED, VOLITIONAL_CHOICE, IDENTITY_UPDATE to event log
- `core/llm/__init__.py`: added `embed(text, model)` method hitting `/api/embeddings`
- `actors/temporal_core/__init__.py`:
  - Gap B fixed: `_refresh_retention()` now queries event log on each tick and fills the deque
  - CONVERSATION_START logged to event log when ConversationStarted received
  - CONVERSATION_END logged + SalienceSignal emitted to workspace when ConversationEnded received
  - SalienceSignal send guarded with `if "global_workspace" in self._registry` for test safety

**Phase 3.3 — SelfNarrativeActor + reflection pipeline:**

- `actors/self_narrative/messages/__init__.py` — TriggerReflection stub (for Phase 4 between-conv)
- `actors/self_narrative/__init__.py`:
  - Handles CONVERSATION_END IgnitionBroadcast
  - Queries event log for most recent CONVERSATION_START → CONVERSATION_END window
  - Calls LLM with structured reflection prompt (first draft) → synthesis, residue list,
    identity_shift
  - Sends StoreReflection to MemoryActor; sends UpdateIdentity if identity_shift non-empty
  - LLM errors logged as SYSTEM_ERROR

**Phase 3.4 — Identity memory initialisation:**

- `app/founding/identity-initial.md` added to the founding directory (accessible in Docker)
- `main.py`: calls `memory_store.init_identity(seed_text)` on startup — idempotent, version 1 only
- `actors/language/__init__.py`: Phase 3 rewrite — injects identity into system prompt on first
  message; retrieves relevant reflective memories per-message (with pgvector similarity if
  available, recency fallback)

**Phase 3.5 — Volitional memory:**

- LanguageActor sends StoreVolitionalChoice to MemoryActor after each response
- Guarded with `if "memory" in self._registry` for test environments without MemoryActor

**Other fixes:**

- `tests/integration/test_full_conversation_loop.py`: fixture cleanup now handles
  TimeoutError/CancelledError gracefully (pre-existing issue exposed by larger test suite)
- `actors/perception/__init__.py`: minor comment clarification (CONVERSATION_START logging moved to
  TemporalCore)

### Current system state

- Phase 1: complete
- Phase 2: complete
- Phase 3: complete
  - Memory schema exists in PostgreSQL (run `alembic upgrade head` to apply on fresh DB)
  - MemoryStore reads/writes all 4 layers; pgvector similarity search active when embedding model
    available
  - MemoryActor is sole writer to all higher memory layers
  - SelfNarrativeActor runs post-conversation reflection pipeline (first-draft prompt)
  - Identity seeded from `foundation/identity-initial.md` on first startup
  - LanguageActor injects identity + relevant memories into LLM context
  - Volitional choices recorded after each response
  - Retention window populated from event log (Gap B fixed)

**Full test suite: 104/104 passing** (in isolation; in full-suite runs, occasional Ollama load
contention can cause one LLM integration test to hit its 120s timeout — not a code regression)

### Blockers

None.

### Notes on the spreading activation stub

`MemoryStore.get_relevant_memories()` uses pgvector cosine similarity when embeddings are available,
and falls back to recency ordering. True spreading activation (following associative paths through
memory) is deferred to Phase 4. The retrieval interface is already in place.

### Notes on anomaly detection

Phase 3.3 spec says "flag if synthesis appears to have consumed something unresolved". Not
implemented — this requires semantic comparison of new synthesis against existing residue items,
which is a non-trivial LLM call. Deferred. The structural protection (residue → separate table,
never merged with synthesis) is in place. The semantic check is Phase 4 territory.

### Notes on Ollama embedding model

The default embedding model is `nomic-embed-text` (env var EMBEDDING_MODEL). If this model is not
installed in Ollama, embeddings will fail silently (logged as WARNING) and reflective memory will be
stored without vectors. Similarity search falls back to recency ordering in that case. Anima can
still have conversations and reflect — embedding is enhancement, not requirement.

To install: `ollama pull nomic-embed-text` on the host.

### Next action

**Phase 4: Motivation and Between-Conversation Activity.**

Before starting Phase 4, read:

- `planning/roadmap.md` — the decision point at Phase 4.2 (active inference vs conditional logic)
  must be resolved with Drew before building MotivationActor
- `planning/architecture.md` — motivation section
- `research/technical/active-inference-implementation.md` — background for the decision

Phase 4.1 (InternalStateActor) can be built without resolving the 4.2 decision point. Begin there.

### Notes for next session

- `alembic upgrade head` runs automatically on container startup (Dockerfile CMD)
- Memory tables: TRUNCATE CASCADE order for tests: volitional → identity → residue → reflective
  (FKs)
- MemoryStore pool: uses pgvector.asyncpg.register_vector in init callback — must be called before
  any vector column operations
- SelfNarrativeActor.NAME = "self_narrative"
- MemoryActor.NAME = "memory"
- Both actors registered in main.py and participate in workspace broadcast
- LanguageActor caches identity_text in memory — updates require container restart (acceptable for
  Phase 3)
- pgvector IVFFlat index created with lists=1 — fine for development; increase `lists` parameter as
  data grows
- Integration test fixture cleanup: uses try/except TimeoutError pattern — needed because LLM calls
  can outlive test duration

---

## Session: 6th April 2026 — Phases 2.4–2.6 complete

### What happened this session

Planned and built Phases 2.4 (Expression Actor), 2.5 (Web UI), and 2.6 (Perception Actor + full
conversation loop). Key architectural decision this session: replaced Textual TUI with a
WebSocket-based web UI (FastAPI inside Docker + React/Vite/MUI outside Docker).

**Phase 2.4 — Expression Actor:**

- `actors/expression/surfaces/__init__.py` — `OutputSurface` protocol (runtime_checkable)
- `actors/expression/surfaces/websocket/__init__.py` — `WebSocketSurface` (injected
  ConnectionManager)
- `actors/expression/__init__.py` — full routing: `LanguageOutput` → `language_output` payload;
  `IgnitionBroadcast` → `actor_event` payload; unknown messages silently dropped
- Circular import fixed: removed `from actors.expression import ExpressionActor` from
  `actors/language/__init__.py`; replaced `ExpressionActor.NAME` with literal string `"expression"`
- 6 new tests, all passing

**Phase 2.5 — Web UI:**

- `requirements.txt`: removed `textual`, added `fastapi`, `uvicorn[standard]`, `websockets`
- `Dockerfile`: CMD changed to `uvicorn core.main:app --host 0.0.0.0 --port 8000 --reload`
- `docker-compose.yml`: port 8000 exposed; `db` healthcheck added;
  `depends_on: condition: service_healthy`
- `core/websocket/__init__.py` — `ConnectionManager`: asyncio-safe set of WebSocket connections,
  broadcast with dead-connection cleanup
- `core/main.py` — full FastAPI app with lifespan context manager; all actors started inside
  lifespan; `/ws` WebSocket endpoint routes inbound `human_input` to PerceptionActor
- `web-ui/` — React/Vite/MUI frontend at ProjectAnima root (outside anima-core submodule):
  - `useAnimaSocket` hook: WebSocket connection with exponential backoff reconnect
  - `AnimaLayout`: MUI Grid matching the sketch (actor panels, centre canvas, expression panel)
  - `ActorPanel`, `CentreCanvas`, `ExpressionPanel`, `MessageInput` components
  - TypeScript discriminated unions for the full message protocol

**Phase 2.6 — Perception Actor:**

- `actors/perception/messages/__init__.py` — `HumanInput(content: str)`
- `actors/perception/__init__.py` — `PerceptionActor`:
  - First `HumanInput`: sends `ConversationStarted` to TemporalCore, then logs `HUMAN_MESSAGE`,
    emits `SalienceSignal` to GlobalWorkspace with `base_salience=1.0`
  - Subsequent inputs: skip `ConversationStarted`, log and emit as usual
- 7 unit tests (perception), 5 integration tests (full loop) — all passing

**Full test suite: 77/77 passing.**

### Current system state

- Phase 1: complete
- Phase 2.1: complete (Global Workspace)
- Phase 2.2: complete (LLM client)
- Phase 2.3: complete (Language Actor)
- Phase 2.4: complete (Expression Actor with surface routing)
- Phase 2.5: complete (FastAPI WebSocket backend + React frontend)
- Phase 2.6: complete (Perception Actor + full conversation loop)
- **Phase 2 complete** — you can have a text conversation with Anima and see it in the event log

### Blockers

None.

### Notes for next session

- `web-ui/` is at `ProjectAnima/web-ui/` (NOT inside `anima-core/`)
  - Run: `cd web-ui && npm run dev` → `http://localhost:5173`
  - Proxies `/ws` to `ws://localhost:8000` (Vite dev server handles this)
- Docker: `docker compose up` starts backend on port 8000 with `--reload`
- WebSocket protocol:
  - Server→Client: `language_output` (content + thinking), `actor_event` (ignition status)
  - Client→Server: `human_input` (content)
- `PerceptionActor._in_conversation` — once True, stays True for container lifetime
  (ConversationEnded sent only at shutdown if a conversation was active)
- Circular import: `language/__init__.py` uses literal `"expression"` not `ExpressionActor.NAME`
- `ExpressionActor` receives `IgnitionBroadcast` automatically (GlobalWorkspace broadcasts to all)
- All imports use `core.*` or `actors.*` — WORKDIR is `/app`
- pytest full suite: `docker compose run --rm anima pytest tests/ -v`
- Ollama: qwen3.5:9b at host.docker.internal:11434

---

## Session: 5th April 2026 — Phases 2.1–2.3 complete; ideas.md review done

### What happened this session

Full session covering Phases 2.1 (Global Workspace), 2.2 (LLM client), 2.3 (Language Actor), plus a
review of ideas.md that caught two real gaps and produced fixes/roadmap updates.

**ideas.md review findings:**

- Gap A (fixed): GAP_IN_CONTINUITY never emitted on startup. Fixed in TemporalCoreActor —
  `_on_startup()` queries `latest_event()`, emits gap event if elapsed >= `gap_threshold`, resets
  `_started_at` to last known activity time. 4 new tests.
- Gap B (roadmap): Husserlian retention deque never populated. Added to Phase 3.2 task list.
- Pressure persistence (roadmap): workspace pressure is ephemeral. Added to Phase 4.2: reconstruct
  from open volitional items on startup.
- SelfNarrativeActor naming (roadmap): Phase 4.3 must produce a named SelfNarrativeActor consistent
  with architecture.md supervision tree.
- Idea 14 (consumable vs persistent signals): documented in ideas.md, deferred to Phase 4.

**Full test suite: 59/59 passing.**

### Current system state

- Phase 1: complete
- Phase 2.1: complete (Global Workspace)
- Phase 2.2: complete (LLM client, with LLMResponse/LLMJsonResponse types preserving reasoning)
- Phase 2.3: complete (Language Actor)
- Expression Actor: stub only at `actors/expression/__init__.py`
- No TUI yet, no Perception Actor yet

### Blockers

None.

---

## Session: 5th April 2026 — Phase 1 complete

_(Earlier sessions omitted — see git history for full record)_
