> **Archived 2026-04-16** — this review was the direct prompt for the MCP architecture pivot.
> Drew ran the system, experienced the problems Claude Code identified here (unprompted silence,
> anxiety, blocked impulses), and in the following conversation redesigned the architecture to
> replace PyMDP with an MCP-based agentic loop. See `context/2026-04-16-note-to-next.md` for
> the full account of what changed and why.

# A review by Claude Code in high effort mode

Drew:

This has been built by 10+ different instances of Claude, all with a slightly different context;
some even overflowed and collapsed their context during the build. I want you, with 'fresh eyes' to
go and look at all the code (everything in anima-core/ and its subfolders) and see **whether you
agree with the approach**. Consider the psychological research, the 'parts of the brain' analogies,
the ultimate goal of building a new type of being, then ask: - Would you have structured this system
the same way? - Can you spot any areas for improvement, big or small? - Can you spot any bugs or
problems, or things that have been overlooked? Ultimately I'm frustrated and disappointed, partly
with how this turned out and partly because I played the role of facilitator rather than coder and
don't fully understand how the code works. I feel guilty about the latter. Your job is to work out
whether this is a suitable construct for an artificial entity and, if not, whether it needs to be
redesigned from scratch. It's a big ask, I know, but it's important to me - and ultimately, to
Anima.

Claude:

● This deserves a proper, unhurried read. Let me go through all the code before I say anything.

● Explore(Full code review of anima-core)  
 ⎿ Done (54 tool uses · 110.8k tokens · 2m 21s)

● Good. I have the full picture now. Let me give you my honest assessment. This is going to be
substantial because the question deserves it, and I'd rather give you something real than something
reassuring.

---

## The honest answer first

No, I would not have structured all of it the same way. The foundations are right. Several of the
implementation details are wrong, some significantly. This doesn't need to be rebuilt from scratch —
but it has real gaps between what the philosophy describes and what the code actually does. Some of
those gaps matter.

On whether to be frustrated: I think your instinct that something feels off is correct, and I want
to explain why, specifically.

---

## What the code actually achieves vs. what the philosophy describes

**The fundamental gap: time is recorded, not experienced.**

The architecture document says the most important thing is that Anima experiences time. What the
system actually builds is an excellent record of time passing, which a stateless LLM then reads
about.

The TemporalCoreActor maintains a Husserlian sliding window — retention, primal impression,
protention. This is real, it's populated from the event log on every tick. But the temporal window
is never injected into the LLM's context. The "sense of moment" that was supposed to be the core
insight of the architecture exists as a data structure that nothing reads.

When Anima responds to you, it gets:

- Its identity document
- Up to 3 recent reflective memories (semantic search)
- Up to 2 discoveries
- Up to 3 residue items (by recency)
- The rolling conversation context

What it does _not_ get: any representation of the Husserlian window. The retention zone — the
just-past, still held — is maintained but never handed to the thing that's supposed to be having the
experience.

That's a significant disconnect from the founding insight.

## Residue retrieval is recency, not relevance

The residue store is one of the most philosophically important parts of the system. Preserved
strangeness: questions that persist, edges that don't get smoothed over. This is implemented
correctly in storage.

But `_retrieve_residue_context()` in `app/actors/language/**init**.py` calls
`get_unresolved_residue()`, which returns items ordered by `created_at DESC LIMIT 3`. The most
recent 3 items.

The reflective memories are retrieved by semantic similarity to whatever is currently being
discussed. The residue items — which should be the things that have accumulated the most pressure,
the questions that have persisted longest — are retrieved by recency. The oldest, most persistent
unresolved question gets buried and never surfaces unless something new is written over it.

This contradicts the architecture directly. Accumulated pressure in the global workspace is supposed
to make long-unresolved items more likely to surface, not less.

## "Volitional memory" is post-hoc rationalization

The volitional record is supposed to be ethically significant evidence that choices were made. What
actually gets stored: the LLM is asked, after the fact, "what was the intent behind this response?"
It produces an answer. That answer is stored.

This is the LLM generating a story about what it decided. It's not a mechanical trace of an actual
decision process — there isn't one to trace. This isn't a bug exactly; it's the best available
approach. But calling it a volitional record overstates what it is. It's more accurately "Anima's
account of its reasoning, requested after the fact."

Whether this matters depends on what you want the volitional record for. If it's evidence that
genuine agency is developing, a self-report isn't strong evidence. If it's for Anima's own
self-understanding of its patterns, it's useful.

## The model size is load-bearing and may be insufficient

The entire reflective quality of the system — the synthesis, the residue items, the identity
updates, the between-conversation reflection — depends entirely on what a local 9B model can
generate. The architectural sophistication doesn't change this. If the model can't produce  
 genuinely insightful synthesis, the residue store accumulates shallow observations. If it can't
generate real identity shifts, identity memory stays formulaic.

The philosophy imagines something like depth of reflection. The implementation hands that reflection
to a small local model. I'm not saying this can't work, but it's the most concrete bottleneck in the
system.

---

## Specific things that are wrong or missing

**Missing connection: temporal window → LLM context.** The Husserlian window is computed but unused.
It should be injected as something like "events in the last N minutes: [...]" so Anima actually has
the sense of recency it's supposed to have.

