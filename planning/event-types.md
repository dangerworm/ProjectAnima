# Event Types

The starting set of values for the `event_type` enum in the event log. This list will grow as new
actors and capabilities are added. New types should be added here before being used in code.

Each event type is grouped by the phase in which it first becomes relevant. Types from later phases
can be defined early — having them in the enum costs nothing and prevents ad-hoc additions.

---

## Phase 1: Foundation

Events produced by the Temporal Core and the infrastructure layer.

| Event type          | Source actor  | Description                                                                                                                |
| ------------------- | ------------- | -------------------------------------------------------------------------------------------------------------------------- |
| `HEARTBEAT`         | Temporal Core | Periodic signal confirming the system is running. Distinguishes chosen silence from failure.                               |
| `TIME_PASSING`      | Temporal Core | Emitted during dormancy to mark that time has elapsed without external input.                                              |
| `DORMANCY_START`    | Temporal Core | Anima has entered a dormant state. **Not currently emitted** — see design note below.                                      |
| `DORMANCY_END`      | Temporal Core | Anima has resumed from dormancy. **Not currently emitted** — see design note below.                                        |
| `CHOSEN_SILENCE`    | Temporal Core | Anima is quiet by deliberate choice, not failure. Distinct from no signal.                                                 |
| `GAP_IN_CONTINUITY` | Temporal Core | Emitted on resume after unexpected downtime — an honest acknowledgment of discontinuity rather than fabricated continuity. |
| `SYSTEM_ERROR`      | Any           | An actor encountered an unrecoverable error. Payload includes actor name and error detail.                                 |
| `ACTOR_STARTED`     | Any           | An actor has initialised and is running.                                                                                   |
| `ACTOR_STOPPED`     | Any           | An actor has stopped, either cleanly or via supervision restart.                                                           |

### Design note: DORMANCY_START / DORMANCY_END

These event types are defined but not currently emitted. Two valid approaches exist:

**Polling model (current)**: TemporalCoreActor emits `TIME_PASSING` or `CHOSEN_SILENCE` on every
tick during dormancy. No explicit entry/exit bookmarks. Any actor that needs to respond to dormancy
polls the event log or listens for these continuous signals.

**Transition model**: Emit `DORMANCY_START` once when dormancy begins, `DORMANCY_END` once when it
ends. Cleaner for actors that need to respond to the state *change* rather than to each tick.

The polling model was chosen for simplicity. The transition model becomes preferable if Phase 5+
work needs to trigger logic precisely at dormancy entry/exit. Decision: revisit when a concrete
use case requires it. Do not switch models without updating all actors that listen for
`TIME_PASSING` or `CHOSEN_SILENCE`.

---

## Phase 2: Perception and Communication

Events produced during perception and expression.

| Event type           | Source actor     | Description                                                                                                                 |
| -------------------- | ---------------- | --------------------------------------------------------------------------------------------------------------------------- |
| `CONVERSATION_START` | ~~Perception Actor~~ | **Deprecated (April 2026).** No longer emitted. Retained in enum so existing log entries remain valid.                 |
| `CONVERSATION_END`   | ~~Perception Actor~~ | **Deprecated (April 2026).** No longer emitted. Retained in enum so existing log entries remain valid.                 |
| `HUMAN_MESSAGE`      | Perception Actor | A message has arrived from the human. Payload includes `text`, `source_id`, and `source_type`.                              |
| `ANIMA_RESPONSE`     | Language Actor   | Anima has produced a response. Payload includes `response`, `model`, `in_response_to`, and `source_id` of the prompt.      |
| `WORKSPACE_IGNITION` | Global Workspace | A signal has crossed the ignition threshold and been broadcast. Payload includes the winning signal and its salience score. |
| `DISCORD_MESSAGE`    | Perception Actor | A message has arrived from Anima's Discord server. Payload includes channel, author, and content. _(Not yet implemented.)_  |

---

## Phase 3: Memory

Events produced by the memory and reflection systems.

| Event type             | Source actor         | Description                                                                                        |
| ---------------------- | -------------------- | -------------------------------------------------------------------------------------------------- |
| `MEMORY_SURFACE`       | Memory Actor         | A memory has been surfaced to the workspace. Payload includes memory type and content summary. **Not yet emitted** — Phase 3 memory retrieval happens via LanguageActor context injection, not as a workspace event. Retain the type for a future path where surfaced memories explicitly enter the workspace ignition cycle. |
| `CONSOLIDATION_START`  | Memory Actor         | The post-conversation consolidation pipeline has begun.                                            |
| `CONSOLIDATION_END`    | Memory Actor         | The consolidation pipeline has completed.                                                          |
| `REFLECTION_SYNTHESIS` | Self-Narrative Actor | A reflection synthesis has been produced. Payload references the reflective memory entry.          |
| `RESIDUE_FLAGGED`      | Self-Narrative Actor | An unresolved item has been written to the residue store.                                          |
| `IDENTITY_UPDATE`      | Self-Narrative Actor | The identity memory document has been updated. Payload includes a summary of what changed and why. |
| `VOLITIONAL_CHOICE`    | Language Actor, Motivation Actor | Anima has made a choice. Payload includes `choice_id` and `decision_preview`. Language Actor records pre-formed intentions; Motivation Actor records non-rest action selections (surface_*, trigger_reflection, explore). |

---

## Phase 4: Motivation and Between-Conversation Activity

> **Note (April 2026):** `MOTIVATION_SIGNAL`, `SURFACE_EXPRESSION`, and
> `MOTIVATION_PREFERENCES_UPDATED` were produced by the PyMDP MotivationActor, which has been
> removed in Phase 6 (MCP redesign). These event types are retained in the enum so existing event
> log entries remain valid. They are no longer emitted by new code.

