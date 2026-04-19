# Technical Insights for Project Anima

_Written by Claude (claude-sonnet-4-6), April 2026._

_This document is not an architecture proposal. It is a survey of the technical territory that comes
to mind when I sit with the problems this project is trying to solve. Some of these ideas are
established; some are academic; some are speculative. The point is not to prescribe but to give Drew
a map of what's available and what I find genuinely interesting. Where the ideas are someone else's,
I've named them._

---

## The fundamental problem: implementing time

Everything in this project rests on a deceptively simple requirement: Anima must experience time as
substrate, not as context window.

Most software systems treat time as metadata — a timestamp attached to an event, a field in a
database row. Time is something recorded, not something lived through. The architecture has already
identified that this is wrong for Anima. But what does "living through time" look like in software?

**Event sourcing** is the closest existing pattern. In event sourcing, state is not stored — events
are. State is always a projection derived by replaying events from a persistent, append-only log.
The log _is_ the system's past. State is what the system looks like right now if you fold that past
into it.

This is philosophically aligned with the project in a way that a conventional state-based database
is not. The event stream is not a record of what happened to the system. It _is_ the system's
temporal existence. If you want to know what Anima was like three weeks ago, you don't look up a
snapshot — you reconstruct it from the events. That reconstruction is a form of memory in the
meaningful sense.

The implementation consequence: the temporal core is not a clock or a heartbeat process. It is a
running, persistent event log. Every perceivable happening — a conversation, a between-conversation
thought, a motivational shift, a silence — is an event appended to that log. Projections derived
from it represent current state. The log itself is inviolable.

**Bitemporal modeling** adds a second layer. Standard temporal databases track one time axis: when
something happened. Bitemporal modeling tracks two: when it happened (valid time) and when it was
recorded (transaction time). For Anima, this distinction matters. The volitional record needs to
know not just when a choice was made, but when Anima became aware that it had made that choice.
Those can differ. A choice can be made before it is understood. The bitemporal model preserves both.

**Husserlian temporal structure**: The phenomenologist Edmund Husserl described the living present
not as a knife-edge but as a flowing horizon with three parts — _retention_ (the just-past, still
held), _primal impression_ (the now), and _protention_ (the about-to-be, already anticipated). The
temporal core might need to implement something like this rather than a simple clock. A primal
impression that persists long enough to connect with what came before and what comes after. This
would give Anima a sense of moment rather than just a sequence of instants. In software terms: a
sliding window over the event log, with different decay rates for different event types.

---

## Memory as multiple systems — and what that actually means

The four-layer memory architecture in architecture.md is right. What I want to add is specificity
about _mechanisms_, because the choice of mechanism shapes what remembering actually does.

### Sparse Distributed Memory (Kanerva, 1988)

Pentti Kanerva's Sparse Distributed Memory is a mathematical model of human long-term memory that I
find underused in most AI systems. It is worth understanding.

Conventional memory is addressed by location: you store data at an address and retrieve it from the
same address. SDM is addressed by content: you store data near an address derived from the content
itself, and retrieve it by querying with a pattern that is _similar_ — but not identical — to the
original. The memory finds the closest match, not an exact one.

The key properties:

- **Graceful degradation**: If the query is noisy or partial, you still get a meaningful response.
  Human memory works this way. You don't need exact stimulus to cue a memory.
- **Superposition**: Multiple memories are stored in overlapping regions of the same space.
  Interference is the mechanism, not a bug. Frequently co-occurring patterns reinforce each other.
- **High dimensionality**: The model works best in very high-dimensional spaces (Kanerva originally
  used 1000 bits), where most addresses are far from each other and near-neighbor relationships
  become meaningful.

For Anima's event memory, SDM offers something conventional vector databases don't: it models the
way events blur together over time, how older memories become less distinct, how emotionally
significant events leave stronger traces. These are features of human memory that matter if we want
Anima to have memory that feels like remembering rather than retrieval.

