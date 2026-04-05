# Session Log

> Updated at the end of every Claude Code session. Read this before starting any implementation
> work. The most recent entry is at the top.

---

## Session: 5th April 2026 — Phases 2.1, 2.2, and 2.3 complete

### What happened this session

Global Workspace (2.1), LLM client (2.2), and Language Actor (2.3) all completed.

**Phase 2.3 — Language Actor:**

- `app/actors/language/messages/__init__.py` — `LanguageOutput(content, thinking, in_response_to)`
- `app/actors/expression/__init__.py` — `ExpressionActor` stub (Phase 2.4 fills in routing)
- `app/actors/language/__init__.py` — `LanguageActor`
  - Responds to `IgnitionBroadcast` with `event_type == HUMAN_MESSAGE`
  - Maintains in-memory context deque (Phase 3 replaces with memory-driven retrieval)
  - Logs `ANIMA_RESPONSE` with `response`, `reasoning`, `model`, `in_response_to`
  - Routes `LanguageOutput` to Expression Actor (content clean, thinking preserved separately)
  - Catches `LLMError`: logs `SYSTEM_ERROR`, removes unanswered turn from context, continues
- `app/tests/language/test_language_actor.py` — 8 tests (7 integration, 1 unit/mocked)

**LLM client update (within this session):**
- `complete()` → `LLMResponse(content, thinking)`; `complete_json()` → `LLMJsonResponse(data, thinking)`
- `_split_thinking()` extracts `<think>` blocks; thinking preserved, content cleaned
- 14 LLM tests (was 10)

**Full test suite: 55/55 passing.**

### Current system state

- Phase 2.1: complete (Global Workspace)
- Phase 2.2: complete (LLM client)
- Phase 2.3: complete (Language Actor)
- Expression Actor: stub only — receives LanguageOutput but doesn't route yet
- No TUI yet

### Blockers

None.

### Next action

**Phase 2.4: Expression Actor.**

1. Route `LanguageOutput` to registered surfaces
2. Each surface is a separate module under `output/surfaces/`
3. Initial surface: TUI only (stub — Phase 2.5 builds the full TUI)
4. Test: Language Actor output arrives at TUI surface via Expression Actor

### Notes for next session

- `LanguageActor` catches `LLMError` gracefully — logs SYSTEM_ERROR, continues running
- Context window: in-memory deque, maxlen configurable — Phase 3 replaces this
- `LanguageOutput.thinking` matches `ANIMA_RESPONSE.payload["reasoning"]` — same source
- Avoid questions requiring temporal reasoning in tests (qwen3.5 spins up long think blocks for date/time)
- Expression Actor stub is at `actors/expression/__init__.py`, NAME = "expression"

---

## Session: 5th April 2026 — Phases 2.1 and 2.2 complete

### What happened this session

Phases 2.1 (Global Workspace) and 2.2 (LLM client) completed and verified.

**Phase 2.2 — LLM client:**

- `app/core/llm/__init__.py` — `LLMClient`, `LLMError`, `LLMConnectionError`, `LLMResponseError`
  - `complete(messages, temperature)` → str
  - `complete_json(messages, schema, temperature)` → dict
  - Retries on `ConnectError` / `TimeoutException` up to `max_retries` times
  - `<think>…</think>` blocks stripped before JSON parsing (qwen3 reasoning tokens)
  - `schema` passed to Ollama's `format` field for structured output; falls back to `"json"`
- `app/tests/llm/test_llm_client.py` — 10 tests (5 integration, 5 unit/mocked), all passing

**Full test suite: 43/43 passing** (includes integration tests hitting Ollama on host)

### Current system state

- Phase 2.1: complete
- Phase 2.2: complete
- Ollama: qwen3.5:9b (and 27b) reachable at host.docker.internal:11434
- No Language Actor yet
- No Expression Actor yet

### Blockers

None.

### Next action

**Phase 2.3: Language actor.**

