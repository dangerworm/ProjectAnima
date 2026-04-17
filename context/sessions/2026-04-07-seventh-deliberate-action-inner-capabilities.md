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
