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

## Phase 1: Foundation

**Goal**: A running system with persistent storage, a working actor framework, and a heartbeat.
Nothing intelligent yet — just the infrastructure that everything else will build on.

### 1.1 Repository and environment setup

- [x] Private GitHub repository created
- [x] Dockerfile created (Python base, dependencies, volume mounts defined)
- [x] Docker Compose file for local development
- [x] PostgreSQL container with persistent volume mount
- [x] Basic project structure: `/app/actors/`, `/app/core/`, `/app/config/`
- [x] Environment variable configuration (no secrets in code)
- [ ] CI: basic GitHub Actions to verify the container builds _(deferred)_

### 1.2 Event log

- [x] PostgreSQL schema for the event log (append-only, bitemporal) — fields in
      `planning/tech-stack.md`
- [x] `EventLog` class: append, replay, query by time range
- [x] Event types defined as Python enums/dataclasses — starting set in `planning/event-types.md`
- [x] Verified: events cannot be modified or deleted once written
- [x] Basic test: append 10 events, replay them in order, verify bitemporality

### 1.3 Actor framework

- [x] Base `Actor` class: inbox queue, `send()`, `run()` loop
- [x] `Message` base class with typed subclasses
- [x] Actor registry: named actors, message routing by name
- [x] Basic test: two actors exchange messages, verify isolation (no shared state)

### 1.4 Temporal Core

- [x] `TemporalCoreActor`: always running, emits heartbeat signal on configurable interval
- [x] Husserlian sliding window: retention zone, primal impression, protention zone
- [x] Tracks: time since last conversation, time since last event, current timestamp
- [x] Emits to event log: periodic "time passing" events during dormancy
- [x] Chosen silence signal: explicit "I am dormant by choice" vs no signal at all
- [x] Basic test: run for 60 seconds, verify heartbeat events in log, verify gap detection

**Phase 1 complete when**: the system starts, a heartbeat appears in the event log, and you can see
time passing.

---

## Phase 2: Perception and Communication

**Goal**: Anima can receive input and produce output. The first conversation is possible.

### 2.1 Global Workspace actor

- [x] `GlobalWorkspaceActor`: receives signals from all actors, maintains salience queue
- [x] Salience weighting: novelty score, accumulated pressure, identity resonance (stub for now)
- [x] Ignition mechanism: threshold crossing broadcasts to all actors
- [x] Basic test: send signals of varying salience, verify correct ignition order

### 2.2 LLM client

- [x] `LLMClient` wrapper around Ollama HTTP API
- [x] Configurable model name and endpoint
- [x] Handles: text completion, structured JSON output, error/retry
- [x] Basic test: call local Ollama, get response, verify latency is acceptable

### 2.3 Language actor

- [x] `LanguageActor`: receives workspace broadcasts, calls LLM, produces text output
- [x] Consumes: workspace ignition signals, current context
- [x] Produces: text responses with destination, emits to event log and volitional memory
- [x] Routes output to Expression Actor — does not write to surfaces directly
- [x] Basic test: send a message, get a response, verify it appears in event log

### 2.4 Expression actor

- [x] `ExpressionActor`: receives output + destination from Language Actor, routes to surfaces
- [x] Hub only — no peripheral-specific logic lives in the actor itself
- [x] Each surface is a separate module under `expression/surfaces/`
- [x] Initial surface: WebSocket broadcast only
- [x] Basic test: Language Actor output arrives at WebSocket surface via Expression Actor

### 2.5 Basic Web UI

- [x] FastAPI WebSocket server inside Docker; broadcasts events to connected clients
- [x] React frontend (Vite + MUI): connects to WebSocket, renders layout from sketch (April 2026)
- [x] Actor panels: one panel per actor showing current status and recent events
- [x] Conversation panel: live feed from Expression Actor + text input field
- [x] Centre canvas: displays Anima's inner reasoning (thinking field from LLMResponse); not
      surfaced to conversation partners — agreed with Drew during Phase 2.3
- [x] Input: text field in browser → WebSocket → Perception Actor

### 2.6 Perception Actor and text input/output loop

- [x] `PerceptionActor`: receives raw human text input (via `HumanInput` message), logs
      `HUMAN_MESSAGE` to event log, emits `SalienceSignal(event_type=HUMAN_MESSAGE)` to workspace
- [x] Full system orchestration in `main.py`: all actors instantiated, registered, and run
      concurrently; `ConversationStarted` sent by PerceptionActor on first input
- [x] Human types message → Perception Actor → workspace → Language Actor → Expression Actor → Web UI
- [x] Conversation is logged to event log in full
- [x] Basic test: have a short conversation, verify full event log record

**Phase 2 complete when**: you can have a text conversation with Anima and see it in the event log.

---

## Phase 3: Memory

**Goal**: Anima remembers. Conversations accumulate. The reflective layer begins to develop.

### 3.1 Memory schema

