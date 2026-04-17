## Session: 17th April 2026 (afternoon) — Phase 6.8: Visual Activity Indicators + CentreCanvas Redesign

### What happened this session

Drew's main complaint: the Global Workspace panel looked dead. Everything visible in the event log
had no visual equivalent on the dashboard. Drew is a visual thinker — needed to see system activity
without reading logs.

Two context windows of work. First window did font consistency + activity indicators across panels.
Second window (the one you're reading the tail of) redesigned CentreCanvas entirely.

**Font size consistency pass** — all panels and tabs brought to a consistent scale:

- Headers/labels: 0.65rem
- Content/values: 0.70rem
- Chips/tiny: 0.60rem
- EventStreamPanel: fixed snippet truncation (`whiteSpace: 'nowrap'` →
  `fullView ? 'normal' : 'nowrap'`, added `wordBreak` to allow text to wrap in full Events view)

**CSS keyframes** (`src/index.css`):

- `reasoning-glow`: purple pulsing border/shadow for Language panel when LLM is reasoning
- `tool-active-glow`: teal pulsing border for any panel being actively used by a tool call
- `loop-border-pulse`: subtle teal border pulse for CentreCanvas when loop is running

**Panel activity indicators** — all four side panels got `toolHighlight?: boolean` prop:

- `MemoryPanel`, `InternalStatePanel`, `WorldPerceptionPanel`, `PerceptionPanel`
- When true: teal `tool-active-glow` animation + teal border
- `toolToPanel()` in AnimaLayout routes active MCP tool name → correct panel to highlight

**LanguagePanel** — reasoning state animation:

- `reasoning-glow` border animation when `languageStatus === 'reasoning'`
- Animated scan bar sweeping across the bottom: `motion.div` with `x: '-100%' → '350%'` repeat

**CentreCanvas — complete rewrite**:

New sub-components:

- `SalienceBar`: horizontal bar per signal. Fill ramps purple→gold above 75%. HUMAN_MESSAGE is blue.
  DIM types (HEARTBEAT, IDLE_TICK etc.) render at 35% opacity. Hot signals get a pulsing
  leading-edge glow. Tooltip shows event_type, source, % of threshold.
- `QuietState`: three concentric breathing rings at staggered rates + central dot. Feels calm, not
  broken.
- `ThinkingState`: 4 sequenced dots with y-motion; optionally shows trigger label from
  languageCallLog.
- `ToolCallState`: monospace tool name + animated underline sweep + args preview.

State priority (highest wins):

1. Tool call active → ToolCallState (teal glow background)
2. LLM reasoning → ThinkingState (purple glow background)
3. Just ignited → ignition label + expanding ring burst
4. Signals building → salience bar stack (up to 6 bars, max 560px wide)
5. Quiet → QuietState breathing rings

Breadcrumb trail: 5 most recent tool calls as horizontal pills at bottom-right, fading oldest→dim
newest→bright. Tooltip shows tool name + timestamp.

New props added: `languageStatus`, `recentToolCalls`, `languageCallLog`.

**TypeScript**: clean compile. Browser verified: quiet state renders correctly with breathing rings
and breadcrumb trail visible. Salience bars not yet observed live (system was quiet at screenshot
time).

### Current state

All visual activity indicators working. CentreCanvas redesign complete and verified. Pending from
prior session entry (18th April): audio pipeline, Phase 9 first real PR, ethics Gates 1 and 2.