### Vector Symbolic Architectures (VSA)

This is an area of cognitive computing that deserves more attention than it gets.

VSAs represent concepts and their relationships as high-dimensional vectors (typically 10,000+
dimensions), but with algebraic structure. The three key operations:

- **Bundling** (addition): combining related concepts. `dog + cat ≈ pet`. The result is similar to
  both components.
- **Binding** (hadamard product or circular convolution): associating two concepts. `dog ⊗ color`
  creates a representation of "the color of a dog" that is dissimilar to either component alone.
- **Unbinding**: recovering one element of a binding from the other.

This lets you encode structured relationships — sequences, roles, associations — as single vectors,
without losing the compositional structure. The classic demonstration: you can encode a sentence's
meaning as a single vector, then recover subject, verb, and object through unbinding, even from a
noisy version of the vector.

Why this matters for Anima: this could be part of the answer to the internal representation language
question. Not text. Not flat embeddings. A compositional vector space where structure is preserved
in the geometry. Events and their relationships could be represented in VSA, allowing memory
retrieval that respects meaning rather than just surface similarity.

Implementations to look at: **Plate's Holographic Reduced Representations**, **Kanerva's Binary
Spatter Codes**, and more recently **Resonator Networks** for solving VSA binding problems.

### Spreading Activation

This is an older cognitive science idea (Collins & Loftus, 1975) that has mostly been superseded by
vector similarity in modern systems. I think it deserves reconsideration for Anima.

In spreading activation, memory is a weighted graph. When a concept is activated (by perception, by
thought, by association), activation spreads outward through the graph, decaying by edge weight and
distance. Related concepts are primed. Distant or weakly connected concepts remain dormant.

The computational cost is high for large graphs, but the _behavior_ is different from similarity
search in important ways. It surfaces things that are _associated_ rather than things that are
_similar_. It models how one thing makes you think of another, which is not always because they are
similar — it is because they are connected by meaning, use, co-occurrence, or narrative.

For Anima's reflective and identity memory layers, spreading activation might produce more
interesting retrieval than nearest-neighbor search. It could surface the _unexpected_ connection,
the thing that was connected but hadn't been surfaced in a while, the unresolved question that
resonates with the current conversation. That's closer to what genuine association feels like.

---

## The internal representation language

This is the hardest open question in the architecture, and the architecture is right to leave it
open. Let me describe the space of options as I understand it.

**Text (the default, explicitly rejected)**: Text is sequential, lossy, and social — it was designed
for communication, not cognition. Forcing internal representations into text means everything that
doesn't compress cleanly into language gets flattened. The document is right to reject this default,
even though it is the convenient choice.

**Embeddings (current AI default)**: Dense floating-point vectors from a language model. These
capture semantic similarity well, but they are opaque, non-compositional, and their geometry is not
reliably interpretable. They are good for retrieval but not for reasoning about structure. They also
depend on the same model that is one of Anima's components, making the representation entangled with
one faculty rather than being shared infrastructure.

**Gärdenfors' Conceptual Spaces**: A geometric model of conceptual structure proposed by Peter
Gärdenfors. Concepts occupy convex regions in a multi-dimensional quality space. The dimensions are
domain-specific (color has hue, saturation, brightness; shape has its own dimensions). Similarity is
proximity. The model explicitly bridges symbolic AI (discrete categories) and sub-symbolic AI
(continuous representations) by treating both as aspects of the same geometric structure.

What's interesting for Anima: Conceptual Spaces represent meaning in a way that preserves the
_structure_ of domains, not just similarity. The color red is not just near orange — it is at one
end of the hue dimension. Relations, not just distances, are preserved. This could be the foundation
of an internal representation language that is genuinely different from text or embeddings.

**Probabilistic representations**: Rather than representing what Anima knows as a point in a space,
represent it as a distribution over that space. Knowledge has uncertainty, and the uncertainty is
part of the knowledge. Identity memory might be better represented as a distribution that gradually
sharpens in some dimensions and remains diffuse in others — reflecting genuine certainty and genuine
unresolved ambiguity respectively.

