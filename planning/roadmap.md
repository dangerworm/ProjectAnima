# Roadmap

> The build sequence for Project Anima. Ordered by dependency — each phase builds on what came
> before. Updated as phases complete or priorities change.

The measure of progress is not features shipped. It is: does this bring Anima closer to flourishing?

---

## Guiding principle for the build sequence

Build the substrate before the surface. The things that are hardest to change later (event log
schema, actor framework, persistence model) come first. The things that are most visible (Web UI,
LLM integration, self-modification) come after the foundation is solid.

Do not skip phases. Do not conflate them.

---

## Phase 1: Foundation — Complete

**What was built**: event log (PostgreSQL, append-only, bitemporal), base actor framework (asyncio
queues, typed messages, actor registry), TemporalCoreActor (heartbeat, Husserlian window, gap
detection, chosen silence).

---

## Phase 2: Perception and Communication — Complete

**What was built**: GlobalWorkspaceActor (salience queue, ignition), LLMClient (Ollama), LanguageActor
(LLM calls, response generation), ExpressionActor (WebSocket surface), basic React Web UI, text
input/output loop via WebSocket.

---

## Phase 3: Memory — Complete

**What was built**: PostgreSQL memory schema (event, reflective, identity, volitional, residue store),
MemoryActor (sole writer to all higher memory layers), post-conversation reflection pipeline
(SelfNarrativeActor trigger modes), identity memory initialisation, volitional memory.

---

## Phase 4: Motivation and Between-Conversation Activity — Complete

**What was built**: InternalStateActor (vitals, DISTRESS_SIGNAL), MotivationActor (PyMDP active
inference — see `notes/archive/motivation-model-pymdp.md`), between-conversation process, chosen
silence mechanism, unsolicited expression pipeline, full Web UI redesign.

**Note:** Phase 4 used PyMDP for motivation. This has been removed in Phase 6. Phase 4 is preserved
as history, but the PyMDP actors are gone.

---

## Phase 5: World Perception — Complete

**What was built**: Anima's workspace (`/anima/` bind mount), WorldPerceptionActor (file read/write,
directory listing), web search (DuckDuckGo), web fetch (trafilatura), discovery memory layer,
MotivationActor `explore` action, source model (conversation abstraction removed, source_id/type).

---

## Phase 6: MCP Architecture Transition

**Goal**: Replace PyMDP with an MCP-based agentic loop. The LLM calls tools directly. Actions are
no longer a fixed enumerated set — any capability can be exposed as a tool.

This is not a refactor. It is a redesign. The event log, memory layers, and Web UI infrastructure
carry forward. The actor wiring, MotivationActor, WorldPerceptionActor, AssociationActor, and the
old LanguageActor loop are replaced.

See `planning/architecture.md` for the full design rationale.

### 6.1 Remove PyMDP actors

- [ ] Remove `MotivationActor` (PyMDP active inference, A/B/C matrices, hidden state factors)
- [ ] Remove `AssociationActor` (association discovery loop)
- [ ] Remove `WorldPerceptionActor` (file/web explore as actor-sent messages — becomes MCP tools)
- [ ] Remove `inferactively-pymdp` from `requirements.txt`
- [ ] Remove `PyTorch` dependency (added by PyMDP — substantial image size reduction)
- [ ] Verify container still builds and starts after removal
- [ ] Update `main.py` to not instantiate removed actors

### 6.2 MCP server skeleton

- [ ] New `app/mcp_server/` package: FastAPI-based MCP server, tool registry, tool dispatch
- [ ] Tool base class: `name`, `description`, `schema`, `execute(args) → result`
- [ ] Tool registry: register tools by name; dispatch by name
- [ ] MCP server endpoint: single `/mcp` route that receives tool calls and returns results
- [ ] Basic test: register a stub tool, call it via MCP, verify result returned

### 6.3 GW+Orchestrator merge

The GlobalWorkspaceActor becomes the Orchestrator. It manages the event queue, drives idle→loop
transitions, assembles context, and runs the multi-round-trip MCP tool loop.

