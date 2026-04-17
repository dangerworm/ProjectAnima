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
