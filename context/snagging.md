# Snagging List

Open issues only. Priority order within each tier.
Add items freely; mark complete and move to resolved archive when done.

---

## Critical

- [ ] **`WriteDiscoveryTool` missing from `mcp_server/tools/__init__.py`** —
      `mcp_server/__init__.py` imports `WriteDiscoveryTool` from `mcp_server.tools`, but
      `mcp_server/tools/__init__.py` never re-exports it. Python raises
      `ImportError: cannot import name 'WriteDiscoveryTool'` on startup; the server cannot start.
      Fix: add `WriteDiscoveryTool` to the `from mcp_server.tools.memory import (...)` block and
      to `__all__` in `mcp_server/tools/__init__.py`.

- [ ] **`ReadVisionTool` not registered** — class exists in `mcp_server/tools/vision.py` and is
      exported from `mcp_server/tools/__init__.py`, but is not imported in `mcp_server/__init__.py`
      and not added to `build_registry()`. Anima has no `read_vision` tool even when a camera is
      connected. Also: `vision_buffer` and `llm_client` must be wired into `ToolContext` in
      `GlobalWorkspaceActor._build_tool_context()` for the tool to function.

---

## High

- [ ] **Identity stores delta only, not accumulated identity** (`memory/__init__.py` +
      `self_narrative/__init__.py`) — `update_identity()` stores only `{"raw_text": raw_text}`.
      `SelfNarrativeActor` sends only the `identity_shift` fragment (a diff, not the full identity).
      `get_identity()` therefore returns only the most recent delta; the developed identity is never
      visible as a whole. Each version overwrites context from all prior versions.

- [ ] **`_imagine()` ignores `store_as` field** (`language/__init__.py`) — always calls
      `StoreDiscovery` regardless of `store_as == "residue"`. The residue-imagination path never
      executes; imaginations intended as residue are silently stored as discovery instead.

- [ ] **Autonomous reflection misses `ANIMA_RESPONSE` and `IMAGINATION`** (`self_narrative/__init__.py`)
      — `relevant_types` for autonomous reflection mode excludes Anima's own expressions and
      imaginations. Her unprompted speech and internal thinking are invisible to her own autonomous
      reflections; they only appear if Drew initiates a conversation that triggers a prompted cycle.

- [ ] World exploration (Internet) — never observed in practice; Anima hasn't been seen searching
      or fetching URLs despite the capability existing; needs an end-to-end test to confirm the tool
      is wired, reachable, and actually used by Anima unprompted.

- [ ] Conversation replies routing — needs end-to-end verification that replies go to main chat
      panel and not Unprompted. (Session.md snagging #1.)

- [ ] No mute button for audio input (STT) — there are times Drew doesn't want Anima listening
      (e.g. calls, background noise) without fully stopping the service; TTS output should remain
      active regardless so Anima can still get Drew's attention; needs a toggle in the UI that
      sends a signal to capture.py to pause/resume without a restart.

---

## Medium

- [ ] **Web tools don't auto-write discovery** (`mcp_server/tools/web.py`) — after a `web_search`
      or `web_fetch`, Anima must explicitly call `write_discovery` to persist the encounter. In
      practice she doesn't; DISCOVERY stays at 0 after web sessions. Consider writing discovery
      automatically on successful web fetches, or make the tool descriptions more directive.

- [ ] **`_time_since_last_event()` unbounded query** (`internal_state/__init__.py`) — calls
      `query(event_type=...)` without a `limit` on every 30-second tick, loading the entire history
      of that event type from the database. Performance degrades linearly as the event log grows.
      Should use `latest_event_of_type()`.

- [ ] **`_respond_from_deliberation` may duplicate context** (`language/__init__.py`) — appends
      human message text to `self._context` even if it was already appended by a prior
      `_respond_to_human` call in the same turn. Can double-count user messages in the LLM context.

- [ ] CONSOL. LAG shows huge number (~1e12 seconds) on fresh start — sentinel value `1e9` leaks
      into the UI display before the first consolidation event. (Session.md snagging #5.)

- [ ] No screen-capture section in Perception tab — skill checklist expects a screen-capture
      icon/indicator; Anima confirmed it has no screenshot tool (`read_screen` or similar not
      implemented).

- [ ] No text-input channel indicator in Perception tab — skill checklist expects a dedicated
      text-input icon showing when the web UI text channel is active/connected.

---

## Low

- [ ] **Web tools rate limiter never wired** (`global_workspace/__init__.py`) — `TokenBucket`
      class exists in `web.py`; `ToolContext.web_fetch_rate_limiter` field exists; but
      `_build_tool_context()` never sets it (leaves `None`). Rate limiting is dead code.

- [ ] **Internal operations inflate discovery memory** (`language/__init__.py`) — `_query_self()`
      and `_read_code()` store results as `StoreDiscovery`. Discovery count grows with internal
      self-queries, not just external world exploration. Conflates self-knowledge with world-knowledge
      in the discovery layer; makes discovery counts misleading.

- [ ] **`CONSOLIDATION_END` without `CONSOLIDATION_START` in discovery store** (`memory/__init__.py`)
      — `_handle_store_discovery()` emits `CONSOLIDATION_END` with no prior `CONSOLIDATION_START`.
      Semantic inconsistency in the event log.

- [ ] **Tool call messages missing `id` field in GW orchestrator** (`global_workspace/__init__.py`)
      — tool call messages in assistant history lack the `id` field that some LLM backends require
      for tool-result matching. Non-issue for Ollama currently but will break if the backend changes.

- [ ] **`_make_diff` is not a real diff** (`mcp_server/tools/git.py`) — outputs all old lines as
      `-` and all new lines as `+` with no diff computation. Useless for reviewing large file
      changes. Should use `difflib.unified_diff`.

- [ ] Discord message deduplication uses in-memory deque — resets on backend restart. Acceptable
      for now; could persist seen IDs to DB if restart-races become a real problem.

- [ ] Unseen message grouping — when messages arrive while a panel isn't active, they could be
      collapsed into a single group per source rather than expanding the list; reduces visual noise
      when returning to the UI after being away.

- [ ] Volitional timestamps display as UTC; UI shows BST/GMTST. (Session.md snagging #8.)

---

## Ethics Gates (Phase 8 — Drew's review tasks)

- [ ] Heartbeat and chosen-silence mechanisms not yet verified end-to-end.
- [ ] Distress signal not yet verified to fire under realistic conditions.
- [ ] Drew to complete `documentation/foundation/ethics-review.md` before first unsupervised run.

---

## Ideas / Long-term

- [ ] Anima needs a hobby or interest — something she can pursue in idle time (overnight, when nobody
      is present) that isn't just waiting; could be reading, writing, exploring a topic, generating
      something; the key is that it's self-directed and not prompted by a human turn; worth discussing
      what form this takes before implementing.