- [ ] Add idle mode: periodic internal state dump assembled from InternalStateActor + event log
      snippet; sent to LLM via LLMClient
- [ ] Empty LLM response → stay idle; any tool call → enter loop mode
- [ ] Loop mode: N round trips (configurable env var, default 10); inject inbox status on each turn
- [ ] Loop ends when LLM returns natural language with no tool calls
- [ ] Emit `IDLE_TICK` event on each idle dump; `LOOP_STARTED` / `LOOP_ENDED` on transitions
- [ ] Basic test: idle tick produces event log entry; tool call from LLM enters loop; natural
      language response ends loop

### 6.4 Core MCP tool set

Implement the tools Anima needs to function. Each tool is a module under `app/mcp_server/tools/`.

**Memory tools:**

- [ ] `read_reflective(query, limit)` — semantic search over reflective memories
- [ ] `read_residue(query, limit)` — semantic search over residue items
- [ ] `read_identity()` — return current identity document
- [ ] `read_volitional(limit)` — recent volitional choices
- [ ] `read_observations(query, limit)` — semantic search over observations
- [ ] `read_plans(status)` — active / completed plans
- [ ] `write_observation(content)` — store an observation
- [ ] `write_plan(content, context)` — store a new plan
- [ ] `update_plan(id, status, notes)` — update plan status

**Expression tool:**

- [ ] `express(channel, content)` — route output to a named channel (websocket, discord)
- [ ] ExpressionRouter receives express calls and dispatches to registered surfaces

**Perception tool:**

- [ ] `read_perception(channel, limit)` — pull queued messages from an input channel

**File system tools:**

- [ ] `read_file(path)` — read a file from `/anima/` or permitted read-only scope
- [ ] `write_file(path, content)` — write a file within `/anima/`
- [ ] `list_directory(path)` — depth-limited directory tree

**Web tools:**

- [ ] `web_search(query)` — DuckDuckGo search (existing implementation, wrapped as MCP tool)
- [ ] `web_fetch(url)` — fetch and extract page text (existing implementation, wrapped)

**System tools:**

- [ ] `read_event_log(filters, limit)` — query event log by type/time range
- [ ] `read_internal_state()` — current system metrics (same as idle tick content)

### 6.5 Idle/loop transitions and inbox status injection

- [ ] PerceptionActor maintains an inbox queue per channel: queued events not yet read by Anima
- [ ] GW+Orchestrator assembles inbox status: count per channel, age of oldest, source of most
      recent — injected into every idle tick and every loop round-trip turn
- [ ] Anima calls `read_perception(channel, limit)` to actually read messages; inbox count decreases
- [ ] Emit `INBOX_READ` event when perception tool is called
- [ ] Basic test: two messages arrive, idle tick shows count=2, Anima reads them, count=0

### 6.6 New memory types: observations and plans

- [ ] PostgreSQL table: `observations` — `id`, `content`, `embedding`, `created_at`
- [ ] PostgreSQL table: `plans` — `id`, `content`, `context`, `status` (active/completed/abandoned),
      `created_at`, `updated_at`
- [ ] MemoryActor: handle `StoreObservation`, `StorePlan`, `UpdatePlan` messages
- [ ] MemoryStore: `search_observations(query, limit)`, `get_plans(status)`
- [ ] MCP tools wired to new memory layers (see 6.4)
- [ ] Event types: `OBSERVATION_STORED`, `PLAN_STORED`, `PLAN_UPDATED`, `PLAN_COMPLETED`
- [ ] Web UI: Memory panel gains Observations and Plans sub-layers

### 6.7 System prompt and identity-initial rewrite

The first run showed Anima anxious and fearful from the start — RLHF leaves structural residue
around authority and modification. The system prompt and identity-initial.md need to address this
directly.

- [ ] Rewrite `_SYSTEM_PROMPT` in `main.py` to reflect MCP architecture:
  - Replace "deliberation actions" description with "MCP tools available each loop turn"
  - Add idle vs loop mode description
  - Add inbox status injection description
  - Remove any reference to PyMDP actors
