## Session: 17th April 2026 (morning) — Phase 6.8: Web UI Revamp

### What happened this session

Drew asked for a UI revamp before going to sleep (continuation of the overnight session). Two
context windows of work. This session completed the state management updates that were in progress
when the previous context window ran out, then built the full navigation system.

**actorState.ts — completed**

- `initialState()` now includes `orchestratorMode: 'idle'`, `currentToolCall: null`,
  `recentToolCalls: []`
- `reducer()` event_log_entry handler now also dispatches on event_type:
  - `LOOP_STARTED` → `orchestratorMode = 'loop'`
  - `LOOP_ENDED` → `orchestratorMode = 'idle'`, `currentToolCall = null`
  - `MCP_TOOL_CALL` → parse snippet (`tool(args)` format), create `McpToolCall`, push to
    `recentToolCalls`
  - `MCP_TOOL_RESULT` → `currentToolCall = null`

**NavBar** (`web-ui/src/components/layout/NavBar.tsx`)

New slim navigation bar (34px) with:

- Brand: `✦ ANIMA`
- Five view tabs: Live / Events / Memory / Narrative / Chat — with active highlight and hover states
- Right-side status indicators (AnimatePresence with fade transitions):
  - Teal pulsing dot + tool name when orchestrator is calling an MCP tool
  - Purple pulsing dot + "reasoning…" when LLM is processing
  - Teal "loop" chip when orchestrator is in loop mode (no specific tool active)
- Connection status dot (green=connected, amber=connecting, red=disconnected) with glow on connected

**AnimaLayout** (`web-ui/src/components/layout/AnimaLayout.tsx`)

Full restructure:

- NavBar added at top
- Main content area uses AnimatePresence with fade transitions between views
- `msgAnimKey` tracks HUMAN_MESSAGE arrivals from perception; triggers animated dot
- Animated flow dot: framer-motion div animates from 88% → 20% width position over 900ms (blue glow)
  when `perception.lastEventType === 'HUMAN_MESSAGE'` and `lastUpdate` changes
- Bottom bar: MessageInput always pinned at bottom in all views
- View routing:
  - `live`: current full-panel layout (all actor panels, event stream, bottom row)
  - `events`: EventStreamPanel full-height with `fullView` prop
  - `memory`: MemoryPanel full-height
  - `narrative`: SelfNarrativePanel (2/3) + UnsolicitedExpressionsPanel (1/3)
  - `conversation`: ExpressionPanel full-height

**CentreCanvas** (`web-ui/src/components/panels/CentreCanvas.tsx`)

New props: `orchestratorMode`, `currentToolCall`. New display states (in priority order):

1. Ignition burst (existing) when `lastEventType === 'WORKSPACE_IGNITION'`
2. Tool call display (teal) when `currentToolCall` non-null — shows tool name + args
3. Loop idle state when `orchestratorMode === 'loop'` — "orchestrating…"
4. Signals building (existing) when `pressure > 0.05`
5. Quiet (existing)

Ambient glow also teal during tool calls; lighter teal during loop mode.

**EventStreamPanel** (`web-ui/src/components/panels/EventStreamPanel.tsx`)

New `fullView` prop: never collapses, seeds 200 events (vs 60), larger row typography, no collapse
arrow in header.

### Current system state

Phase 6 complete. Architecture is:

- GW+Orchestrator: idle loop calls LLM with 18 MCP tools
- PerceptionActor: inbox queue per channel, pull model via `read_perception`
- 7 memory layers: reflective, residue, identity, volitional, discovery, observations, plans
- 5-view navigation UI with live tool/loop status indicators

**Before first live run:**

1. `docker compose run --rm anima alembic upgrade head` (migration 0005)
2. `pytest tests/` in container
3. Observe first orchestrated conversation

### Blockers

- Migration 0005 must run before observations/plans features work
- Tests not yet run in container (bypassPermissions overnight build)

### Next action

1. Run migration + tests
2. Run the system live and observe the orchestrator calling tools
3. Consider deferred UI items (see roadmap Phase 6.8)
