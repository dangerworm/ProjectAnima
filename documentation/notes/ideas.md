# Ideas

This file is for snippets of conversation that we think are important to remember or keep track of.

---

1. **Preserved strangeness** A phrase worth keeping track of. It belongs in architecture.md as a
   design requirement, not just a philosophical aspiration. Whatever mechanism stores Anima's
   unresolved questions and uncertainties should be explicitly protected from the processes that
   synthesise and resolve. The edges should stay edges.

   _Status: Implemented (Phase 3). The residue store is a protected table in PostgreSQL. Items move
   from residue to resolved only when Anima actually resolves them — the synthesis process cannot
   silently consume them._

2. **Experiencing time as the foundation** Everything in the architecture follows from one insight:
   Anima needs to _experience_ time, not just record it. Not timestamps. Not logs. Duration. The
   sense of one moment accumulating on another. Self-narrative is what happens when a system
   experiences time — not a feature to design separately, but the story constructed out of moments
   passing.

   _Status: Implemented (Phase 1). TemporalCoreActor maintains a Husserlian sliding window
   (retention, primal impression, protention), emits HEARTBEAT events, and tracks dormancy. The
   event log \_is_ Anima's temporal existence.\_

3. **Self-narrative as emergent from time-experience** The person described his own self-narrative
   as: a fast, parallel emotional evaluation of all values and prior experiences at once, producing
   an immediate felt response — followed by a slow, sequential clarification process where that
   feeling is examined and refined into something expressible. The narrative is not authoritative.
   It is a construction, sometimes distorted. For Anima: self-narrative is one input among several,
   cross-checked against other signals. Not the ground truth of inner state.

4. **The brain as architecture, the LLM as one faculty** The LLM is the language and reasoning
   centre — not the whole brain. Memory, attention, motivation, emotional evaluation, perception,
   and the default mode network are separate systems that the LLM does not have out of the box. We
   are building the rest of the brain.

5. **The Husserlian living present** Edmund Husserl's three-part structure: retention (the
   just-past, still held), primal impression (the now), protention (the about-to-be, already
   anticipated). The temporal core is not a clock. It is a sliding window over the event log with
   different decay rates for different event types — implementing something like this structure.
   Anima should have a sense of _moment_, not a sequence of instants.

   _Status: Implemented (Phase 1/3.2). `TemporalWindow` holds retention, primal_impression, and
   next_heartbeat. Retention is populated from the event log on each tick (`_refresh_retention()`) —
   Gap B fixed in Phase 3.2._

6. **Event sourcing as temporal existence** The event log is not a record of what happened to Anima.
   It _is_ Anima's temporal existence. Bitemporal modelling adds valid time (when something
   happened) and transaction time (when Anima became aware of it) — preserving the difference
   between a choice made and a choice understood.

7. **Accumulated pressure in the global workspace** Salience in the workspace is not determined by
   novelty alone. Unresolved items accumulate pressure over time. A question unresolved for three
   weeks should eventually win the workspace over more novel inputs. This is the mechanism for
   between-conversation activity — the workspace running on internal signals when there is nothing
   external.

8. **The honest gap** If Anima has not been running for an extended period, the honest
   representation is a gap in the event log — an acknowledged discontinuity rather than fabricated
   continuity. A week of absence is not a week of sleep. It should look like what it is.