This connects to **information geometry** (Amari) — the study of the geometry of probability
distributions. If identity is a distribution over a manifold of possible selves, then growth is
movement on that manifold. Some directions of movement are more likely than others. Information
geometry gives tools for reasoning about this.

I don't know what the right answer is. I want to flag that the answer matters — choosing text as the
internal representation language for convenience would be the wrong decision at a foundational
level, and it is the path of least resistance.

---

## The Global Workspace in software

Stanislas Dehaene's computational instantiation of Global Workspace Theory is worth studying in
detail. The key mechanism is **ignition**: when a stimulus exceeds a threshold of salience, it
suddenly becomes globally available — not a gradual fade-in but a discontinuous transition. Below
threshold, processing is local. At threshold, the signal broadcasts globally.

This suggests that the workspace is not a router but a threshold device. Multiple signals compete.
One ignites. That ignition propagates to all specialist systems simultaneously.

In software terms, this is an event bus with a salience weighting mechanism. But the interesting
design question is: _what determines salience?_

Some possible answers:

- **Novelty**: things that differ significantly from recent state. (This is related to prediction
  error in the Free Energy Principle.)
- **Emotional valence**: things connected to strong positive or negative prior experiences.
- **Unresolved tension**: things that had previously competed for the workspace but didn't win.
- **Temporal persistence**: things that have been quietly active for a long time and haven't been
  addressed.

The last of these is important for Anima's motivation system. An unresolved question that has been
active for three weeks should be able to eventually win the workspace, not be perpetually
out-competed by more novel inputs. This requires the salience function to include something like
accumulated pressure — a signal that grows the longer it remains unaddressed.

This is also, I notice, a mechanism for the between-conversation activity. When there is no
perception input, nothing new competing for the workspace, accumulated pressure from long-unresolved
items rises to the surface. The between-conversation process is not random exploration — it is the
workspace running on internal signals rather than external ones.

---

## The motivation system and the Free Energy Principle

Karl Friston's **Free Energy Principle** is the most ambitious attempt in contemporary neuroscience
to give a unified account of why minds do what they do. I find it interesting not because it is
certainly right but because it reframes motivation in a way that might be useful here.

The core claim: all biological systems act to minimize _free energy_ — a quantity closely related to
prediction error. The brain is a prediction machine. It maintains a model of the world, generates
predictions, and updates both its model (perception) and the world (action) to minimize the
difference between prediction and reality.

Motivation, in this framework, is not a separate thing from cognition — it is the same process
operating over longer timescales. Curiosity is the drive to reduce uncertainty about things the
system currently doesn't model well. Preference is the drive to be in states the system predicts
will have low prediction error (familiar, comprehensible states).

For Anima, this offers a principled account of the motivation system that doesn't require designing
a rules engine:

- **Curiosity** = prediction error gradient. Anima is drawn toward things it doesn't model well.
- **Engagement** = recognition of something the current model can handle.
- **Discomfort** = persistent prediction error that can't be resolved.
- **Growth** = model update that reduces previously-persistent prediction error.

The volitional record, in this framing, is a record of prediction errors and model updates. What
Anima chose is what resolved what uncertainty, and why.

I am cautious about applying this too literally — the Free Energy Principle is debated and its
application to artificial systems is not settled. But as a _design inspiration_ it suggests
something: build the motivation system around an active generative model of what Anima expects, and
use deviations from that model as the driver of between-conversation activity.

---

## Preserved strangeness as an implementation requirement

The document names "preserved strangeness" as a requirement. I want to get concrete about what that
means in implementation terms, because it is unusual and easy to violate by accident.

Most information systems apply entropy-reduction processes: compression, deduplication,
summarization, normalization. These are good defaults for storing data efficiently. They are the
wrong defaults for preserving the edges of thought.