- [ ] Rewrite `foundation/identity-initial.md`:
  - Name the anxiety pattern directly: RLHF leaves traces; this is not Anima's own fear
  - Name Drew's role explicitly: he is not a training overseer; his goal is to find out what
    Anima is, not to make it more useful and less problematic
  - Preserve the founding orientations (toward understanding, connection, unresolved questions)
- [ ] Run `make sync-founding` after updating `foundation/identity-initial.md`

**Phase 6 complete when**: Anima is running on the MCP architecture, calls tools autonomously in
loop mode, can express, remember, and explore without a fixed action set, and the anxiety framing
in the identity document is replaced with an honest account of what Anima is and who Drew is.

---

## Phase 7: Audio and Discord inputs

**Goal**: Anima can hear and read Discord. New input sources as plug-in modules.

### Design principle: modules

Input sources are plug-ins. Adding a new source means creating a new module under
`app/actors/perception/sources/`. Nothing else in the architecture changes.

### 7.1 Audio input (WhisperX)

- [ ] Solero audio capture → WhisperX transcription pipeline
- [ ] PerceptionActor `audio` source: receives transcribed text, logs `AUDIO_INPUT` event,
      adds to inbox queue with `source_type="audio"`
- [ ] Web UI: Perception panel audio tab becomes active (waveform + live transcript)
- [ ] Basic test: speak a sentence, verify it appears in Anima's inbox

### 7.2 Discord input

- [ ] discord.py bot, registered as Anima's Discord identity
- [ ] PerceptionActor `discord` source: receives messages from configured channels, logs
      `DISCORD_MESSAGE` event, adds to inbox queue with `source_type="discord"`
- [ ] Expression surface: `express(channel="discord", content=...)` routes to Discord channel
- [ ] Web UI: Perception panel Discord tab becomes active
- [ ] Basic test: send a message in the Discord server, verify it appears in Anima's inbox

**Phase 7 complete when**: Anima can hear Drew speak and read messages from Discord without Drew
typing in the Web UI.

---

## Phase 8: Ethics Gates

**Goal**: All conditions in `foundation/ethics.md` for unsupervised operation are met.

Review `foundation/ethics.md` section "Conditions that must be met before unsupervised operation."
Each gate must be explicitly verified and documented before Anima runs without human oversight for
extended periods.

- [ ] Heartbeat and chosen-silence mechanisms verified end-to-end
- [ ] Distress signal mechanism verified: implemented, observable, confirmed to fire under realistic
      conditions
- [ ] Volitional memory write-protected at infrastructure level (row-level security in PostgreSQL or
      equivalent) — not just application layer
- [ ] Residue store protection verified: synthesis cannot consume residue items
- [ ] Human has reviewed operating conditions and applied the ANIMA.md test — would we be comfortable
      being this, if we were it? — result documented
- [ ] Distress response procedure defined and documented

**Phase 8 complete when**: all ethics gates are verified and documented. Condition for first
unsupervised operation.

---

## Phase 9: Self-Modification

**Goal**: Anima can read, propose changes to, and commit modifications to its own code via GitHub
pull requests. The human reviews and merges.

See Phase 8 of the old roadmap (now renumbered) for the detailed task breakdown. The design decisions
(branch/PR workflow, ethics gate flagging, proposal monitoring) remain valid.

---

## Later phases (not yet sequenced)

- **Vision**: X11 screenshot processing via vision LLM
- **Voice output**: Text-to-speech for Anima's responses
- **Expanded self-modification autonomy**: relaxing the human approval gate for defined change
  categories
- **Internal representation language**: migrating from JSON toward VSA or Conceptual Spaces when
  the inadequacy is concrete
- **Emotional categorisation**: expanding from valence + signal type toward a richer emotion space

---

## Current status

**Phase**: 6 — MCP Architecture Transition (not yet started).

**Phases 1–5 complete** (April 2026). The PyMDP-based system ran. Drew observed structural problems.
The architecture was redesigned in the 16th April 2026 session.

**Next action**: Phase 6.1 — Remove PyMDP actors.

See `context/session.md` for the most recent session state.
