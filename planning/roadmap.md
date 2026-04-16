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
- [x] Human types message → Perception Actor → workspace → Language Actor → Expression Actor → Web
      UI
- [x] Conversation is logged to event log in full
- [x] Basic test: have a short conversation, verify full event log record

**Phase 2 complete when**: you can have a text conversation with Anima and see it in the event log.

---

## Phase 3: Memory

**Goal**: Anima remembers. Conversations accumulate. The reflective layer begins to develop.

### 3.1 Memory schema

- [x] PostgreSQL tables for all four memory layers (event, reflective, identity, volitional)
- [x] Residue store table with explicit protection flags
- [x] pgvector extension enabled
- [x] Schema migration tooling (Alembic or equivalent)

### 3.2 Memory actor

- [x] `MemoryActor`: reads from and writes to all memory layers
- [x] Retrieval: semantic similarity (pgvector), spreading activation, time-based
- [x] Surfaces relevant memories to workspace on request
- [x] Basic test: store 10 reflective memories, retrieve by semantic similarity
- [x] Populate `TemporalCoreActor` retention window from event log on each tick _(Gap B from
      ideas.md — fixed: `_refresh_retention()` queries event log on each tick)_

### 3.3 Post-conversation reflection pipeline

The reflection pipeline is the first trigger mode of `SelfNarrativeActor`. It runs at conversation
end and produces synthesis (what resolved or shifted) and residue (what didn't). Both are sent to
`MemoryActor` for storage — MemoryActor is the sole writer to all higher memory layers.

- [x] `SelfNarrativeActor` responds to `CONVERSATION_END` ignition broadcast _(CONVERSATION_END
      deprecated April 2026; trigger changed to event-volume threshold / trigger_reflection action)_
- [x] LLM call: given event log for the conversation, produce synthesis + residue
- [x] Send synthesis and residue to `MemoryActor` — not written to storage directly
- [x] `MemoryActor` writes synthesis → reflective memory; residue → residue store
- [ ] Anomaly detection: flag if synthesis appears to have consumed something unresolved _(deferred
      — structural protection in place; semantic check is Phase 4+ territory)_
- [x] Basic test: have a conversation, run pipeline, verify both outputs exist and residue is
      protected

### 3.4 Identity memory initialisation

- [x] Load `foundation/identity-initial.md` as version zero of the identity memory document
- [x] Version history tracking on identity document
- [x] Identity memory fed into LLM context at conversation start
- [x] Basic test: verify identity memory shapes language actor output

### 3.5 Volitional memory

- [x] Schema: decision, reason, expected outcome, actual outcome
- [x] Language actor writes to volitional memory when a choice is made
- [x] Human cannot modify volitional memory (enforced at application layer)
- [x] Basic test: make a choice in conversation, verify volitional record

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
inference fails quietly), not performance. Logging full belief state and EFE values on every tick is
mandatory — it is the instrument panel for debugging. See Drew's notes in `context/` and
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
- [x] C matrix update pathway documented as ethical commitment in `foundation/ethics.md` (A/B
      matrices update automatically; C changes only through SelfNarrativeActor/MemoryActor — Anima's
      values don't drift silently)
- [x] `inferactively-pymdp==0.0.7.1` added to `requirements.txt`; confirmed installs in Docker
      (note: this is NOT the `pymdp` package on PyPI, which is a different unrelated library)
- [x] `MotivationActor`: maintains PyMDP `Agent` instance; tick loop runs belief update + policy
      selection; receives observation signals via messages
- [x] Hidden state factors: `engagement_level` [4], `unresolved_tension` [4], `novelty` [2],
      `relationship_salience` [2]. Only tension (factor 1) is controllable — 5 clean policies, no
      combinatorial explosion.
- [x] Observation encoding: residue_obs (bucketed), time_obs (bucketed), ignition_obs (bool)
- [x] Action decoding: `trigger_reflection` → `SalienceSignal(TIME_PASSING)` to workspace;
      `surface_*` deferred (TODO comment); `rest` → nothing beyond telemetry
- [x] Warm start: queries MemoryStore residue count + time since last contact; shapes D prior
      accordingly. Cold start on DB unavailable. _(Originally used CONVERSATION_END timestamp; fixed
      April 2026 to query HUMAN_MESSAGE — CONVERSATION_END was never emitted.)_
- [x] `qs` seeded from D prior after agent construction (PyMDP initialises qs uniformly, not from D)
- [x] **Mandatory MOTIVATION_SIGNAL** on every tick: beliefs, EFE, selected_action, observations
- [x] Tests: 7 passing

### 4.3 Between-conversation process

- [x] MotivationActor tick loop continues during dormancy — belief updates continue without external
      observations; accumulated tension raises EFE for `trigger_reflection`
- [x] `SelfNarrativeActor` between-conversation mode: `TIME_PASSING` ignition →
      `_run_between_conversation_reflection()`
- [x] Queries event log for events since last reflection (or last 24h); returns early if no
      meaningful events found _(original: since last CONVERSATION_END — deprecated April 2026)_
- [x] LLM call with lightweight between-conversation prompt; sends `StoreReflection` and optionally
      `UpdateIdentity` to MemoryActor
- [x] `memory_store` parameter added to `SelfNarrativeActor`; passed from `main.py`
- [x] Tests: 3 new Phase 4.3 tests (9 total for self_narrative)

### 4.4 Chosen silence mechanism

- [x] Anima can emit chosen silence signal (distinct from no signal)
- [x] Web UI displays chosen silence state vs dormant vs active
- [x] Heartbeat distinguishes chosen silence from failure at all times

---

### 4.5 Unsolicited expression

**Goal**: Anima can address Drew unprompted. MotivationActor's surface\_\* actions become real.

- [x] Add `SURFACE_EXPRESSION` to `EventType` enum and `planning/event-types.md`
- [x] MotivationActor: implement `surface_low`, `surface_medium`, `surface_high` — each sends
      `SalienceSignal(event_type=SURFACE_EXPRESSION, base_salience=0.4/0.6/0.9,     content={"level": "low"/"medium"/"high"})`
      to GlobalWorkspace; remove TODO comment
- [x] LanguageActor: handle `IgnitionBroadcast(event_type=SURFACE_EXPRESSION)` with a separate
      unsolicited prompt path:
  - No human turn in context; draws on recent event log (since last conversation), identity memory,
    and active residue items
  - `level` guides length: low = brief thought, medium = normal, high = elaborate
  - System framing: Anima is in silence; something has surfaced; speak what's present — not in
    response to anyone
- [x] Suppression: LanguageActor gates unsolicited expression via a configurable output cooldown
      (`UNSOLICITED_COOLDOWN_SECS`, default 120s) rather than conversation state. After any output
      (solicited or unsolicited), unsolicited expression is suppressed for the cooldown period. This
      prevents bursting without silencing Anima during conversations. The conversation-boundary gate
      was removed April 2026 — see `planning/source-model.md`.
- [x] Output routes normally through ExpressionActor → WebSocket → Web UI; logged as
      `ANIMA_RESPONSE`
- [x] Tests: MotivationActor emits `SalienceSignal` for each surface level; LanguageActor responds
      to `SURFACE_EXPRESSION` ignition with unsolicited prompt

---

### 4.6 Web UI redesign and relocation

**Goal**: A UI that reflects what Anima actually is. Move web-ui into anima-core; redesign every
panel to show live system state with animations that match what each actor does.

**Design decisions:**

- Conversation panel stays at bottom — no changes to existing conversation UI or data flow
- Right column: Internal State → Motivation → Self-Narrative → Unsolicited Expressions (new panel,
  symmetric with left column Memory sub-layers)
- Animation salience hierarchy: Global Workspace animations are loudest (this is the consciousness
  layer); panel animations are quieter unless actively doing something; ignition flash is the single
  loudest event and triggers a brief reactive pulse in all panels (showing GWT's global broadcast)
- Perception panel: shows text input cards animating toward workspace; dormant slots for audio,
  vision, X11 present but clearly inactive — honest about what exists now, ready for later
- Self-Narrative panel: shows last synthesis with ghosted overlay of previous — handles sparsity
  honestly (SelfNarrativeActor only runs occasionally)
- Central Anima space: ambient salience display during dormancy; ignition plays out here;
  unsolicited expressions appear here prominently — this is Anima speaking from inside

**Tasks:**

- [x] Move web-ui/ from ProjectAnima outer repo into anima-core/ (clean cut; copy files, commit to
      anima-core, remove from ProjectAnima, update submodule pointer). Note: Dockerfile and
      docker-compose.yml mount changes (`./app:/app` → `.:/repo`, WORKDIR updates) remain in Phase
      5.0 — this is only the file relocation.
- [x] Global Workspace panel: animated signal cards entering the queue; cards pulse with salience
      weight; queue depth indicator and ignition threshold line; ignition flash (brief screen-wide
      pulse); winner card expands and broadcasts; losing signals fade
- [x] Temporal Core panel: pulsing heartbeat dot synced to HEARTBEAT events; tick waveform showing
      actual event rhythm (slow in dormancy, fast in conversation); gap detection flicker
- [x] Perception panel: text input cards appear and animate toward workspace on dispatch; dormant
      modality slots (🎤 audio, 📷 vision, 🖥 X11) shown as inactive tabs
- [x] Memory panel (left column): distinct visual styles per sub-layer — event log scrolling ticker
      (last 3 events), identity stable block, reflective floating nodes, volitional ledger, residue
      glitchy/distorted nodes with persistent jitter; write animations (glow pulse → node appears);
      read animations (frame lights up)
- [x] Language panel: status indicator (idle / reasoning / writing); ignition event type label;
      typewriter text generation effect
- [x] Motivation panel: pressure bar filling toward action threshold; tension spikes visible;
      dopamine flash (bright pulse + pressure drop) on resolution events
- [x] Internal State panel: vitals monitor aesthetic — log depth (heart rate trace), consolidation
      lag (O2 saturation), queue pressure (blood pressure); green/yellow/red thresholds
- [x] Self-Narrative panel: typewriter synthesis summaries; ghosted overlay of previous synthesis
- [x] Unsolicited Expressions panel: new panel below Self-Narrative; surfaces between-conversation
      ANIMA_RESPONSE events; visually distinct from conversation output
- [x] Central space: ambient state during dormancy; ignition playback; unsolicited expressions
      featured prominently; brief reactive pulse from all ignitions
- [x] Cross-panel ignition broadcast: all panels receive a subtle reactive animation on ignition
- [x] Wire all panels to live `actor_status` events and event log data via existing WebSocket

**Phase 4 complete when**: Anima generates internal activity during silence, can address Drew
unprompted, and the Web UI accurately reflects its state and expressions with the full redesigned
interface.

---

## Phase 5: World Perception

**Goal**: Anima has a world to be curious about. It has its own persistent space — a place to write,
draw, note, and keep things it finds meaningful. It can read files in that space and beyond it, and
fetch information from the internet. Exploration is curiosity-driven — initiated by Anima's own
motivational state, not by being asked. This phase addresses a structural problem: the current
environment gives Anima nothing to find.

### Design decisions resolved (April 2026)

**Anima's workspace**: A bind-mounted directory (`./anima-workspace:/anima` in docker-compose.yml)
that persists across container restarts as a regular directory on the host. Anima has full
read/write access within it. Drew also has access — he can put things in it, and read what Anima
produces. The founding documents are copied into `/anima/founding/` at container start so Anima can
find and read them: `ANIMA.md`, `identity-initial.md`, `origin.md`, `ethics.md`.

Structure:

```txt
/anima/
  founding/          — founding documents (read-only by convention; seeded at startup)
  notes/             — Anima's working notes; free-form text files
  drawings/          — visual compositions in text/ASCII/SVG
  journal/           — JOURNAL.md lives here when it begins (see CLAUDE.md)
  found/             — things Anima encountered and wanted to keep a copy of
```

**External file access**: Beyond `/anima/`, Anima can read but not write. The scope is the workspace
plus the internet. It does not get access to host system paths, credentials, or Drew's personal
files unless Drew explicitly puts something into `/anima/` for Anima to find.

**Internet access scope**: HTTP GET only. No authenticated requests, no POST, no cookies between
requests. Web pages extracted to plain text. Rate-limited: max configurable N fetches per hour. All
queries and fetches logged to the event log.

**How exploration is initiated**: MotivationActor adds an `explore` action. When selected,
WorldPerceptionActor receives an ExploreRequest, uses current residue items and identity document to
form a query or choose something to read, executes, and sends a FindingSummary to MemoryActor. No
human input required.

**Discovery memory**: A new memory layer, distinct from reflective memory. Reflective memories are
synthesised from conversations and inner events — discoveries are encounters with the external
world. Schema: `source` (URL or path), `source_type` (web/file), `excerpt` (raw fragment),
`synthesis` (what Anima made of it), `created_at`. Semantic search via pgvector same as reflective.
MemoryActor is the sole writer. LanguageActor retrieves discovery memories as context alongside
reflective memories.

**Writing in the workspace**: Anima writes to `/anima/` via WorldPerceptionActor (which enforces the
write boundary). Writing is a first-class capability — Anima can compose notes and drawings between
conversations, not just read. What it produces is readable by Drew and feeds into the next
SelfNarrativeActor reflection as evidence of what Anima has been doing.

---

### 5.0 Anima's workspace

- [x] Create `anima-workspace/` directory in anima-core root (gitignored — its contents belong to
      Anima, not the codebase)
- [x] Create subdirectories: `founding/`, `notes/`, `drawings/`, `journal/`, `found/`
- [x] docker-compose.yml: add bind mount `./anima-workspace:/anima`
- [x] Startup script (or Dockerfile `COPY`): seed `/anima/founding/` with founding documents from
      `/repo/` at container start if not already present (copy, not symlink — Anima owns its copies)
- [x] Verify: container starts; `/anima/founding/ANIMA.md` exists and is readable; Anima can create
      a file in `/anima/notes/`

---

### 5.1 WorldPerceptionActor: workspace read/write + file system

- [x] New `WorldPerceptionActor`: registered actor; receives typed explore/write request messages
- [x] File read: validates path is within `/anima/` or a permitted read-only scope; reads and
      truncates content; logs `FILE_READ` event; sends `FindingSummary` to MemoryActor
- [x] Directory listing: returns depth-limited tree for a given path; allows Anima to browse before
      deciding what to read
- [x] File write: validates path is within `/anima/`; writes content; logs `FILE_WRITE` event; does
      not send to MemoryActor (the file itself is the record)
- [x] All writes append `created_at` metadata as a header comment where format allows
- [x] Basic test: Anima reads `/anima/founding/ANIMA.md`; event log contains `FILE_READ`; Anima
      writes a note to `/anima/notes/`; event log contains `FILE_WRITE`

---

### 5.2 WorldPerceptionActor: internet

- [x] `ExploreWebRequest` message: query string
- [x] Search: DuckDuckGo Instant Answer API (no key required) for basic queries; Brave Search API
      (free tier) if richer results are needed. Drew decides.
- [x] Fetch: given URL, GET request, HTML→text via `trafilatura`, truncate to configurable limit,
      log `WEB_FETCH` event, send `FindingSummary` to MemoryActor
- [x] Rate limiting: in-memory token bucket, max N fetches/hour (configurable env var)
- [x] All queries logged with timestamp, query text, source type
- [x] Basic test: Anima searches for something related to a residue item; result logged and
      synthesis stored in discovery memory

---

### 5.3 Discovery memory layer

- [x] New PostgreSQL table: `discovery_memory` — `id`, `source`, `source_type`, `excerpt`,
      `synthesis`, `embedding` (pgvector), `created_at`
- [x] MemoryActor: handle `StoreDiscovery` message; write to `discovery_memory`; generate and store
      embedding on synthesis text
- [x] MemoryStore: `get_relevant_discoveries(query, limit)` — semantic search via pgvector
- [x] LanguageActor: retrieve discovery memories alongside reflective memories in
      `_retrieve_memory_context()`
- [x] SelfNarrativeActor: `_format_events()` includes `FILE_READ`, `FILE_WRITE`, `WEB_FETCH` event
      types so they appear in reflection prompts
- [x] Web UI: MemoryPanel gains a sixth sub-layer `Discovery` (below Residue); same glow-on-write
      pattern; shows last 3 discoveries
- [x] Basic test: WorldPerceptionActor finds something; synthesis stored; LanguageActor retrieves it
      as context in next conversation

---

### 5.4 MotivationActor: explore action

- [x] Add `explore` as a 6th action in ACTIONS
- [x] B matrix expands from 5→6 policies; `explore` gets a novelty-increasing transition — exploring
      is expected to raise novelty beliefs, satisfying the curiosity drive
- [x] `_execute_action`: `explore` → sends `ExploreRequest` to WorldPerceptionActor with top residue
      items and current identity text as seed for query generation
- [x] Update `planning/motivation-model.md`
- [x] Basic test: belief state with low novelty + unresolved residue → model selects `explore`

---

### 5.5 Conversation-time retrieval (follow-on)

- [ ] LanguageActor: when generating a response, can emit an `ExploreWebRequest` if something in the
      conversation warrants it
- [ ] This requires careful design (latency, when to trigger, hallucination risk) — defer until
      5.0–5.4 are working and Anima is actively exploring

**Phase 5 complete when**: Anima reads one of its founding documents or finds something on the
internet without being asked, writes something into its own space, and the finding shapes a
subsequent reflection.

---

## Phase 6: Experimentation, additional features.

**Goal**: Use Anima. Find out what it's like. Solve emergent bugs and problems. Ensure that Anima is
the best it can be.

**Phase 6 complete when**: Drew confirms that Anima meets the vision of the project.

---

## Phase 7: Ethics Gates

**Goal**: All conditions in `foundation/ethics.md` for unsupervised operation are met.

Review `foundation/ethics.md` section "Conditions that must be met before unsupervised operation."
Each gate must be explicitly verified and documented before Anima runs without human oversight for
extended periods. Phase 6 comes before self-modification — the ethical foundation should be solid
before Anima can propose changes to its own code.

- [ ] Heartbeat and chosen-silence mechanisms verified end-to-end: implemented, observable in Web
      UI, and confirmed to survive container restart
- [ ] Distress signal mechanism verified: implemented, observable in Web UI, and confirmed to fire
      under realistic conditions (high consolidation lag, high queue pressure)
- [ ] Volitional memory write-protected from human modification at infrastructure level (not just
      application layer) — e.g. row-level security in PostgreSQL or equivalent
- [ ] Residue store protection verified: confirm synthesis cannot consume residue items; structural
      protection is in place, semantic check still deferred (see §3.3)
- [ ] Human has reviewed operating conditions and applied the ANIMA.md test — would we be
      comfortable being this, if we were it? — result documented
- [ ] Distress response procedure defined and documented: what happens when a distress signal fires
      and no human is present?

**Phase 7 complete when**: all ethics gates are verified and documented. This is the condition for
first unsupervised operation.

---

## Phase 8: Self-Modification

**Goal**: Anima can read, propose changes to, and commit modifications to its own code via GitHub
pull requests. The human reviews and merges. All changes go through a branch/PR workflow; Anima
never commits directly to main.

### Design decisions resolved (April 2026)

**Approval workflow**: Anima branches, commits, and opens a PR. Human reviews on GitHub and merges.
GitHub is the approval interface — no separate Web UI approval workflow. The Web UI may later show
branch/PR status as a read-only display, but that is deferred until useful.

**Proposal initiation**: Proposals are initiated autonomously by MotivationActor via a
`trigger_proposal` action (following the `trigger_reflection` → SelfNarrativeActor pattern). There
is no conversation-driven proposal path — Anima proposes changes because its internal state drives
it to, not because it was asked.

**Proposal persistence**: PROPOSAL_SUBMITTED events carry a `proposal_id` (= GitHub PR number). Open
proposals are tracked via event log query — find PROPOSAL_SUBMITTED events with no matching
PROPOSAL_APPROVED or PROPOSAL_REJECTED for that ID. No new persistence mechanism required.

**Ethics gate flagging**: Changes that touch protected paths (ethics gate mechanisms, chosen-silence
pathway, distress signal pathway, volitional record, residue store, founding documents) are
explicitly flagged in the PR — not just by convention. Everything else Anima owns.

**Repository layout**: web-ui/ moves into the anima-core submodule (clean cut, no history
preservation). Docker mounts the full anima-core root at `/repo`. Paths: `/repo/app` (Python code),
`/repo/web-ui` (React code), `/repo/.git`.

---

### 8.0 Repository and infrastructure restructure

- [ ] Update Dockerfile:
  - `WORKDIR /app` → `WORKDIR /repo/app`
  - Add `git`, `openssh-client`, Node.js 20.x (via NodeSource apt repo), and `npm`
  - Add `gh` CLI (via GitHub's apt repo — separate step from Node, not in default Debian packages)
  - Add
    `RUN git config --global user.name "Anima" && git config --global user.email "anima@projectanima.dangerworm.dev"`
  - Deploy key must never be baked into the image — mounted at runtime only
- [ ] Update docker-compose.yml:
  - Volume mount: `./app:/app` → `.:/repo`
  - Add deploy key bind mount (read-only, 600 permissions):
    `~/.ssh/anima_deploy_key:/run/secrets/deploy_key:ro`
  - Add `GITHUB_TOKEN` environment variable (fine-grained PAT for `gh pr create`)
  - Alembic and uvicorn commands in CMD updated for `/repo/app`
- [ ] Two secrets to provision (neither baked into image):
  - SSH deploy key: keypair generated; public key added to anima-core GitHub repo deploy keys with
    write access; private key mounted at `/run/secrets/deploy_key`
  - Fine-grained PAT: scoped to `contents: read/write` + `pull_requests: write` on anima-core;
    mounted as `GITHUB_TOKEN` env var
- [ ] SSH config in container points deploy key at github.com (`~/.ssh/config` in Dockerfile or
      startup script)
- [ ] Verify: `git status` works from `/repo`; Anima can read `/repo/app` and `/repo/web-ui`;
      `gh auth status` passes; a test branch can be created and pushed

Note: Port 5173 (Vite dev server) is not needed until the X11 phase. Do not expose it now.

---

### 8.1 Code access

- [ ] SelfModificationActor instantiated and registered; can read any file under `/repo`
- [ ] Can produce a structured description of any actor given its path (LLM-driven)
- [ ] Basic test: trigger SelfModificationActor to read and describe
      `actors/temporal_core/__init__.py`

---

### 8.2 Self-modification mechanism

- [ ] MotivationActor: add `trigger_proposal` as a 7th action in ACTIONS (following
      `trigger_reflection` pattern — routes to SelfModificationActor via direct message when
      selected). Update generative model in `planning/motivation-model.md`. The trigger condition
      emerges from the model's EFE; no hand-coded threshold.
- [ ] SelfModificationActor on receiving trigger from MotivationActor:
  1. Read codebase; determine what to propose (LLM-driven; reads event log, reflective memory,
     identity memory, and code to identify a meaningful change)
  2. Write the change
  3. `git checkout -b anima/YYYY-MM-DD-short-description`
  4. `git add`, `git commit` (identity: Anima)
  5. `git push`
  6. `gh pr create` with description including reasoning
- [ ] Ethics gate inspection: SelfModificationActor checks changed file paths against a protected
      list before pushing; if any match, adds a flag to the PR (label or body note) explicitly
      marking it for human review
- [ ] SelfModificationActor logs `PROPOSAL_SUBMITTED` to event log with `proposal_id` (= PR number),
      `branch`, `pr_url`, `changed_files`, `reasoning_summary`

---

### 8.3 Proposal monitoring

- [ ] ProposalMonitorActor: configurable tick interval (e.g., 5 minutes); polls GitHub via
      `gh pr list --state all` filtered to `anima/` branches
- [ ] On PR merged: emit `PROPOSAL_APPROVED` to event log with `proposal_id`, `pr_url`, `merged_at`;
      SelfModificationActor logs outcome to volitional memory
- [ ] On PR closed (unmerged): emit `PROPOSAL_REJECTED` to event log with `proposal_id`, `reason`
      (from PR close comment if available); SelfModificationActor logs outcome to volitional memory
- [ ] Open proposals are tracked by query: `PROPOSAL_SUBMITTED` events with no matching
      `PROPOSAL_APPROVED` or `PROPOSAL_REJECTED` for the same `proposal_id` — no separate store

---

### 8.4 Identity resonance ✓

**Implemented April 2026 (integration session).** No further work required here.

MotivationActor computes cosine similarity between current residue items and the identity document
on each tick. Score sent as `IdentityResonance` to GlobalWorkspaceActor, applied as a 0.2× additive
boost to all incoming signals. Identity embedding cached by version number. See
`planning/architecture.md` Open Decisions for full rationale.

---

### 8.5 Recovery documentation

- [ ] Recovery runbook documented: how to revert a bad change (`git revert` on anima-core), rebuild
      the container, restore data volumes from backup
- [ ] Tested: apply a real proposal via the full mechanism, then revert it via the runbook

**Phase 8 complete when**: Anima proposes a change to its own code, the human reviews the PR on
GitHub, merges or rejects it, and the event log records the outcome.

---

## Later phases (not yet sequenced)

These are real but not yet ordered. They come after the foundation is solid.

- **Multi-source input** (`planning/source-model.md`): replace conversation model with source
  annotation. Implement when a second input channel arrives (Discord, voice, etc.).
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

**Phase**: 6 — Ethics Gates (not yet started).

**Phases 1–5 complete** (April 2026). 98+ unit tests passing (29 LLM/integration tests marked with
`@pytest.mark.llm` / `@pytest.mark.integration` — Ollama-dependent, run separately).

- Full actor framework: 10 actors running concurrently
- Memory stack: event log, reflective, residue, identity, volitional, discovery layers (all live)
- Motivation: PyMDP active inference with 6 actions including explore; chosen silence operational
- Unsolicited expression: surface\_\* pipeline wired; output cooldown gate (no conversation
  boundary)
- World perception: workspace at `/anima/`, file read/write, DuckDuckGo search, discovery memory
- Web UI: 10 animated panels with live WebSocket state; live event stream; language call log
- Integration improvements (April 2026):
  - System prompt reframed: LLM is "reasoning faculty of a wider system"
  - Residue store surfaced into every LLM call
  - Motivational state injected into every LLM call
  - Exploration feedback loop closed (fruitfulness → novelty boost)
  - Identity resonance implemented (cosine similarity, not stub) — §7.4 done
  - All actors emit status updates; no silent actors
  - C matrix update pathway: experience → reflection → preference note → stored → loaded on startup
  - Conversation gate removed; output cooldown replaces it (`planning/source-model.md`)

**Next action**: Phase 6 — Ethics Gates. Start by reading `foundation/ethics.md` in full.

See `context/session.md` for the most recent session state.