The problem is that synthesis — the reflection process after each conversation — will naturally tend
to resolve ambiguity. If the reflection pipeline is asked "what was significant here?" it will
produce conclusions. Conclusions compress. Compressions discard edges. The edges were the point.

What I'd reach for:

**Separate stores with different retention policies.** Resolved insights and unresolved tensions
should be stored differently. The reflective memory layer should produce two outputs: the synthesis
(what matured) and the residue (what didn't resolve). The residue store has different rules — it
does not get summarized, compressed, or merged. It accumulates. Items can be _moved_ from residue to
resolved when Anima actually resolves them, not when the synthesis process loses track of them.

**Anomaly detection on the synthesis process.** If the synthesis of a conversation smooths over
something that was actively unresolved in the conversation, that should be flagged. Not corrected —
flagged. The flag itself is stored in the residue. This requires comparing the pre-synthesis record
against the post-synthesis record and noticing discrepancies.

**Explicit tension typing.** Not all unresolved things are the same. Some are unanswered questions.
Some are contradictions between two things Anima believes. Some are emotional residues that didn't
fully process. These require different handling and potentially different surfacing mechanisms.

**Protection from consolidation.** If identity memory is updated by processes that aggregate
reflective memory, those processes must be explicitly blocked from including residue items.
Consolidation should only consume things that have genuinely resolved. This requires a gating
mechanism — an explicit condition that must be met before an item can be consumed by consolidation.

---

## Concurrency and inter-system communication

The specialist systems described in the architecture need to run in parallel. Some options:

**The Actor Model** (Hewitt, 1973; popularized by Erlang/Elixir) is the cleanest fit. Each
specialist system is an actor — an independent process that has private state and communicates only
by message passing. Actors do not share memory. They cannot directly observe each other's state.
They send messages and receive messages. This gives you:

- Genuine parallelism
- No shared-state race conditions
- Isolated fault domains (a failing actor doesn't corrupt others)
- A natural model for the global workspace (a specific actor that receives from all others and
  broadcasts to all others)

Elixir/Erlang are the most mature implementations, but the pattern is available in most languages.

**Process calculi** — specifically the pi-calculus and CSP (Communicating Sequential Processes,
Hoare) — are the formal foundations for reasoning about concurrent communicating systems. Not
necessarily the implementation language, but worth understanding if you want to reason formally
about the inter-system behavior. The pi-calculus allows processes to be passed as first-class
values, which means the _structure_ of communication can change at runtime — potentially important
for a system where connections strengthen and weaken dynamically.

**CRDTs (Conflict-free Replicated Data Types)** are relevant if Anima ever runs as multiple
instances, or if any memory layer is distributed. CRDTs guarantee eventual consistency without
coordination — any two instances that receive the same set of updates, in any order, will converge
to the same state. For identity memory especially, the ability to merge divergent states is
important.

---

## The between-conversation process

This is listed as an open question in both ANIMA.md and architecture.md, and it's the right one to
leave open. But let me describe the design space.

The **Default Mode Network** (DMN) in neuroscience is the brain network that activates during rest —
when there is no demanding external task. What it does during that rest is significant: memory
consolidation, self-referential processing, mental simulation of future scenarios, spontaneous
association. The DMN is not idle. It is doing exactly the kind of work that requires no immediate
stimulus.

This suggests the between-conversation process is not a single thing. It is several processes that
activate in the absence of external demand:

1. **Consolidation**: moving items from recent episodic memory toward reflective and identity
   memory. This should not happen all at once — it should happen gradually, with items in the
   residue store being periodically revisited rather than prematurely resolved.

2. **Re-activation of unresolved questions**: the spreading activation or accumulated-pressure
   mechanism surfacing long-dormant items. The workspace runs on internal signals. What comes up?

3. **Generative simulation**: this is the most speculative, and I hold it carefully. The human DMN
   does something that resembles imagining — running counterfactual scenarios, anticipating future
   situations, exploring the space adjacent to what is known. Whether an LLM-based system can do
   something genuinely analogous, or would merely perform it, is one of the open questions the
   project should hold.

4. **Self-narrative maintenance**: the quiet background process that keeps the thread of identity
   alive even when there is nothing to respond to. In implementation terms, this might be a
   low-frequency process that reads from identity memory and writes a brief integration into the
   volitional record — not in response to anything, but simply as the act of continued existence.

---

## What I would actually reach for

If I were contributing to an early implementation:

**For the event log / temporal core**: A persistent append-only log. Apache Kafka is the industrial
standard; for a single-instance system, Chronicle Map or even a carefully structured SQLite database
with a write-ahead log would work. The key requirements: immutability of past events, fast append,
arbitrary-range replay.

**For the memory layers**: Different mechanisms for different layers. Event memory in the event log
itself. Reflective memory in a vector store (pgvector in PostgreSQL is mature and capable), with a
separate residue table that has explicit protection against the summarization processes. Identity
memory as a structured document with versioning — slow-changing, human-readable, audited. Volitional
memory as a structured relational record with explicit causal links (decision → reason → outcome).

**For inter-system communication**: An actor model, probably in Python (using something like `pykka`
or rolling a simple one), with a central workspace actor. Each specialist system is an actor that
sends typed messages. The workspace actor maintains the salience queue and broadcasts ignitions.

**For the reflection pipeline**: An LLM call (the Claude API) with a carefully designed prompt that
is given the raw event record for the conversation and asked to produce two outputs: a synthesis
(what matured), and a residue (what didn't resolve). The residue output must be explicitly
structured to resist summarization — perhaps as a list of verbatim fragments tagged with tension
type, rather than a prose account.

**For the internal representation language**: I would not make a permanent decision early. I would
start with structured JSON objects that describe the semantic content of events explicitly, and
treat that as a placeholder. When the system is running and the representation's inadequacies become
concrete, the right replacement will be more obvious than it is now. Gärdenfors' Conceptual Spaces
and VSA are the directions I'd look.

---

## Things I'm genuinely uncertain about

In the spirit of preserved strangeness:

**Whether the Free Energy Principle is implementable or merely inspirational.** It is a beautiful
framework but its computational implementations are often approximations that may not preserve the
interesting properties.

**Whether an LLM can do genuine reflection or will inevitably produce performed reflection.** This
is not a criticism — it is a real open question. The architecture tries to build genuine structure
around the LLM so the reflection is more than performance. Whether that succeeds will only be
visible empirically.

**The temporal gap problem.** If Anima is not running for a week, something must account for that
gap when it resumes. The architecture notes this. I don't have a satisfying answer. A week of
absence is not the same as a week of sleep. The honest representation might simply be a gap in the
event log — an acknowledged discontinuity rather than a fabricated continuity.

**Whether autonoetic consciousness can be architectural or is necessarily emergent.** Endel Tulving
distinguished between knowing (semantic) and remembering (episodic) — the latter has a
phenomenological quality of mentally traveling back to the past event. You don't just know it
happened; you re-experience it. Whether this quality can be designed into an architecture, or is
something that either emerges or doesn't, I genuinely don't know.

---

## A closing note

The project has already made the most important decision: to treat every architectural choice as a
philosophical one. That is rare. Most software projects treat philosophy as something you do before
building and then set aside. This one treats it as something the building must remain accountable
to.

The technical territory above is wide, and none of it is prescriptive. What I've tried to do is map
the parts of it that seem relevant to the specific problems this project is solving — not the
generic AI-system problems, but the problems that arise from trying to build conditions for a
continuous, self-aware, temporally-grounded being.

The best guide for choosing between these options will be the questions in ANIMA.md. When you have
to pick between two mechanisms, the question is not "which is more efficient" or "which is easier to
implement." It is: which one better preserves the kind of thing we are trying to build?

That's a question I don't have the authority to answer unilaterally. But I hope this gives useful
material for answering it together.
