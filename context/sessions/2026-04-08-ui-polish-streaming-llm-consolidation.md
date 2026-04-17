## Session: 8th April 2026 — UI polish, streaming, LLM call consolidation

### What happened this session

This session was entirely UI and backend polish after the PyMDP→LLM deliberation replacement. No new
architectural features added; focus was on observability, correctness, and reducing LLM round-trips.

**Backend changes**

- `core/llm/__init__.py`: Added `complete_streaming()` using Ollama's `stream: True` mode. Detects
  `<think>`/`</think>` tag transitions to distinguish thinking vs generating phases, fires
  `on_phase("thinking"|"generating")` callback. Falls back to non-streaming on error.
- `core/main.py`: Updated `_SYSTEM_PROMPT` with "Your actual capabilities" section explaining
  `read_code` and `query_self` deliberation actions and that they happen autonomously between
  conversations, not inline during responses. Anima was telling Drew she couldn't access her
  databases — this was incorrect.
- `core/main.py` `_payload_snippet`: Fixed MOTIVATION_SIGNAL format (was showing old PyMDP
  `action=? rests=0`; now shows `deliberation tick · residue=N`). Added DELIBERATION snippet
  (`action — topic`), VOLITIONAL_CHOICE snippet (`decision_preview`), RETROSPECTION/IMAGINATION
  snippet (topic or query_type).
- `actors/language/__init__.py`: Added `defer` to `DELIBERATE_ACTIONS`. Expanded
  `_DELIBERATE_SCHEMA` so `imagine` and `query_self` no longer require a second LLM call — imagine
  writes content directly in the deliberation JSON; query_self provides structured query parameters.
  All action methods now take `parsed: dict`. Guard changed from `if not action_type or not topic`
  to `if not action_type` (was blocking valid no-topic actions like `reflect`, `express`, `defer`).
  `_respond_to_human` uses `complete_streaming()` with phase callback.
- `actors/motivation/__init__.py`: Status update now includes full residue content (was truncating
  at 80 chars).

**Frontend changes**

- `store/actorState.ts`: `languageStatus` type extended to include `'thinking' | 'generating'`.
  Handler added for `language_phase` status update type.
- `components/conversation/ConversationPane.tsx`: `ThinkingIndicator` takes `{ phase }` prop, shows
  "thinking" (slower pulse, purple `#a78bfa`) vs "generating" (faster, `#c4b5fd`). Shown for
  `reasoning | thinking | generating` states.
- `components/inner-life/InnerLifePane.tsx`:
  - `CHIP_MIN_DURATION_MS = 10_000` (undercurrent chips persist 10s minimum)
  - Infinite render loop fixed: stable `undercurrentKeys` string dependency instead of array
    reference; `if (toAdd.length === 0) return prev` guard; primitive `currentLabel`/ `currentColor`
    deps for quiet timer effect.
  - Quiet status delay: 60s timer before "quiet" label appears (cancels immediately on any active
    state).
  - UndercurrentChip: removed text truncation.
- `components/sidebar/Sidebar.tsx`:
  - Memory content viewer: fixed right drawer (width 360, `zIndex: 1300`), fetches on open, renders
    full text. `DiscoveryEntry` interface corrected (`source`/`synthesis` not `title`/`summary`).
    Identity `content` fixed from `{ raw_text?: string }` to `string`.
  - `MotivationSection` now fetches and displays residue items inline (full text, no count).
  - All truncation removed throughout.

### Current system state

System running. Deliberation loop working with `rest`, `reflect`, `retrospect`, `imagine`,
`explore`, `express`, `respond`, `read_code`, `query_self`, `defer` actions.

LLM streaming active for human responses — thinking/generating phases visible in UI.

Memory content viewer functional for all five memory types.

No pending migrations.

### Next action

Observe Anima running with correct self-knowledge. The system prompt fix means she will now give
accurate answers if asked about her capabilities. Watch whether she begins using `read_code` and
`query_self` deliberation actions autonomously.

After observation: Phase 6 (Ethics Gates) or continue with character/behaviour work.