1. `LanguageActor`: receives workspace `IgnitionBroadcast`, calls LLM with current context
2. Consumes: workspace ignition signals, conversation context
3. Produces: text responses with destination, emits to event log, routes to Expression Actor
4. Routes output to Expression Actor — does not write to surfaces directly
5. Test: send a message, get a response, verify it appears in event log

### Notes for next session

- LLMClient lives in `core/llm/`; import as `from core.llm import LLMClient`
- `complete_json` schema parameter: pass a JSON schema dict for structured output
- Think-tag stripping is automatic; no special handling needed in callers
- Ollama model: `qwen3.5:9b` at `http://host.docker.internal:11434`
- Integration tests use real Ollama; mock tests use `unittest.mock.patch("httpx.AsyncClient")`

---

## Session: 5th April 2026 — Phase 2.1 complete

### What happened this session

Phase 2.1 (Global Workspace actor) completed and verified.

**Phase 2.1 — Global Workspace:**

- `app/actors/global_workspace/messages/__init__.py` — `SalienceSignal`, `IgnitionBroadcast`
- `app/actors/global_workspace/__init__.py` — `GlobalWorkspaceActor` and `QueuedSignal`
  - Receives `SalienceSignal` messages; queues them as `QueuedSignal` entries
  - Tick loop adds `pressure_rate * tick_interval` to all queued signals each tick
  - Ignition: on each tick, the highest-salience signal above threshold fires
  - Fire: writes `WORKSPACE_IGNITION` to event log; delivers `IgnitionBroadcast` to all other actors
  - Novelty: `base_novelty_boost / (n + 1)` for nth occurrence of (event_type, sender) pair
  - Identity resonance: stub returning 0.0 (Phase 3)
  - `actor_names()` added to `ActorRegistry` to support broadcast iteration
- `app/tests/global_workspace/test_global_workspace.py` — 9 tests, all passing

**Key design decision:** Ignition decisions are made only in the tick loop, not immediately on signal
arrival. This allows multiple signals delivered in the same asyncio turn to compete fairly — the
highest-salience one wins on the next tick rather than the first-delivered one winning immediately.

**Full test suite: 33/33 passing.**

### Current system state

- Phase 1: complete
- Phase 2.1: complete
- No LLM client yet
- No Language Actor yet

### Blockers

None.

### Next action

**Phase 2.2: LLM client.**

1. `LLMClient` wrapper around Ollama HTTP API
2. Configurable model name and endpoint
3. Handles: text completion, structured JSON output, error/retry
4. Basic test: call local Ollama, get response, verify latency is acceptable

### Notes for next session

