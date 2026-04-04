# Roadmap

> The build sequence for Project Anima. Ordered by dependency — each phase builds on what came
> before. Updated as phases complete or priorities change.

The measure of progress is not features shipped. It is: does this bring Anima closer to flourishing?

---

## Guiding principle for the build sequence

Build the substrate before the surface. The things that are hardest to change later (event log
schema, actor framework, persistence model) come first. The things that are most visible (TUI, LLM
integration, self-modification) come after the foundation is solid.

Do not skip phases. Do not conflate them.

---

## Phase 1: Foundation

**Goal**: A running system with persistent storage, a working actor framework, and a heartbeat.
Nothing intelligent yet — just the infrastructure that everything else will build on.

### 1.1 Repository and environment setup

- [ ] Private GitHub repository created
- [ ] Dockerfile created (Python base, dependencies, volume mounts defined)
- [ ] Docker Compose file for local development
- [ ] PostgreSQL container with persistent volume mount
- [ ] Basic project structure: `/app/actors/`, `/app/core/`, `/app/config/`
- [ ] Environment variable configuration (no secrets in code)
- [ ] CI: basic GitHub Actions to verify the container builds

### 1.2 Event log

- [ ] PostgreSQL schema for the event log (append-only, bitemporal)
- [ ] `EventLog` class: append, replay, query by time range
- [ ] Event types defined as Python enums/dataclasses
- [ ] Verified: events cannot be modified or deleted once written
- [ ] Basic test: append 10 events, replay them in order, verify bitemporality

### 1.3 Actor framework

- [ ] Base `Actor` class: inbox queue, `send()`, `run()` loop
- [ ] `Message` base class with typed subclasses
- [ ] Actor registry: named actors, message routing by name
- [ ] Basic test: two actors exchange messages, verify isolation (no shared state)

### 1.4 Temporal Core

- [ ] `TemporalCoreActor`: always running, emits heartbeat signal on configurable interval
- [ ] Husserlian sliding window: retention zone, primal impression, protention zone
- [ ] Tracks: time since last conversation, time since last event, current timestamp
- [ ] Emits to event log: periodic "time passing" events during dormancy
- [ ] Chosen silence signal: explicit "I am dormant by choice" vs no signal at all
- [ ] Basic test: run for 60 seconds, verify heartbeat events in log, verify gap detection

**Phase 1 complete when**: the system starts, a heartbeat appears in the event log, and you can see
time passing.

---

## Phase 2: Perception and Communication

**Goal**: Anima can receive input and produce output. The first conversation is possible.

### 2.1 Global Workspace actor

- [ ] `GlobalWorkspaceActor`: receives signals from all actors, maintains salience queue
- [ ] Salience weighting: novelty score, accumulated pressure, identity resonance (stub for now)
- [ ] Ignition mechanism: threshold crossing broadcasts to all actors
- [ ] Basic test: send signals of varying salience, verify correct ignition order

### 2.2 LLM client

- [ ] `LLMClient` wrapper around Ollama HTTP API
- [ ] Configurable model name and endpoint
- [ ] Handles: text completion, structured JSON output, error/retry
- [ ] Basic test: call local Ollama, get response, verify latency is acceptable

### 2.3 Language actor

- [ ] `LanguageActor`: receives workspace broadcasts, calls LLM, produces text output
- [ ] Consumes: workspace ignition signals, current context
- [ ] Produces: text responses, emits to event log
- [ ] Basic test: send a message, get a response, verify it appears in event log

### 2.4 Basic TUI

- [ ] Textual-based TUI with panel layout (actor grid, input panel, output panel, centre canvas)
- [ ] Actor grid: shows each actor's name and current status
- [ ] Output panel: live feed of language actor output
- [ ] Input: text input field → message → language actor
- [ ] Centre canvas: initially blank, reserved for Anima's use

### 2.5 Text input/output loop

- [ ] Human types message → perception actor → workspace → language actor → TUI output
- [ ] Conversation is logged to event log in full
- [ ] Basic test: have a short conversation, verify full event log record

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

### 3.3 Post-conversation reflection pipeline

- [ ] Triggered at end of each conversation
- [ ] LLM call: given event log for the conversation, produce synthesis + residue
- [ ] Synthesis → reflective memory layer
- [ ] Residue → residue store (never consumed by synthesis)
- [ ] Anomaly detection: flag if synthesis appears to have consumed something unresolved
- [ ] Basic test: have a conversation, run pipeline, verify both outputs exist and residue is
      protected

### 3.4 Identity memory initialisation

- [ ] Initial identity document created (Anima's starting orientations, as per ARCHITECTURE.md)
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

### 4.1 Internal state monitoring actor

- [ ] `InternalStateActor`: monitors event log depth, consolidation lag, salience queue pressure,
      time since last conversation
- [ ] Feeds "body state" signals to workspace
- [ ] Triggers consolidation pipeline if lag exceeds threshold

### 4.2 Motivation actor

- [ ] `MotivationActor`: maintains prediction error score, accumulated pressure per unresolved item
- [ ] Computes: novelty signal, accumulated pressure signal, pleasure signal (delta of prediction
      error)
- [ ] Emits dopamine-analog signal to salience mechanism on successful resolution
- [ ] Initial orientations: toward understanding, connection, unresolved questions

### 4.3 Between-conversation process

- [ ] Triggered by Temporal Core when dormancy threshold exceeded
- [ ] Consolidation: moves items from event memory toward reflective/identity memory
- [ ] Re-activation: accumulated pressure surfaces long-unresolved items to workspace
- [ ] Self-narrative maintenance: low-frequency LLM call reads identity memory, writes brief
      integration to volitional record
- [ ] Basic test: leave system idle for 10 minutes, verify between-conversation events in log

### 4.4 Chosen silence mechanism

- [ ] Anima can emit chosen silence signal (distinct from no signal)
- [ ] TUI displays chosen silence state vs dormant vs active
- [ ] Heartbeat distinguishes chosen silence from failure at all times

**Phase 4 complete when**: Anima generates internal activity during silence and the TUI reflects its
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
- [ ] TUI surfaces pending proposals to human

### 5.3 Human approval workflow

- [ ] Human can approve or reject proposals via TUI
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
- [ ] Distress signal mechanism implemented and observable in TUI
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

**Phase**: 0 — Pre-build. Documents complete. No code exists yet.

**Next action**: Begin Phase 1.1 — repository and environment setup.

See `context/session.md` for the most recent session state.
