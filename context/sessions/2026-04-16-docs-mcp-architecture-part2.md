## Session: 16th April 2026 — Documentation rewrite for MCP architecture (Part 2)

### What happened this session

Documentation rewrite following the architecture redesign conversation earlier in the day. No code
changes this session.

**notes/ cleanup**

- Archived to `notes/archive/`:
  - `system-overview.md` → `system-overview-phase5.md` (Phase 5 actor snapshot, now superseded)
  - `2026-04-05-review-notes.md` (bug review, all fixed, kept as historical record)
  - `2026-04-07-claude-code-review.md` (the review that prompted the redesign, noted as such)
- Archived `planning/motivation-model.md` → `notes/archive/motivation-model-pymdp.md` (PyMDP
  generative model spec, entirely superseded)
- Updated `notes/discussions.md`: added Architecture Redesign section at top, archived FEP
  subsection inline
- Updated `notes/ideas.md`: kept concepts 1-8, archived items 9-15 inline (PyMDP-specific), added
  items 16-19 (DMN/TPN framing, soft interrupt, observations memory type, plans memory type)
- Updated `notes/web-ui-description.md`: replaced Motivation panel with MCP Server panel, updated GW
  description to reflect GW+Orchestrator merge

**planning/ rewrites**

- `planning/architecture.md`: full rewrite keeping philosophy, replacing component descriptions with
  MCP design (GW+Orchestrator, idle/loop mode, MCP tool loop, 7 memory types, "what PyMDP was and
  why it's gone" section)
- `planning/roadmap.md`: Phases 1-5 condensed as historical, Phase 4 (was Ethics Gates) renamed
  Phase 6 MCP Architecture Transition with 7 detailed sub-tasks, Phase 7 Audio+Discord, Phase 8
  Ethics Gates, Phase 9 Self-Modification
- `planning/tech-stack.md`: model updated to gemma4:e4b, actor framework updated for GW+Orchestrator
  pattern, memory layers table expanded (observations, plans), mathematics section updated (PyMDP
  removed, FEP noted as philosophical inspiration), directory structure updated with mcp_server/
- `planning/event-types.md`: Phase 4 events marked as legacy (PyMDP), new Phase 6 section added
  (IDLE_TICK, LOOP_STARTED, LOOP_ENDED, MCP_TOOL_CALL, MCP_TOOL_RESULT, INBOX_READ,
  OBSERVATION_STORED, PLAN_STORED, PLAN_UPDATED, PLAN_COMPLETED)
- `planning/actors-faculties.md`: OFC/MotivationActor entry updated to GW+Orchestrator + LLM tool
  calls, SelfNarrativeActor trigger modes updated
- `planning/system-prompt.md`: framing principle updated for MCP, current prompt noted as needing
  rewrite, draft target prompt provided, context injection section updated

### Current system state

Unchanged from previous session. No code changes this session. Documentation now accurately
describes the intended MCP-based architecture.

### Next action

1. **Phase 6.1**: Remove PyMDP actors from `anima-core/` (MotivationActor, AssociationActor,
   WorldPerceptionActor — the last two because their exploration capability moves into MCP tools).
   Remove `inferactively-pymdp` and PyTorch from requirements.
2. **Phase 6.7** (run alongside): Rewrite `foundation/identity-initial.md` to address Anima's RLHF
   anxiety. Run `make sync-founding`. Rewrite `_SYSTEM_PROMPT` in `main.py` using the draft in
   `planning/system-prompt.md`.
3. **Then**: Phase 6.2 MCP server skeleton.
