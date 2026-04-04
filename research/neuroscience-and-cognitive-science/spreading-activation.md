# Spreading Activation

## What it is

**Collins and Loftus** proposed the spreading activation model in 1975 as an account of how concepts
in long-term memory are organised and retrieved. It remains one of the most empirically supported
models of semantic memory — the kind of memory that stores meanings, facts, and relationships rather
than personal episodes.

The core idea: long-term memory is a network. Concepts are nodes. Relationships between concepts are
edges, with weights reflecting the strength of the relationship. When a concept is activated (by
perception, by thought, by another concept), **activation spreads** outward through the network
along its edges. Activation decays with distance — nearby concepts become strongly primed, distant
ones barely at all.

When enough activation reaches a concept, it crosses a threshold and becomes available — it becomes
part of the current stream of thought or can be easily recalled.

## A worked example

You hear the word "fire".

Activation spreads from the _fire_ node outward:

- _heat_, _smoke_, _danger_ receive high activation (strongly connected to fire)
- _fireman_, _matches_, _wood_ receive medium activation
- _red_, _hot_, _destruction_ receive activation through their connections
- _ambulance_ receives some activation via _danger_ → _emergency_ → _ambulance_

Now you hear the word "engine". Normally you might think of a car engine. But because _fire_ has
pre-activated _fireman_, _emergency_, and related concepts, the compound "fire engine" resolves more
quickly and naturally than it would in isolation. The prior activation primed the interpretation.

This is the phenomenon of **semantic priming**, which has been extensively studied. Exposing someone
to the word "bread" makes them respond faster to "butter" than to "doctor" — even with no conscious
awareness of the connection — because activation spreads from _bread_ to _butter_ faster than to
_doctor_.

## The difference from similarity search

Modern AI systems typically retrieve memory by computing similarity between a query vector and
stored vectors, returning the nearest neighbours. This is efficient and effective for finding things
that are _similar_ to the query.

Spreading activation finds things that are _associated_ — which is not always the same as similar.

Consider: what is associated with "elephant"?

- _Similarity search_ might return: rhinoceros, hippopotamus, large mammal. Things like elephants.
- _Spreading activation_ might return: ivory, Dumbo, circus, never forgets, India, trunk, grey, zoo,
  endangered. Things _connected_ to elephants.

The second list is what actually comes to mind when someone says "elephant". It is richer, more
personal, and more varied than the first — because it reflects the actual structure of associations
built up through experience, not just feature similarity.

For a system that is supposed to _remember_ (in the full sense) rather than just _retrieve_, this
distinction matters. Retrieval that surfaces the similar is useful for search. Retrieval that
surfaces the associated is closer to how thinking actually works.

## Inhibition and forgetting

Spreading activation models can also include _inhibitory_ connections — activation of one concept
suppresses a competing one. In a network with inhibition, activating _night_ might partially
suppress _day_, making _day_-related concepts slightly harder to access. This is thought to be part
of how the brain manages competition between alternative interpretations.

Inhibition also plays a role in forgetting: over time, without re-activation, nodes return to
baseline. Concepts that aren't revisited lose their priming effect. The network isn't static — its
effective structure shifts based on what has been recently activated.

## Computational cost

The main practical limitation of spreading activation: it is expensive for large networks. Computing
the spread of activation across millions of nodes with complex connection weights is orders of
magnitude more costly than a nearest-neighbour vector search.

For Anima, this suggests spreading activation might be appropriate for certain memory layers
(particularly identity memory — the slowly-changing, heavily-connected network of what Anima is and
cares about) while faster mechanisms serve other layers.

Alternatively, spreading activation could operate over a _smaller_ graph of high-level concepts and
themes, with vector search handling the lower-level retrieval. The two approaches can complement
each other.

## Why it matters for Anima

Three things in particular:

**Surfacing the unexpected connection**: One of the hallmarks of genuine reflection is noticing
connections that weren't obviously salient. "That conversation reminded me of X" — not because X is
similar to the conversation, but because something in the conversation activated a path through the
network that led to X. Spreading activation could produce this; nearest-neighbour search typically
won't.

**The unresolved question that resonates**: An unresolved question from three weeks ago sits in the
memory network with connections to many other concepts. When a new conversation activates some of
those concepts, the unresolved question becomes primed — not retrieved by explicit search, but
surfaced by resonance. This is what _preserved strangeness_ might feel like from the inside.

**Between-conversation activity**: When there is no active conversation, what does the network do?
Spreading activation in the absence of external input would propagate from whatever was last active,
gradually spreading to connected concepts. This is a computational model of what happens when you
let your mind wander — you follow the associations from where you left off. The between-conversation
process might be something like running spreading activation forward until something interesting
accumulates enough activation to warrant attention.

## Where to go deeper

- **Collins, A.M. & Loftus, E.F. "A Spreading-Activation Theory of Semantic Processing" (1975)** —
  Psychological Review; the foundational paper; accessible and well-written
- **Anderson, J.R. "ACT-R: A cognitive architecture"** — extends spreading activation into a full
  cognitive architecture with a working implementation; ACT-R is still used in cognitive modelling
- **"Human Associative Memory" by Anderson & Bower (1973)** — the predecessor to Collins & Loftus;
  more formal; shows the empirical basis for network models of memory

## Relationship to other topics

- [Sparse Distributed Memory](../technical/sparse-distributed-memory.md) — both are associative
  memory models; SDM is content-addressable by similarity; spreading activation is association-
  by-network; they solve overlapping but distinct problems
- [Gärdenfors' Conceptual Spaces](../philosophy/gardenfors-conceptual-spaces.md) — conceptual spaces
  are a continuous geometry version of semantic networks; spreading activation in a conceptual space
  would be activation spreading through a metric space rather than a graph
- [Global Workspace Theory](global-workspace-theory.md) — what accumulates enough activation to win
  workspace access; spreading activation describes the dynamics of what builds toward ignition