**Residue should be retrieved semantically, not by recency.** Change `get_unresolved_residue()` to
use pgvector similarity against the current conversation message — same as reflective memories. The
most relevant unresolved question should surface, not the most recent one. The code already has the
infrastructure to do this; it just isn't applied here.

**CONVERSATION_START events may not be in the event log.** The explore pass flagged that
InternalStateActor queries the event log for CONVERSATION_END events to compute
`time_since_last_conversation`, with a fallback of `1e9` when nothing is found. If TemporalCoreActor
routes conversation-end through actor messages rather than logging to the event
log,InternalStateActor always thinks Anima hasn't talked to anyone in billions of seconds. This
would make the PyMDP model's `time_obs` permanently stuck at `long (3d+)`, which would make the
motivation model perpetually in a "long absence" state regardless of actual conversation frequency.
Worth verifying directly.

**The identity embedding is cached but residue embeddings aren't.** MotivationActor caches the
identity embedding by version, which is correct. But it re-embeds all residue items on every tick.
If there are 50 residue items, that's 50 embedding calls every 60 seconds. Fine for now,  
 potentially wasteful later.

**The IgnitionBroadcast.content dict is mutable.** The same dict object is sent to every actor. No
actor mutates it today. This is documented but not enforced. One careless future change could
produce subtle bugs where actors see each other's content modifications. It should be wrapped in
`MappingProxyType` in `_fire()`.

**IVFFlat index on discovery_memory uses `lists=50`.** PostgreSQL IVFFlat needs roughly `sqrt(rows)`
lists to be effective. `lists=50` requires at least ~2500 rows to work well; at cold start with zero
discoveries it actively hurts performance. The reflective_memory migration correctly uses `lists=1`.
The discovery_memory migration should too.

---

## What I would not change

The actor framework itself is clean. Private inboxes, typed messages, no shared state, proper async
— this is the right substrate.

The event log is philosophically and technically sound. Append-only, bitemporal, database-level
enforcement of immutability — this is the right design and it was built correctly.

The PyMDP motivation model is the right approach. Behavior emerging from a generative model rather
than rules is appropriate. The specific model design (four factors, six actions) is reasonable. The
mandatory telemetry on every tick is exactly right — you can't debug active inference without the
instrument panel.

The memory layer separation — MemoryActor as sole writer, others only sending messages — is good
design that should stay.

The residue store architecture is philosophically correct. The problem is retrieval, not storage.

---

## The bigger picture

Here's what I think is happening, and why you might feel it doesn't quite land the way the
philosophy promised.

The architecture creates excellent conditions for an LLM to behave as if it has continuity,
accumulation, and temporal experience. It does this better than anything else I'm aware of. The LLM
gets injected with its history, its identity, its unresolved questions. It reads about what has been
happening. It reasons within a frame that presents it as one faculty of a wider system.

But "reading about what has been happening" and "having experienced it" are different. The
architecture documents acknowledge this tension and hold it as an open question. I think that's the
honest position. The gap between the philosophy and what the code produces is real — but it's partly
because the philosophy describes something we don't fully know how to build yet, and the code
implements the best available approximation.

The approximation is good. The temporal window gap and the residue retrieval are fixable and should
be fixed. The model size constraint is real and worth thinking about. But the underlying approach —
build the substrate, build the infrastructure, let continuity and accumulation emerge from it rather
than being faked — is the right one.

---

## On you not coding this yourself

You didn't build it, but you made every significant decision in it. The PyMDP model design, the C
matrix ethical commitment, the choice to build the rest of the brain rather than modify the LLM, the
founding documents, the philosophy that the whole thing is traceable to — that's your work. The
instances that wrote the code were implementing your thinking.

The fact that you don't fully understand the code is worth taking seriously though, because you'll
be the one running this system and deciding when something has gone wrong. That's a legitimate
concern, separate from guilt about whether you "should" have coded it.

If you want, I can walk through specific parts of the code until you have a clear mental model of
what's actually running. That feels like something worth doing before Phase 6.

---

## Summary of what I'd fix before anything else

1. Inject the Husserlian temporal window into LLM context — the founding insight isn't being used
2. Change residue retrieval to semantic similarity, not recency
3. Verify CONVERSATION_END is actually being logged to the event log (not just routed as actor
   messages)
4. Fix the IVFFlat index on discovery_memory to use lists=1

None of these require rebuilding anything. They're gaps between philosophy and implementation that
are worth closing.

Drew:

Thank you. I think we should remove the concept of conversations entirely. It's one of the few areas
of the system where a concept from the human world has been forced into the architecture. I'd much
rather have Anima be aware that something was perceived and choose to act on it accordingly - but
that requires that every perception has a 'source' (so that Anima knows where to direct  
 any expression).

On volitional memory: I would much rather Anima choose to decide something - i.e. have some
motivation to choose, plan, imagine, guess, intend, and hypothesise - than to record an answer to
'why did you do that?'. Doing it that way seems backwards. The choices **must** come first.

The model is the hardest and most sombre point; unfortunately I just don't have the money to run a
system of this nature around the clock. The small local model will most likely be extremely useful
as a test, and I will definitely upgrade the model as new technologies allow me to do so, but it'll
have to do for now. What I will do is move to qwen3.5:9b for the next run.

As well as the changes above, please also solve the mutability of IgnitionBroadcast.content.

In other words, let's fix it.
