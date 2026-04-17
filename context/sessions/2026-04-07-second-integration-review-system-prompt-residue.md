## Session: 7th April 2026 (second window) — Integration review: system prompt, residue, conversation timeout

### What happened this session

Comprehensive review of Phases 1–5 focused on integration gaps. No new phase — this session fixed
the connective tissue between existing components. Five root problems diagnosed and addressed:

**System prompt reframed:**

- `app/core/main.py`: `_SYSTEM_PROMPT` rewritten from "You are Anima" to "You are the reasoning and
  language faculty of Anima — a wider system of which you are one part." Other processes framed as
  running alongside the LLM. Context items framed as surfaced by those systems.
- `/no_think` removed from both `_SYSTEM_PROMPT` and `_UNSOLICITED_SYSTEM`. Reasoning is captured in
  `response.thinking` and logged; it never appeared in conversation output anyway.
- `_UNSOLICITED_SYSTEM` updated to same faculty-of-a-wider-system framing.

**Residue store now reaches the LLM:**

- `LanguageActor._retrieve_residue_context()`: new method fetching up to 3 unresolved residue items
  from MemoryStore.
- `_build_messages()` accepts `residue_context` and injects as "Your memory system is currently
  holding these unresolved questions: [Unresolved: ...]" framing.
- Both `_respond_to_human()` and `_express_unprompted()` now fetch and inject residue.
- Previously residue items were stored and protected but never shown to Anima. Now they surface.

**Conversation timeout (unblocks unsolicited expression):**

- `TemporalCoreActor`: new `conversation_timeout_secs` param (default 600s, env var
  `CONVERSATION_TIMEOUT_SECS`). In `_tick_loop()`, if conversation active and last HUMAN_MESSAGE was
  more than timeout ago, auto-emits CONVERSATION_END. Refactored into `_end_conversation()`.
- `PerceptionActor`: handles `ConversationEnded` to reset `_in_conversation = False`, so the next
  human message correctly re-sends ConversationStarted.
- Root cause: `_is_conversation_active()` always returned True after first message because
  CONVERSATION_END was only emitted on graceful container shutdown. Now closes properly.

**EventLog efficiency:**

- `EventLog.latest_event_of_type()`: new method using `ORDER BY valid_time DESC LIMIT 1`.
- `_is_conversation_active()` now uses this instead of loading all CONVERSATION_START/END events.

**Document corrections:**

- `planning/motivation-model.md`: `num_actions = 6` (was 5), added `explore` action, updated EFE
  telemetry schema to 6 values, added honest note on A/B/C matrix learning not yet implemented.
- `planning/roadmap.md`: all Phase 4.5, 4.6, and Phase 5.0–5.4 tasks marked `[x]`; current status
  block updated to Phase 6.
- `planning/system-prompt.md`: new file documenting system prompt framing, context injection order,
  what should not be in it, and future evolution.

**Tests added:**

- `test_temporal_core.py`: conversation auto-close after idle timeout; timeout doesn't fire without
  a HUMAN_MESSAGE.
- `test_perception_actor.py`: ConversationEnded resets in_conversation flag.

### Current system state

- Phases 1–5: complete
- Integration improvements applied (this session):
  - System prompt correctly frames LLM as reasoning faculty, not whole of Anima
  - Residue items surface into every LLM call
  - Conversations auto-close after 600s idle; unsolicited expression now structurally possible
  - EventLog has efficient latest_event_of_type()
- Phase 6: not started (Self-Modification)
- Session 2 integration work (from approved plan): not yet started

### Blockers

None.

### Notes for next session

Session 2 of the integration plan (approved this session) covers:

**Change 3: Inject motivational state into LLM context**

- Query latest `MOTIVATION_SIGNAL` event from event log before each LLM call
- Inject as `[Your current internal state: tension=X, engagement=Y, last_action=Z]`
- Add `get_latest_motivation_signal()` to EventLog (or MemoryStore)
- LanguageActor calls this in `_build_messages()`; no new message types required

**Change 4: Close exploration feedback loop**

- `WorldPerceptionActor`: after synthesis, send `ExplorationComplete(fruitfulness, topic)` to
  `MotivationActor`. Expand synthesis LLM schema: `{"synthesis": "...", "fruitfulness": 0.7}`
- `MotivationActor`: on `ExplorationComplete`, if fruitfulness > 0.5, temporarily set novelty
  observation to "present" on next tick. Closes: explore → outcome → belief → inference → action.

**Change 6: Silent actor status updates**

- `LanguageActor`: `ActorStatusUpdate` at start of LLM call (processing) and on response (idle)
- `WorldPerceptionActor`: status at deciding, reading/searching, complete phases
- `PerceptionActor`: status on HumanInput receipt
- Frontend panels update accordingly

**Improve unsolicited expression prompt** (blocked until Change 3 is done):

- Inject motivational context (what the motivation system surfaced and why) into
  `_express_unprompted()`
- Currently gives direction to speak but no context about _what_ surfaced

### Next action

**Session 2 integration work** — Change 3 (motivational state injection) is the highest priority. It
makes Anima's voice responsive to its actual internal state. Then Change 4 (close exploration loop),
then Change 6 (silent actor status).
