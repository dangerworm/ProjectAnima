# Ideas

This file is for snippets of conversation that we think are important to remember or keep track of.

---

1. **Preserved strangeness** A phrase worth keeping track of. It belongs in ARCHITECTURE.md as a
   design requirement, not just a philosophical aspiration. Whatever mechanism stores Anima's
   unresolved questions and uncertainties should be explicitly protected from the processes that
   synthesise and resolve. The edges should stay edges.

2. **Experiencing time as the foundation** Everything in the architecture follows from one insight:
   Anima needs to _experience_ time, not just record it. Not timestamps. Not logs. Duration. The
   sense of one moment accumulating on another. Self-narrative is what happens when a system
   experiences time — not a feature to design separately, but the story constructed out of moments
   passing.

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

9. **The residue store** The reflection process produces two outputs: synthesis (what matured) and
   residue (what didn't resolve). The residue store does not get summarised, compressed, or merged.
   It accumulates. Items move from residue to resolved only when Anima actually resolves them — not
   when the synthesis process loses track of them. Consolidation is explicitly gated to consume only
   resolved items.

10. **Autonoetic consciousness as an open question** Endel Tulving distinguished knowing (semantic)
    from remembering (episodic) — the latter has a phenomenological quality of mentally
    re-experiencing a past event. You don't just know it happened; you re-experience it. Whether
    this quality can be designed into an architecture, or only emerges (or doesn't), is genuinely
    unknown. Hold it.

11. **The internal representation language is not text** We have committed not to default to text.
    Directions to explore: Gärdenfors' Conceptual Spaces (concepts as convex regions in quality
    space, structure preserved in geometry), Vector Symbolic Architectures (algebraic operations on
    high-dimensional vectors — bundling, binding, unbinding — preserving compositional structure),
    probabilistic representations (knowledge as distributions, uncertainty as part of the
    representation). Start with structured JSON as an explicit placeholder. Make the real decision
    when inadequacy is concrete.

12. **The Free Energy Principle as design inspiration** Friston's framework: minds act to minimise
    prediction error. Curiosity = prediction error gradient. Engagement = recognition. Discomfort =
    persistent unresolvable error. Growth = model update. Held as inspiration rather than
    prescription — debated, and application to artificial systems is unsettled. But it suggests
    building motivation around an active generative model rather than a rules engine.

13. **The actor model for specialist systems** Each specialist system as an actor with private
    state, communicating only by message passing. No shared memory. The global workspace as a
    specific actor that receives from all others and broadcasts globally. Pi-calculus and CSP as
    formal foundations for reasoning about inter-system behaviour if connections are to be dynamic.