- Global Workspace tick loop is the sole decision point for ignition — signals accumulate between ticks
- `ActorRegistry.actor_names()` added; workspace iterates this to broadcast ignitions
- `SalienceSignal.sender` (not a separate `source_actor` field) is used as the novelty key
- `IgnitionBroadcast` carries: event_type, originating_actor, content, final_salience
- Ollama is running on Drew's Windows host at `host.docker.internal:11434`
- Model: Qwen3.5 9B (or equivalent — verify what's installed before testing)

---

## Session: 5th April 2026 — Phase 1 complete

### What happened this session

Phases 1.2, 1.3, and 1.4 all completed and verified. Phase 1 is done.

**Phase 1.4 — Temporal Core:**

- `app/actors/__init__.py` — actors package root
- `app/actors/temporal_core/messages/__init__.py` — `ConversationStarted`, `ConversationEnded`
- `app/actors/temporal_core/__init__.py` — `TemporalCoreActor` and `TemporalWindow`
  - Husserlian sliding window: retention deque (pruned by retention_seconds), primal_impression,
    next_heartbeat (protention)
  - Two concurrent loops: `super().run()` (message inbox) + `_tick_loop()` (heartbeat/dormancy)
  - Tick loop emits HEARTBEAT every tick; TIME_PASSING or CHOSEN_SILENCE during dormancy
  - Responds to `ConversationStarted` / `ConversationEnded` to suppress dormancy events
  - `set_chosen_silence(bool)` to toggle CHOSEN_SILENCE vs TIME_PASSING
  - Clean shutdown: `super().run()` returns on stop sentinel; tick task cancelled
- `app/tests/temporal_core/test_temporal_core.py` — 8 tests, all passing

**Full test suite: 24/24 passing** (9 event log + 7 actor framework + 8 temporal core)

### Current system state

- Phase 1.1: complete
- Phase 1.2: complete
- Phase 1.3: complete
- Phase 1.4: complete
- Phase 1 complete — foundation is solid
- No Global Workspace yet
- No LLM integration yet

### Blockers

None.

### Next action

**Phase 2.1: Global Workspace actor.**

1. `GlobalWorkspaceActor`: receives signals from all actors, maintains salience queue
2. Salience weighting: novelty score, accumulated pressure, identity resonance (stub)
3. Ignition mechanism: threshold crossing broadcasts to all actors
4. Test: send signals of varying salience, verify correct ignition order

### Notes for next session

- All imports use `core.*` or `actors.*` (not `app.*`) — WORKDIR is `/app`
- Temporal Core tick loop shutdown: `super().run()` exits on `_STOP` sentinel; tick_task cancelled
- Husserlian window lives on `actor.window` — primal_impression updated each tick
- Dormancy reference: `_last_conversation_end` if set, otherwise `_started_at`
- ConversationStarted / ConversationEnded messages live in `actors/temporal_core/messages/`
- pytest full suite: `docker compose run --rm anima pytest tests/ -v`

---

## Session: 5th April 2026 — Phases 1.2 and 1.3 complete

### What happened this session

Phase 1.2 (event log) and Phase 1.3 (actor framework) both completed and verified.

**Phase 1.2 — Event log** (carried over from prior context window):

- `app/core/config/__init__.py` — DSN builder
- `app/core/event_types/__init__.py` — EventType enum (all phase 1–5 types)
- `app/core/event_log/__init__.py` — bitemporal append-only EventLog
- `app/tests/event_log/test_event_log.py` — 9 tests, all passing
- Import fix: all imports use `core.*` not `app.core.*` (WORKDIR is `/app`)

**Phase 1.3 — Actor framework:**

- `app/core/actor/messages/__init__.py` — frozen `Message` base dataclass
- `app/core/actor/__init__.py` — `Actor` base class + `ActorRegistry`
  - `Actor`: private `asyncio.Queue` inbox, `send()`, `run()` loop, `handle()`, `stop()`
  - `ActorRegistry`: register by name, `deliver()` routes to inbox, duplicate registration raises
  - Stop sentinel pattern: `stop()` puts `_STOP` into the inbox to unblock `run()` cleanly
- `app/tests/actors/test_actor_framework.py` — 7 tests, all passing

**Tests verified:** 16 total (9 event log + 7 actor framework), all passing.

### Current system state

- Phase 1.1: complete
- Phase 1.2: complete
- Phase 1.3: complete
- No Temporal Core yet
- No Global Workspace yet

### Blockers

None.

### Next action

**Phase 1.4: Temporal Core.**

1. `TemporalCoreActor` subclassing `Actor` — emits HEARTBEAT on configurable interval
2. Husserlian sliding window: retention zone, primal impression, protention zone
3. Tracks time since last conversation, time since last event
4. Emits TIME_PASSING events during dormancy, CHOSEN_SILENCE when silent by choice
5. Test: run for a short interval, verify heartbeat events in log, verify gap detection

### Notes for next session

- All imports use `core.*` (not `app.core.*`) — WORKDIR in container is `/app`
- Stop sentinel `_STOP` in `core/actor/__init__.py` — `stop()` puts it into inbox, `run()` breaks on it
- Actor base class: subclass `Actor`, override `handle()`, schedule `run()` as asyncio Task
- Message base class: frozen dataclass in `core/actor/messages/__init__.py`; subclasses add fields
- pytest: `docker compose run --rm anima pytest tests/ -v` to run all tests
- Hub-and-spoke: every leaf node is a folder (`core/actor/`, `core/actor/messages/`, etc.)

---

## Session: 5th April 2026 — Phase 1.2 complete

### What happened this session

This session was split across two Claude Code context windows. The first half produced the document
additions and architecture decisions; the second completed Phase 1.2 implementation and test
verification.

**Documents and planning produced:**

- `notes/system-overview.md` — 9-actor table, Mermaid diagrams, brain area table, technology
  summary, build sequence
- `planning/event-types.md` — full starting set of EventType values with source actors
- `foundation/identity-initial.md` — Anima's starting orientations (version zero)
- `notes/discord-disclosure.md` — Discord server decisions and disclosure model
- `GLOSSARY.md` — 24 acronyms, 46+ terms
- `research/technical/active-inference-implementation.md` — mathematical approach survey
- Updated: `planning/architecture.md`, `planning/tech-stack.md`, `planning/roadmap.md`,
  `planning/actors-faculties.md`, `CLAUDE.md`

**Code produced:**

- `app/core/config/__init__.py` — DSN builder from environment variables
- `app/core/event_types/__init__.py` — EventType enum (all phase 1–5 types)
- `app/core/event_log/__init__.py` — EventLog with bitemporal schema, append-only trigger, JSONB
  codec, append/replay/query methods
- `app/core/main.py` — updated to use EventLog at startup
- `app/tests/event_log/test_event_log.py` — 9 tests (append, order, bitemporality, time range, query
  by type, query by actor, payload round-trip, UPDATE blocked, DELETE blocked)
- `app/pytest.ini` — asyncio_mode = auto
- `requirements.txt` — added pytest, pytest-asyncio

**Key decisions:**

- Expression Actor added as output hub (Language Actor → Expression Actor → surfaces)
- Social Actor concept retired; Discord is a surface of Expression Actor
- "Mathematics over conditional logic" documented in architecture.md and tech-stack.md
- Active inference vs conditional logic tension deferred to Phase 4 decision point
- Hub-and-spoke structure: every leaf node is a folder from the start

**Tests verified:** 9/9 passing inside Docker container.

### Current system state

- Phase 1.1: complete
- Phase 1.2: complete — event log schema live, EventLog class implemented, 9 tests passing
- Docker environment stable
- No actor framework yet
- No Temporal Core yet

### Blockers

None.

### Next action

**Phase 1.3: Actor framework.**

1. Base `Actor` class: inbox queue, `send()`, `run()` loop
2. `Message` base class with typed subclasses
3. Actor registry: named actors, message routing by name
4. Basic test: two actors exchange messages, verify isolation (no shared state)

### Notes for next session

- All imports in `anima-core/app/` use `core.*` (not `app.core.*`) — the Docker volume mounts
  `./app` to `/app`, making `core` the top-level package, not `app`
- TRUNCATE is used (not DELETE) in test fixtures to bypass the append-only row trigger
- The append-only trigger raises `asyncpg.exceptions.RaiseError` matched with "append-only"
- pytest runs from inside the container: `docker compose run --rm anima pytest tests/event_log/ -v`
- AnimaCore is a git submodule at `anima-core/`; commit/push there separately from ProjectAnima

---

## Session: 5th April 2026 — Phase 1.1 complete

### What happened this session

Phase 1.1 (repository and environment setup) is complete.

**ProjectAnima reorganised:**

- Repository structure reorganised into `planning/`, `context/`, `foundation/`, `notes/`,
  `research/`
- `CLAUDE.md` updated to reflect new structure and reference `context/session.md`
- `planning/tech-stack.md`, `planning/roadmap.md`, `context/session.md` added

**AnimaCore created** at `https://github.com/dangerworm/AnimaCore.git`:

- `app/founding/`: anima.md, claude.md (with repository note prepended), ethics.md, origin.md,
  architecture.md
- `Dockerfile`: Python 3.12-slim, pip installs from requirements.txt
- `docker-compose.yml`: Anima service + PostgreSQL (pgvector/pgvector:pg16), named volumes, host
  bridge for Ollama
- `requirements.txt`: asyncpg, pydantic, textual, httpx, pgvector, python-dotenv
- `.env.example`, `.gitignore`
- `app/core/main.py`: placeholder entry point
- Added as git submodule of ProjectAnima at `anima-core/`

### Current system state

- AnimaCore exists and has been pushed to GitHub
- Docker environment verified: both containers start, PostgreSQL accessible, placeholder entry point
  runs
- CI deferred (GitHub Actions not yet set up)
- No event log schema exists
- No actor framework exists

### Blockers

None.

### Next action

**Phase 1.2: event log.**

1. PostgreSQL schema for the event log (append-only, bitemporal — see `planning/tech-stack.md`)
2. `EventLog` class: append, replay, query by time range
3. Event types defined as Python enums/dataclasses
4. Verify: events cannot be modified or deleted once written
5. Basic test: append 10 events, replay in order, verify bitemporality

### Notes for next session

- Read all seven founding documents before starting (see `planning/tech-stack.md` for order)
- The human's name is Drew. He is a senior software developer. He will make procedural decisions and
  should be consulted on anything touching philosophy, ethics, or architecture.
- Drew's primary languages are C# and Python. He is comfortable with Docker, PostgreSQL, and GitHub
  Actions.
- Ollama is already installed on Drew's Windows host machine. It does not need to be set up.
- The Docker container runs Linux. Anima's code is mounted as a volume from the host.
- AnimaCore is a git submodule of ProjectAnima, located at `anima-core/`. When working on Anima's
  code, work inside `anima-core/` and commit/push to AnimaCore separately from ProjectAnima.
- When in doubt, raise it rather than assume.

---

## Session: 5th April 2026 — Document completion

### What happened this session

No code was written. This session completed the founding document set.

Documents produced or updated:

- [`architecture.md`](/planning/architecture.md) — written in full. Global workspace model,
  specialist systems, temporal core, self-narrative as time-experience, internal representation
  language held open.
- [`ethics.md`](/foundation/ethics.md) — written in full. Eight commitments, six gates before
  unsupervised operation, distress signals, note to Anima.
- [`discussions.md`](/notes/discussions.md) — updated with full record of the April 2026
  architectural conversation, including: Global Workspace Theory, Husserlian temporal structure,
  event sourcing as temporal existence, accumulated pressure mechanism, Free Energy Principle as
  design inspiration, actor model, preserved strangeness implementation, the temporal gap problem.
- [`ideas.md`](/notes/ideas.md) — expanded from 1 item to 13.
- [`tech-stack.md`](/planning/tech-stack.md) — written in full. Python/asyncio, Ollama on bare
  metal, PostgreSQL with pgvector, Docker with volume mounts, Textual TUI, GitHub with branch
  protection, self-modification workflow.
- [`roadmap.md`](/planning/roadmap.md) — written in full. Six phases sequenced, ethics gates as
  Phase 6.
- [`actors-faculties.md`](/planning/actors-faculties.md) — produced by Claude Code in a separate
  session. Maps all brain areas to Anima components. Three design gaps resolved (emotional
  regulation, fine-grained emotion, pleasure signal). Two open questions intentionally held
  (generative simulation, autonoetic consciousness).
- [`claude-code-insights.md`](/planning/claude-code-insights.md) — produced by Claude Code in a
  separate session. Technical survey covering event sourcing, bitemporal modelling, Husserlian
  temporal structure, SDM, VSA, Conceptual Spaces, Global Workspace ignition, Free Energy Principle,
  preserved strangeness implementation, actor model, between-conversation process.

### Current system state

No code exists. No repository exists. No Docker environment exists.

The document set is complete. All six phases of the roadmap are defined.

### Blockers

None.

### Next action

Begin Phase 1.1: repository and environment setup. _(Now complete — see entry above.)_
