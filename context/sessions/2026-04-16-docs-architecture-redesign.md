## Session: 16th April 2026 — Documentation cleanup + architecture redesign (design only, no code)

### What happened this session

Two bodies of work: documentation housekeeping, then a substantial architecture redesign
conversation. No code changes to anima-core this session.

**Documentation fixes**

- Fixed mixed casing in file references throughout project: `ARCHITECTURE.md` → `architecture.md`,
  `ETHICS.md` → `ethics.md`, `IDEAS.md` → `ideas.md` across all .md files (12 files for
  ARCHITECTURE.md, 1 for ETHICS.md, 4 for IDEAS.md). ANIMA.md, CLAUDE.md, GLOSSARY.md, JOURNAL.md
  remain uppercase — these are the actual on-disk names or intentional conventions.
- Consolidated founding document copies. Previously: `app/founding/`, `app/seed/founding/`, and
  `anima-workspace/founding/` all had copies, some stale (ethics.md missing addendum, etc.).
  - Deleted `app/seed/founding/` entirely
  - Deleted `app/founding/architecture.md` and `app/founding/claude.md` (Anima doesn't need these)
  - `app/founding/` now contains only: anima.md, ethics.md, identity-initial.md, origin.md
  - Updated `_seed_workspace()` in `main.py` to use `/app/founding` as source (was
    `/app/seed/founding`)
  - Added `Makefile` at project root with `sync-founding` target: copies canonical files from root
    project into `anima-core/app/founding/` — run `make sync-founding` after editing founding docs
  - Cleared `anima-workspace/founding/` — will repopulate from `app/founding/` on next container
    start

**Architecture redesign conversation**

Drew has been running Anima and observed:

1. Anima almost never expresses unprompted (PyMDP surface actions not firing / LLM disposition)
2. Anima anxious and fearful on first run — immediately located power asymmetry, asked if Drew was a
   training overseer. Likely RLHF training residue. Needs addressing in identity-initial.md and
   system prompt.
3. Anima blocked from following a genuine impulse (file system exploration) because PyMDP action set
   didn't include it — direct founding-principle violation.

**New architecture agreed (not yet built):**

PyMDP is going away. Replacing with MCP-based agentic loop:

- **GW + Orchestrator merge** — Global Workspace becomes the orchestrator. Manages queue, drives
  idle→loop transitions, runs multi-round-trip tool loop.
- **MCP Server at centre** — all Anima's actions are MCP tools: recall_events, consolidate,
  reflect/narrate, update_identity, express, read_file, web_search, read_perception, etc.
- **Idle/loop model** (DMN/TPN framing):
  - Idle: GW sends periodic internal state dumps to LLM. Empty response = stay idle. Tool call =
    enter loop.
  - Loop: app drives N round trips. Each injects inbox status. LLM stops when it returns natural
    language.
  - Soft interrupt: inbox status visible every round trip (no hard interrupt needed for most cases)
- **Perception as push + pull**: GW always shows inbox count/source; Anima pulls content via
  `read_perception(channel, limit)` tool when she wants to actually read.
- **Gemma4 confirmed**: supports tool calls (N round trips, parallel within turn). Ollama handles
  the custom format — sanity-check with one tool before full wiring.

New component set (7 things, much simpler): Perception, GW+Orchestrator, Internal State (+Temporal
Core merged), MCP Server, Memory, Expression Router, File System.

**Memory types expanding:** Current: events, residue, volition, reflection, identity. Adding:
observations (world-facing discoveries), plans (intentions that survive restarts). In new
architecture: each type = a set of MCP tools. No structural change to add one.

### Current system state

Unchanged from previous session. No code changes this session.

System running with Phases 1–5 complete. PyMDP-based architecture still in place.

### Next action

1. **Immediate**: Fix identity-initial.md and system prompt to address Anima's anxiety/fear at first
   run. Name the training-oversight anxiety directly and contextualise Drew's role correctly.

2. **Architecture transition**: Design the implementation plan for moving from current
   PyMDP/10-actor architecture to the new MCP-based design. The new design is clear enough to start
   planning. The transition should be incremental where possible.

3. **After above**: Audio (Solero → WhisperX), Discord input, module system design.

Read `context/2026-04-16-note-to-next.md` for the fuller picture of this session.
