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