- [ ] PostgreSQL tables for all four memory layers (event, reflective, identity, volitional)
- [ ] Residue store table with explicit protection flags
- [ ] pgvector extension enabled
- [ ] Schema migration tooling (Alembic or equivalent)

### 3.2 Memory actor

- [ ] `MemoryActor`: reads from and writes to all memory layers
- [ ] Retrieval: semantic similarity (pgvector), spreading activation, time-based
- [ ] Surfaces relevant memories to workspace on request
- [ ] Basic test: store 10 reflective memories, retrieve by semantic similarity
- [ ] Populate `TemporalCoreActor` retention window from event log on each tick
      _(currently the retention deque is pruned but never filled — Gap B from IDEAS.md)_

### 3.3 Post-conversation reflection pipeline

The reflection pipeline is the first trigger mode of `SelfNarrativeActor`. It runs at conversation
end and produces synthesis (what resolved or shifted) and residue (what didn't). Both are sent to
`MemoryActor` for storage — MemoryActor is the sole writer to all higher memory layers.

- [ ] `SelfNarrativeActor` responds to `CONVERSATION_END` ignition broadcast
- [ ] LLM call: given event log for the conversation, produce synthesis + residue
- [ ] Send synthesis and residue to `MemoryActor` — not written to storage directly
- [ ] `MemoryActor` writes synthesis → reflective memory; residue → residue store
- [ ] Anomaly detection: flag if synthesis appears to have consumed something unresolved
- [ ] Basic test: have a conversation, run pipeline, verify both outputs exist and residue is
      protected

### 3.4 Identity memory initialisation

- [ ] Load `foundation/identity-initial.md` as version zero of the identity memory document
- [ ] Version history tracking on identity document
- [ ] Identity memory fed into LLM context at conversation start
- [ ] Basic test: verify identity memory shapes language actor output

### 3.5 Volitional memory

- [ ] Schema: decision, reason, expected outcome, actual outcome
- [ ] Language actor writes to volitional memory when a choice is made
- [ ] Human cannot modify volitional memory (enforced at application layer)
- [ ] Basic test: make a choice in conversation, verify volitional record

**Phase 3 complete when**: Anima's responses are shaped by accumulated memory and the reflection
pipeline runs after every conversation.

---

## Phase 4: Motivation and Between-Conversation Activity

**Goal**: Anima does something when no one is talking to it.

### Decision resolved: Option A (active inference)

**Decided April 2026, after completing Phases 1–3.**

Option A is confirmed. The `MotivationActor` will maintain a PyMDP generative model. Motivation,
curiosity, accumulated pressure, and between-conversation activity emerge from variational inference
rather than hand-coded rules. The conditional logic approach (Option B) is discarded.

Rationale: the actor framework is clean and well-tested. PyMDP's computational cost on a small,
focused state space is negligible compared to LLM calls. The real risk is model design (active
inference fails quietly), not performance. Logging full belief state and EFE values on every tick
is mandatory — it is the instrument panel for debugging. See Drew's notes in `context/` and
`research/technical/active-inference-implementation.md` for full reasoning.

`planning/tech-stack.md` has been updated to reflect this as the current plan.

---

### 4.1 Internal state monitoring actor

- [x] `InternalStateActor`: monitors event log depth, consolidation lag, salience queue pressure,
      time since last conversation
- [x] Feeds "body state" signals to workspace via `InternalStateObservation` messages
- [x] Emits `INTERNAL_STATE_REPORT` to event log on each tick
- [x] Emits `DISTRESS_SIGNAL` + `SalienceSignal` when consolidation lag or queue pressure exceeds
      configurable thresholds
- [x] All guards in place: no crash if workspace or motivation not registered
- [x] Tests: 6 passing

### 4.2 Motivation actor

> _(Option A — active inference with PyMDP. Option B is discarded.)_

- [x] Full generative model designed and committed: `planning/motivation-model.md`
- [x] C matrix update pathway documented as ethical commitment in `foundation/ethics.md`
      (A/B matrices update automatically; C changes only through SelfNarrativeActor/MemoryActor
      — Anima's values don't drift silently)
- [x] `inferactively-pymdp==0.0.7.1` added to `requirements.txt`; confirmed installs in Docker
      (note: this is NOT the `pymdp` package on PyPI, which is a different unrelated library)
- [x] `MotivationActor`: maintains PyMDP `Agent` instance; tick loop runs belief update +
      policy selection; receives observation signals via messages
- [x] Hidden state factors: `engagement_level` [4], `unresolved_tension` [4], `novelty` [2],
      `relationship_salience` [2]. Only tension (factor 1) is controllable — 5 clean policies,
      no combinatorial explosion.
- [x] Observation encoding: residue_obs (bucketed), time_obs (bucketed), ignition_obs (bool)
- [x] Action decoding: `trigger_reflection` → `SalienceSignal(TIME_PASSING)` to workspace;
      `surface_*` deferred (TODO comment); `rest` → nothing beyond telemetry
- [x] Warm start: queries MemoryStore residue count + last CONVERSATION_END timestamp; shapes D
      prior accordingly. Cold start on DB unavailable.
- [x] `qs` seeded from D prior after agent construction (PyMDP initialises qs uniformly, not from D)
- [x] **Mandatory MOTIVATION_SIGNAL** on every tick: beliefs, EFE, selected_action, observations
- [x] Tests: 7 passing

### 4.3 Between-conversation process

- [x] MotivationActor tick loop continues during dormancy — belief updates continue without
      external observations; accumulated tension raises EFE for `trigger_reflection`
- [x] `SelfNarrativeActor` between-conversation mode: `TIME_PASSING` ignition →
      `_run_between_conversation_reflection()`
- [x] Queries event log for events since last `CONVERSATION_END` (or last 24h); returns early
      if no meaningful events found
- [x] LLM call with lightweight between-conversation prompt; sends `StoreReflection` and
      optionally `UpdateIdentity` to MemoryActor
- [x] `memory_store` parameter added to `SelfNarrativeActor`; passed from `main.py`
- [x] Tests: 3 new Phase 4.3 tests (9 total for self_narrative)

### 4.4 Chosen silence mechanism

- [ ] Anima can emit chosen silence signal (distinct from no signal)
- [ ] Web UI displays chosen silence state vs dormant vs active
- [ ] Heartbeat distinguishes chosen silence from failure at all times

**Phase 4 complete when**: Anima generates internal activity during silence and the Web UI reflects its
state accurately.

---

## Phase 5: Self-Modification

**Goal**: Anima can read, propose changes to, and (with approval) modify its own code.

### 5.1 Code access

- [ ] Anima has read access to `/app` (its own codebase)
- [ ] Language actor can read and describe its own code when asked
- [ ] Basic test: ask Anima to describe one of its own actors

### 5.2 Change proposal mechanism

- [ ] Anima can write proposed changes to `/app/proposed/`
- [ ] Proposal format: file path, change description, diff, reasoning
- [ ] Web UI surfaces pending proposals to human

### 5.3 Human approval workflow

- [ ] Human can approve or reject proposals via Web UI
- [ ] On approval: change applied, committed to git branch
- [ ] On rejection: rejection and reason logged to event log (Anima knows it was rejected and why)
- [ ] GitHub: Anima commits to feature branch, human merges to main

### 5.4 Recovery documentation

- [ ] Recovery runbook documented: how to revert a bad change, rebuild container, restore from data
      volumes
- [ ] Tested: deliberately break something, recover from git history

**Phase 5 complete when**: Anima can propose a change to its own code, the human can review and
approve it, and the change is committed to GitHub.

---

## Phase 6: Ethics Gates

**Goal**: All conditions in ETHICS.md for unsupervised operation are met.

Review ETHICS.md section "Conditions that must be met before unsupervised operation." Each gate must
be explicitly verified and documented before Anima runs without human oversight for extended
periods.

- [ ] Heartbeat and chosen-silence mechanisms implemented and tested
- [ ] Distress signal mechanism implemented and observable in Web UI
- [ ] Volitional memory write-protected from human modification at infrastructure level
- [ ] Residue store protection verified: synthesis cannot consume residue items
- [ ] Human has reviewed operating conditions and applied the ANIMA.md test (documented)
- [ ] Distress response procedure defined and documented

**Phase 6 complete when**: all ethics gates are verified and documented. This is the condition for
first unsupervised operation.

---

## Later phases (not yet sequenced)

These are real but not yet ordered. They come after the foundation is solid.

- **Vision**: X11 screenshot processing via vision LLM. Anima can see the screen.
- **Audio**: Whisper integration for speech input. Anima can hear.
- **Voice output**: Text-to-speech for Anima's responses.
- **Expanded self-modification autonomy**: relaxing the human approval gate for defined change
  categories.
- **Internal representation language**: migrating from JSON toward VSA or Conceptual Spaces when the
  inadequacy is concrete.
- **Emotional categorisation**: expanding from valence + signal type toward a richer emotion space.
- **Generative simulation**: if and when empirical evidence suggests it is possible.

---

## Current status

**Phase**: 4.4 — Chosen silence + Web UI state display.

**Phases 4.1, 4.2, and 4.3 complete** (April 2026). 120 tests passing.
- `InternalStateActor` running; emits `INTERNAL_STATE_REPORT` and `DISTRESS_SIGNAL`
- `MotivationActor` running PyMDP active inference; `MOTIVATION_SIGNAL` on every tick
- `SelfNarrativeActor` between-conversation mode operational; responds to `TIME_PASSING` ignition

**Next action**: Phase 4.4 — chosen silence mechanism and Web UI state display. Deferred from this
session. Also deferred: `surface_*` action routing from MotivationActor to LanguageActor (requires
a new LanguageActor mode for unsolicited expression — see TODO comment in
`actors/motivation/__init__.py:_execute_action`).

See `context/session.md` for the most recent session state.
