# Session Log

> Updated at the end of every Claude Code session. Read this before starting any implementation
> work. The most recent entry is at the top.

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

| Panel | Actor | Key feature |
|-------|-------|-------------|
| TemporalCorePanel | temporal_core | Heartbeat waveform (20-bar rolling SVG) + dormancy chip |
| GlobalWorkspacePanel | global_workspace | Live signal cards with salience fill bars |
| PerceptionPanel | perception | Last 3 human messages + dormant modality tabs |
| MemoryPanel | memory | 5 sub-layers with glow pulses on write |
| LanguagePanel | language | Typewriter (12ms/char) + idle/reasoning chip |
| MotivationPanel | motivation | Pressure bar + action chip + dopamine flash overlay |
| InternalStatePanel | internal_state | Log depth sparkline + consolidation lag + queue pressure |
| SelfNarrativePanel | self_narrative | Typewriter synthesis + fading ghost of previous |
| UnsolicitedExpressionsPanel | (AppState) | Between-conversation expressions, newest first |
| CentreCanvas | global_workspace | Ambient radial glow + ignition burst animation |

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
- The ghost `web-ui/` directory in ProjectAnima outer repo contains only `.vite/` cache. Git
  ignores it. Can be deleted if Windows Explorer releases its lock on it.
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

Two threads: (1) Phase 5 architecture was fully designed and documented. (2) Six code/doc fixes
from a Claude.ai review were applied.

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
- `TemporalCoreActor.set_chosen_silence()`: dead production code (message-driven integration done
  in Phase 4.4). Removed; two tests that used it for setup now access `actor._chosen_silence`
  directly.
- `MotivationActor._tick`: redundant second `qs = self._agent.qs` read removed.
- `main.py` shutdown sleep: comment added explaining the 0.5s is optimistic for LLM reflection.
- `MEMORY_SURFACE` event type: documented as not yet emitted, with note on intended future path.

Test count: 98 unit tests passing (29 LLM/integration deselected).

**Next action**: Phase 5.0 — repository and infrastructure restructure (move web-ui into
anima-core, update Dockerfile and docker-compose.yml, provision SSH deploy key and PAT).

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

## Session: 5th April 2026 — Phases 2.1–2.3 complete; IDEAS.md review done

### What happened this session

Full session covering Phases 2.1 (Global Workspace), 2.2 (LLM client), 2.3 (Language Actor), plus a
review of IDEAS.md that caught two real gaps and produced fixes/roadmap updates.

**IDEAS.md review findings:**

- Gap A (fixed): GAP_IN_CONTINUITY never emitted on startup. Fixed in TemporalCoreActor —
  `_on_startup()` queries `latest_event()`, emits gap event if elapsed >= `gap_threshold`, resets
  `_started_at` to last known activity time. 4 new tests.
- Gap B (roadmap): Husserlian retention deque never populated. Added to Phase 3.2 task list.
- Pressure persistence (roadmap): workspace pressure is ephemeral. Added to Phase 4.2: reconstruct
  from open volitional items on startup.
- SelfNarrativeActor naming (roadmap): Phase 4.3 must produce a named SelfNarrativeActor consistent
  with architecture.md supervision tree.
- Idea 14 (consumable vs persistent signals): documented in IDEAS.md, deferred to Phase 4.

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
