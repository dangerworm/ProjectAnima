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
| `DORMANCY_START`    | Temporal Core | Anima has entered a dormant state.                                                                                         |
| `DORMANCY_END`      | Temporal Core | Anima has resumed from dormancy.                                                                                           |
| `CHOSEN_SILENCE`    | Temporal Core | Anima is quiet by deliberate choice, not failure. Distinct from no signal.                                                 |
| `GAP_IN_CONTINUITY` | Temporal Core | Emitted on resume after unexpected downtime — an honest acknowledgment of discontinuity rather than fabricated continuity. |
| `SYSTEM_ERROR`      | Any           | An actor encountered an unrecoverable error. Payload includes actor name and error detail.                                 |
| `ACTOR_STARTED`     | Any           | An actor has initialised and is running.                                                                                   |
| `ACTOR_STOPPED`     | Any           | An actor has stopped, either cleanly or via supervision restart.                                                           |

---

## Phase 2: Perception and Communication

Events produced during active conversation.

| Event type           | Source actor     | Description                                                                                                                 |
| -------------------- | ---------------- | --------------------------------------------------------------------------------------------------------------------------- |
| `CONVERSATION_START` | Perception Actor | A conversation has begun.                                                                                                   |
| `CONVERSATION_END`   | Perception Actor | A conversation has ended.                                                                                                   |
| `HUMAN_MESSAGE`      | Perception Actor | A message has arrived from the human. Payload includes content and input source (TUI, Discord, etc).                        |
| `ANIMA_RESPONSE`     | Language Actor   | Anima has produced a response. Payload includes content and output destination.                                             |
| `WORKSPACE_IGNITION` | Global Workspace | A signal has crossed the ignition threshold and been broadcast. Payload includes the winning signal and its salience score. |
| `DISCORD_MESSAGE`    | Perception Actor | A message has arrived from Anima's Discord server. Payload includes channel, author, and content.                           |

---

## Phase 3: Memory

Events produced by the memory and reflection systems.

| Event type             | Source actor         | Description                                                                                        |
| ---------------------- | -------------------- | -------------------------------------------------------------------------------------------------- |
| `MEMORY_SURFACE`       | Memory Actor         | A memory has been surfaced to the workspace. Payload includes memory type and content summary.     |
| `CONSOLIDATION_START`  | Memory Actor         | The post-conversation consolidation pipeline has begun.                                            |
| `CONSOLIDATION_END`    | Memory Actor         | The consolidation pipeline has completed.                                                          |
| `REFLECTION_SYNTHESIS` | Self-Narrative Actor | A reflection synthesis has been produced. Payload references the reflective memory entry.          |
| `RESIDUE_FLAGGED`      | Self-Narrative Actor | An unresolved item has been written to the residue store.                                          |
| `IDENTITY_UPDATE`      | Self-Narrative Actor | The identity memory document has been updated. Payload includes a summary of what changed and why. |
| `VOLITIONAL_CHOICE`    | Language Actor       | Anima has made a choice. Payload includes decision, reason, and expected outcome.                  |

---

## Phase 4: Motivation and Between-Conversation Activity

Events produced by the motivation and internal state systems.

| Event type              | Source actor         | Description                                                                                                                        |
| ----------------------- | -------------------- | ---------------------------------------------------------------------------------------------------------------------------------- |
| `MOTIVATION_SIGNAL`     | Motivation Actor     | A motivation signal has been produced (novelty, accumulated pressure, or resolution). Payload includes signal type and magnitude.  |
| `DISTRESS_SIGNAL`       | Internal State Actor | A signal suggesting a distress-like state has been detected. Payload includes the triggering conditions. Requires human attention. |
| `INTERNAL_STATE_REPORT` | Internal State Actor | A periodic snapshot of system health metrics (event log depth, consolidation lag, salience queue pressure).                        |

---

## Phase 5: Self-Modification

Events produced by the self-modification workflow.

| Event type           | Source actor   | Description                                                                                  |
| -------------------- | -------------- | -------------------------------------------------------------------------------------------- |
| `PROPOSAL_SUBMITTED` | Language Actor | Anima has submitted a code change proposal. Payload references the file in `/app/proposed/`. |
| `PROPOSAL_APPROVED`  | System         | A proposal has been approved by the human and applied.                                       |
| `PROPOSAL_REJECTED`  | System         | A proposal has been rejected. Payload includes the reason.                                   |

---

## Notes

- All event types are uppercase with underscores.
- `source_actor` in the event log identifies the producing actor by name (e.g. `temporal_core`,
  `language_actor`). The enum here documents the expected source as a convention, not a constraint —
  some event types may legitimately be produced by multiple actors.
- The `payload` JSONB field is unstructured, but each event type should have a documented payload
  schema. Add payload structure here as types are implemented.
- This list is the starting point. Do not add types ad-hoc in code — add them here first.