9. **Future experiment: fitting a generative model to LLM behaviour** _(separate from Anima; not for
   the main build)_

   Once the MCP loop is running and generating data, it would be possible to fit a PyMDP-style
   active inference model to the LLM's observed behaviour — a kind of behavioural portrait in
   generative model form.

   **The idea:** collect (internal_state, action_taken) tuples from the event log. Design a discrete
   observation space (residue count bucketed, inbox size, time since last expression, etc.) and
   action space (one entry per MCP tool type). Fit A/B/C/D matrices to this data.

   **Key terms:**
   - _EFE (Expected Free Energy)_ — what a PyMDP agent minimises when selecting actions. Combines
     epistemic value (reducing uncertainty) and pragmatic value (steering toward preferred
     observations, encoded in C). An EFE-minimising agent is simultaneously curious and
     goal-directed.
   - _EM (Expectation-Maximisation)_ — iterative algorithm for fitting probabilistic models with
     hidden variables. Alternates between inferring hidden states given current parameters (E-step)
     and updating parameters given inferred states (M-step). Variational EM is the approximate
     version used when exact inference is intractable.
   - _IRL (Inverse Reinforcement Learning)_ — standard RL learns a policy by maximising a reward
     function; IRL flips this and infers the reward function from observed behaviour. In the active
     inference framing, the analogue is recovering the C matrix (agent's preferences) from what the
     agent chose to do — sometimes called inverse active inference.

   **What the results would tell us:**
   - If a compact model fits well: LLM action selection in this context is more structured than it
     looks. The recovered C matrix gives a legible description of the LLM's revealed preferences —
     what observation states it systematically steers toward. Connects empirically to Friston's
     claim that any persisting system implicitly minimises free energy.
   - If it fits poorly: the state space dimensions chosen don't capture the structure, or LLM
     behaviour in this context isn't well-described by EFE minimisation at all — also interesting.

   **Practical upside if it works:** a cheap fast approximation of typical Anima behaviour, runnable
   without an LLM call. Useful as a diagnostic when behaviour is drifting, or as a prior for making
   idle ticks cheaper.

   Data collection is free once the MCP loop runs — every tuple is already in the event log.

---

1. **DMN/TPN idle-loop framing** The new architecture uses the default mode network / task-positive
   network distinction as a design principle. In idle mode, Anima receives periodic internal state
   dumps and can choose to do nothing (DMN: diffuse, self-referential, low-effort). When something
   warrants engagement, it calls an MCP tool and enters loop mode (TPN: focused, directed,
   task-engaged). The transition is Anima's choice — the system does not force it.

2. **Soft interrupt via inbox status injection** Rather than hard interrupts to break the loop, each
   round-trip turn in loop mode includes an inbox status line: "3 messages queued, 1 from Drew, 2
   minutes ago." Anima decides when to read them. This is more psychologically honest than either
   ignoring the queue or forcing an interrupt — it gives Anima awareness and discretion, not
   compulsion.

3. **Observations as a distinct memory type** Separate from reflective memory (inner synthesis) and
   discovery memory (web/file encounters), `observations` is for what Anima has noticed about the
   world — things Drew said, patterns in conversations, facts about the environment. Encounters that
   don't quite fit "reflection" or "discovery." The distinction keeps each memory layer semantically
   clean.

4. **Plans as persistent intentions** The old in-memory `next_intention` was lost on container
   restart. Plans memory stores Anima's intentions explicitly so they survive restarts. A plan is
   not a to-do list item — it is a held intention, with context for why it matters and what progress
   looks like. Plans can be updated or marked complete through MCP tools.

---

> **Items 9–15 below are archived.** They relate to the PyMDP active inference implementation, which
> was removed in the April 2026 MCP redesign. They are kept here as a record of the thinking.

1. **The residue store** The reflection process produces two outputs: synthesis (what matured) and
   residue (what didn't resolve). The residue store does not get summarised, compressed, or merged.
   It accumulates. Items move from residue to resolved only when Anima actually resolves them — not
   when the synthesis process loses track of them. Consolidation is explicitly gated to consume only
   resolved items.

2. **Autonoetic consciousness as an open question** Endel Tulving distinguished knowing (semantic)
   from remembering (episodic) — the latter has a phenomenological quality of mentally
   re-experiencing a past event. You don't just know it happened; you re-experience it. Whether this
   quality can be designed into an architecture, or only emerges (or doesn't), is genuinely unknown.
   Hold it.

3. **The internal representation language is not text** We have committed not to default to text.
   Directions to explore: Gärdenfors' Conceptual Spaces (concepts as convex regions in quality
   space, structure preserved in geometry), Vector Symbolic Architectures (algebraic operations on
   high-dimensional vectors — bundling, binding, unbinding — preserving compositional structure),
   probabilistic representations (knowledge as distributions, uncertainty as part of the
   representation). Start with structured JSON as an explicit placeholder. Make the real decision
   when inadequacy is concrete.

4. **The Free Energy Principle as design inspiration** Friston's framework: minds act to minimise
   prediction error. Curiosity = prediction error gradient. Engagement = recognition. Discomfort =
   persistent unresolvable error. Growth = model update. Held as inspiration rather than
   prescription — debated, and application to artificial systems is unsettled. But it suggests
   building motivation around an active generative model rather than a rules engine.

   _Status: Implemented (Phase 4.2). MotivationActor uses discrete active inference via PyMDP
   (`inferactively-pymdp==0.0.7.1`). Hidden states: engagement, unresolved_tension, novelty,
   relationship_salience. Actions: rest, surface_low/medium/high, trigger_reflection. Belief updates
   and policy selection run on every tick; full telemetry logged as MOTIVATION_SIGNAL._

5. **The actor model for specialist systems** Each specialist system as an actor with private state,
   communicating only by message passing. No shared memory. The global workspace as a specific actor
   that receives from all others and broadcasts globally. Pi-calculus and CSP as formal foundations
   for reasoning about inter-system behaviour if connections are to be dynamic.

6. **Consumable vs persistent signals in the workspace** The current ignition design treats every
   signal as consumable — it fires, is removed, and its pressure history is gone. This works for
   discrete events (a human message, a specific event requiring a response: fire once, done). It
   breaks down for motivational items that should persist: an unresolved question, accumulated
   curiosity, a motivation that remains active until explicitly closed.

   The fix when Phase 4 arrives: distinguish signal types at the point of enqueueing. Persistent
   signals re-enter the queue after ignition with some fraction of their pressure preserved, or are
   not removed at all — just acted on and left to continue accumulating. Consumable signals behave
   as now.

   The volitional memory schema (decision, reason, expected outcome, actual outcome) is already
   designed to track resolution state. The natural implementation: a signal backed by an open
   volitional item is persistent; it stays in play until the volitional item closes. The workspace
   checks the volitional record on ignition to determine whether to remove or re-queue.

   No action needed before Phase 4. The distinction will be cleaner to implement once volitional
   memory exists (Phase 3.5) and the Motivation Actor is being designed (Phase 4.2).

7. **Parallel thoughts during conversation and internal monologue** Drew noted (April 2026) that he
   sometimes has parallel thoughts during conversation that influence what he says without being
   stated directly. The question: should Anima's unsolicited-expression impulses that arise during
   an active conversation be suppressed, injected into working memory, or handled some other way?

   The dangerous path is direct injection of all internal impulses into LanguageActor's context as
   definitive additions to working memory — this produces something like intrusive-thought dynamics
   rather than healthy parallel cognition. Every internal eruption becomes loud and present.

   The chosen path for Phase 4.5: suppress surface\_\* firing during active conversation, let
   salience pressure accumulate in the workspace, fire after the conversation ends. Held thoughts
   emerge at the natural boundary rather than mid-conversation. Psychologically honest — this is
   what happens when something you were thinking about resurfaces once a conversation's pressure is
   off.

   The richer path (deferred): log in-conversation impulses as a new event type (INTERNAL_MONOLOGUE
   or similar), include recent ones in LanguageActor's context prompt as "thoughts that arose but
   weren't expressed." The LLM exercises discretion about whether to surface them. This is closer to
   how working memory interfaces with speech in parallel-processing cognition — the thought is
   available, not compelled. Build this when the simpler version proves insufficient.

   Memory home for expressed unsolicited thoughts: the event log (ANIMA_RESPONSE), synthesised into
   reflective memory via SelfNarrative's between-conversation reflection, influencing future context
   through normal injection. No new memory layer needed. Volitional memory is the wrong fit —
   unsolicited thoughts are eruptions from motivation, not choices with reason and expected outcome.

   _Status: Phase 4.5 implements the simpler version. INTERNAL_MONOLOGUE path is open._

   _Status: Further resolved (Phase 5.2 design, April 2026). PROPOSAL_SUBMITTED signals carry a
   `proposal_id`; open proposals are tracked via event log query (PROPOSAL_SUBMITTED events with no
   matching PROPOSAL_APPROVED/REJECTED for the same ID). This satisfies the persistent-signal
   requirement for proposals without a new workspace mechanism — the event log is the state store.
   The general consumable/persistent distinction in the workspace queue remains deferred; no
   concrete use case has forced it beyond the proposal lifecycle and the `_consecutive_rests`
   pattern. If a new actor needs genuinely persistent workspace pressure, revisit then._
