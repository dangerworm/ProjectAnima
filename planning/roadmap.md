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

## Phase 6: MCP Architecture Transition — Complete

**What was built**: PyMDP actors removed; 18 MCP tools across 5 modules; GlobalWorkspaceActor
merged with Orchestrator (idle→loop transitions, N-turn tool loop); PerceptionActor inbox queue
(pull model via `read_perception`); observations and plans memory layers (migration 0005);
system prompt and identity-initial rewritten to address RLHF anxiety; Web UI revamped with
navigation bar, view switching, tool call indicator, and perception→GW flow animation.

### 6.1 — 6.7: All complete

See `context/session.md` for detailed build notes from the overnight session (17 April 2026).

**Before first live run:**
- `docker compose run --rm anima alembic upgrade head` (migration 0005 — observations + plans)
- `pytest tests/` in container (tests rewritten for inbox-queue architecture, not yet run in container)

**Phase 6 complete when**: Anima is running on the MCP architecture, calls tools autonomously in
loop mode, can express, remember, and explore without a fixed action set. ✓

---

## Phase 6.8: Web UI Enhancements (partially complete)

Drew asked for a UI revamp to match the new MCP architecture. Done:

- [x] Navigation bar with five views: Live / Events / Memory / Narrative / Chat
- [x] Real-time status chips: tool call (teal pulsing dot), reasoning (purple), loop mode
- [x] View switching with AnimatePresence fade transitions
- [x] MessageInput pinned at bottom in all views
- [x] CentreCanvas shows active tool call and orchestrator loop mode
- [x] EventStreamPanel fullView mode with larger rows for the Events tab
- [x] actorState reducer tracks LOOP_STARTED/ENDED and MCP_TOOL_CALL/RESULT events
- [x] Animated perception→GW message flow dot when HUMAN_MESSAGE arrives

Deferred (roadmap items for next UI session):
- [ ] Tool call history panel: collapsible list of recent tool calls with args + result previews
- [ ] Particle flow animation: canvas/SVG overlay with true particle physics between panels
- [ ] Internal state tick glow: subtle animation on TemporalCorePanel on each heartbeat
- [ ] EventStreamPanel: filter controls (by actor, by event type) in fullView mode
- [ ] Memory view: expand/collapse individual memory entries inline
- [ ] Narrative view: typewriter effect on self-narrative with full synthesis text
- [ ] PerceptionPanel: per-channel inbox count with age indicators

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