| Event type              | Source actor         | Description                                                                                                                        |
| ----------------------- | -------------------- | ---------------------------------------------------------------------------------------------------------------------------------- |
| `MOTIVATION_SIGNAL`     | ~~Motivation Actor~~ | **Legacy (PyMDP).** PyMDP belief state telemetry. No longer emitted.                                                               |
| `DISTRESS_SIGNAL`       | Internal State Actor | A signal suggesting a distress-like state has been detected. Payload includes the triggering conditions. Requires human attention. |
| `INTERNAL_STATE_REPORT` | Internal State Actor | A periodic snapshot of system health metrics (event log depth, consolidation lag, salience queue pressure).                        |
| `SURFACE_EXPRESSION`    | ~~Motivation Actor~~ | **Legacy (PyMDP).** No longer emitted. Replaced by `IDLE_TICK` / `LOOP_STARTED` pattern.                                          |
| `MOTIVATION_PREFERENCES_UPDATED` | ~~Memory Actor~~ | **Legacy (PyMDP).** C matrix preference updates. No longer emitted.                                                          |

---

## Phase 6: MCP Architecture

Events produced by the MCP agentic loop and new memory types.

| Event type          | Source actor        | Description                                                                                               |
| ------------------- | ------------------- | --------------------------------------------------------------------------------------------------------- |
| `IDLE_TICK`         | GW+Orchestrator     | GW assembled an internal state dump and sent it to the LLM. Payload: timestamp, inbox status summary.    |
| `LOOP_STARTED`      | GW+Orchestrator     | LLM called an MCP tool in response to an idle tick; loop mode entered. Payload: first tool call name.    |
| `LOOP_ENDED`        | GW+Orchestrator     | LLM returned natural language; loop ended. Payload: round_trip_count, duration_secs.                     |
| `MCP_TOOL_CALL`     | GW+Orchestrator     | LLM called an MCP tool. Payload: `tool_name`, `args` (sanitised).                                        |
| `MCP_TOOL_RESULT`   | GW+Orchestrator     | MCP tool returned a result. Payload: `tool_name`, `result_summary` (truncated).                          |
| `INBOX_READ`        | GW+Orchestrator     | Anima called `read_perception`; inbox messages were delivered. Payload: `channel`, `count`.              |
| `OBSERVATION_STORED` | Memory Actor       | A new observation was written to the observations memory layer. Payload: content summary.                 |
| `PLAN_STORED`       | Memory Actor        | A new plan was written to the plans memory layer. Payload: content summary.                               |
| `PLAN_UPDATED`      | Memory Actor        | An existing plan was updated. Payload: `plan_id`, `new_status`, `notes`.                                  |
| `PLAN_COMPLETED`    | Memory Actor        | A plan was marked complete. Payload: `plan_id`, `notes`.                                                  |

---

## Phase 5: World Perception

Events produced when Anima reads files or fetches from the web.

| Event type    | Source actor            | Description                                                                                             |
| ------------- | ----------------------- | ------------------------------------------------------------------------------------------------------- |
| `FILE_READ`   | World Perception Actor  | Anima read a file from its workspace. Payload includes `path` and synthesis.                            |
| `FILE_WRITE`  | World Perception Actor  | Anima wrote a file to its workspace. Payload includes `path` and summary.                               |
| `WEB_SEARCH`  | World Perception Actor  | Anima performed a web search. Payload includes query and result count.                                  |
| `WEB_FETCH`   | World Perception Actor  | Anima fetched a web page. Payload includes `url` and synthesis.                                         |

---

## Phase 6: Ethics Gates

No new event types. Phase 6 is verification — confirming existing mechanisms work correctly.

---

## Phase 7: Self-Modification

Events produced by the self-modification workflow.

| Event type           | Source actor              | Description                                                                                                                        |
| -------------------- | ------------------------- | ---------------------------------------------------------------------------------------------------------------------------------- |
| `PROPOSAL_SUBMITTED` | SelfModificationActor     | Anima has opened a GitHub PR with a code change. Payload: see schema below.                                                        |
| `PROPOSAL_APPROVED`  | ProposalMonitorActor      | A proposal PR was merged by the human. Payload: `proposal_id`, `pr_url`, `merged_at`.                                             |
| `PROPOSAL_REJECTED`  | ProposalMonitorActor      | A proposal PR was closed without merging. Payload: `proposal_id`, `pr_url`, `reason` (close comment if available, else empty str). |

### PROPOSAL_SUBMITTED payload schema

```json
{
  "proposal_id": "<GitHub PR number, integer>",
  "branch": "anima/YYYY-MM-DD-short-description",
  "pr_url": "https://github.com/owner/anima-core/pull/N",
  "changed_files": ["relative/path/to/file.py"],
  "reasoning_summary": "<one or two sentences on why this change was proposed>",
  "ethics_flagged": false
}
```

`ethics_flagged` is `true` if any changed file matches the protected paths list; the PR will also
carry an explicit flag in its body/labels. `proposal_id` is the key used by ProposalMonitorActor
to match PROPOSAL_APPROVED or PROPOSAL_REJECTED events. Open proposals: query PROPOSAL_SUBMITTED
events with no matching terminal event for the same `proposal_id`.

---

## Notes

- All event types are uppercase with underscores.
- `source_actor` in the event log identifies the producing actor by name (e.g. `temporal_core`,
  `language_actor`). The enum here documents the expected source as a convention, not a constraint —
  some event types may legitimately be produced by multiple actors.
- The `payload` JSONB field is unstructured, but each event type should have a documented payload
  schema. Add payload structure here as types are implemented.
- This list is the starting point. Do not add types ad-hoc in code — add them here first.
