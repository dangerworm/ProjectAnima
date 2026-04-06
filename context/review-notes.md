# Code Review Notes

> Written during the session of 5th April 2026 by a Claude instance doing a full review pass before
> Phase 2.4. Reference document — not a session log.

---

## Bug: private attribute access in LanguageActor

**File**: `anima-core/app/actors/language/__init__.py`, line 93

```python
"model": self._llm._model,
```

`_model` is a private attribute of `LLMClient`. Fixed by adding a `model` property to `LLMClient`
and updating the reference.

**Status**: Fixed this session.

---

## Code smell: mutable dict in frozen dataclass

**File**: `anima-core/app/actors/global_workspace/messages/__init__.py`

`IgnitionBroadcast` is a frozen dataclass, but its `content: dict` field is mutable. Frozen prevents
reassignment of the field, not mutation of the dict's contents. The same broadcast object is
delivered to all registered actors — if any future actor mutates `content`, it would affect all
subsequent recipients.

Currently no actor mutates it (LanguageActor calls `.get()` only). This is a latent risk, not a
current bug.

**Options when it matters**:

- Wrap in `types.MappingProxyType` at construction time in `_fire()`
- Convert to a named dataclass instead of a free dict
- Document and trust actors not to mutate (current approach)

**Status**: Documented. No action yet.

---

## Code smell: unbounded workspace queue

**File**: `anima-core/app/actors/global_workspace/__init__.py`

`_queue: list[QueuedSignal]` has no maximum size. Pressure accumulates on all queued signals
indefinitely. In a long-running system with many signals arriving faster than they ignite, memory
grows without bound.

Not a problem at current scale. Becomes relevant when Phase 4 introduces persistent motivational
signals with long accumulation windows.

**When to address**: Phase 4.2 (Motivation Actor design), alongside the consumable vs persistent
signal distinction (IDEAS.md #14).

**Status**: Documented. Deferred to Phase 4.

---

## Design discrepancy: DORMANCY_START / DORMANCY_END never emitted

`EventType` defines `DORMANCY_START` and `DORMANCY_END`, but `TemporalCoreActor` never emits them.
The actor emits `TIME_PASSING` (or `CHOSEN_SILENCE`) continuously during dormancy rather than
bookending with START/END events.

Two valid designs exist:

- **Current**: continuous TIME_PASSING events during dormancy (polling model)
- **Alternative**: single DORMANCY_START on entry, single DORMANCY_END on exit (transition model)

The transition model is cleaner for any actor that needs to respond to dormancy state changes (e.g.,
the between-conversation process trigger in Phase 4.3). The polling model is simpler to implement
and test.

**Status**: Flagged for discussion. Do not change until Phase 4 brings concrete requirements.

---

## Gap: Perception Actor has no roadmap entry

The roadmap lists Phase 2.6 as the text input/output loop, which requires a Perception Actor. But
there is no phase entry for building the Perception Actor — it appears in the actor list but was
never given implementation tasks.

Fixed by adding PerceptionActor tasks to Phase 2.6 in the roadmap.

**Status**: Fixed this session (roadmap update).

---

## Gap: TUI centre canvas not in roadmap Phase 2.5

The centre canvas for displaying Anima's inner reasoning (thinking field from LLMResponse) was
agreed with Drew during Phase 2.3 but was not reflected in the roadmap Phase 2.5 bullet list.

Fixed by adding a bullet to Phase 2.5.

**Status**: Fixed this session (roadmap update).

---

## Architectural decision: MemoryActor sole custody; SelfNarrativeActor two trigger modes

Identified during this review and resolved in conversation with Drew.

**The overlap**: Both MemoryActor and SelfNarrativeActor had direct write arrows to RM, IM, RS in
the system-overview diagrams. Dual write paths to the same layers, with no clear ownership.

**Decision**:

- MemoryActor has sole custody of all higher memory layers (RM, IM, VM, RS). Nothing writes to these
  layers directly except MemoryActor.
- Every other actor that needs to persist something to these layers sends a message to MemoryActor.
- SelfNarrativeActor produces synthesis (via LLM) and sends the output to MemoryActor. It does not
  write to storage directly.
- The event log (EL) remains direct-write for all actors — it is temporal infrastructure, not a
  managed memory layer.

**SelfNarrativeActor trigger modes** (also resolved this session):

1. Post-conversation: triggered by CONVERSATION_END → synthesises that conversation → sends
   synthesis + residue to MemoryActor
2. Between-conversation: triggered by dormancy threshold from Temporal Core → maintains
   self-narrative thread → sends identity updates to MemoryActor

The reflection pipeline (Phase 3.3) lives in SelfNarrativeActor, not as a separate actor.

**Documents updated**: `planning/architecture.md`, `notes/system-overview.md`, `planning/roadmap.md`
(Phase 3.3).

---

## Known deferred gaps (already documented elsewhere)

These are real but have homes in the roadmap — listed here for completeness.
Status updated April 2026 (Phase 4 complete).

- **Husserlian retention window empty**: `TemporalWindow.retention` is pruned but never populated.
  Phase 3.2 will populate it from the event log on each tick.
  **→ Fixed (Phase 3.2).** `_refresh_retention()` now queries the event log on each tick and fills
  the deque. Gap B from IDEAS.md is closed.

- **Workspace pressure ephemeral**: Accumulated salience pressure is lost on restart. Phase 4.2 will
  reconstruct from open volitional items.
  **→ Still deferred.** MotivationActor warm start uses residue count and time-since-conversation
  as a proxy. The workspace queue itself (`_queue: list[QueuedSignal]`) is still in-memory only.
  True pressure reconstruction from volitional items is not yet implemented.

- **Identity resonance stub**: `GlobalWorkspaceActor._identity_resonance()` returns 0.0. Phase 3
  connects this to the identity memory layer.
  **→ Still deferred.** Phase 3 built MemoryStore and identity retrieval, but GlobalWorkspaceActor
  was not given a MemoryStore dependency. Two options for Phase 5: (1) inject MemoryStore into
  GlobalWorkspaceActor, (2) surface identity bias via MotivationActor's salience signals instead.
  Decision deferred — documented in `planning/architecture.md` Open Decisions section.

- **In-memory context window**: `LanguageActor._context` is a simple deque. Phase 3 replaces this
  with memory-driven retrieval from the event log and reflective memory layers.
  **→ Fixed (Phase 3).** LanguageActor now retrieves relevant reflective memories per-message via
  pgvector similarity (or recency fallback) and injects them into context. The short-term `_context`
  deque still exists for within-conversation turns — that is correct and intentional.

## Code smells (status update April 2026)

- **Mutable dict in frozen dataclass** (`IgnitionBroadcast.content`): Still present. No actor
  mutates `content` today. Decision: document and trust actors. A comment was added to
  `GlobalWorkspaceActor._fire()` naming this precondition explicitly. If Phase 5 adds actors that
  consume IgnitionBroadcast and might mutate it, wrap in `types.MappingProxyType`.

- **Unbounded workspace queue** (`GlobalWorkspaceActor._queue`): Still present. Not a problem at
  current scale. The MotivationActor's active inference model provides external pressure regulation,
  which reduces the risk of unbounded growth in practice. Revisit if queue grows unexpectedly in
  long-running sessions.
