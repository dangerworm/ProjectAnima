# Person Knowledge & Concept Nodes

## The thing you notice when it breaks

**Prosopagnosia** is the inability to recognise faces. People with this condition — caused by damage
to the fusiform gyrus in the inferior temporal lobe — cannot match a face to a known person.
Familiar faces look like strangers. A man with severe prosopagnosia might fail to recognise his own
wife by sight.

But he knows everything about her. Her name, her voice, her habits, their shared history. The moment
she speaks, recognition floods in. The knowledge is intact. Only the face-based route to it is
broken.

This dissociation reveals something important: face recognition and person knowledge are separate
systems. You can have the knowledge without the recognition route, or (in other conditions) the
recognition without the knowledge. They are distinct, and the architecture reflects that.

---

## The Bruce and Young model

In 1986, Vicki Bruce and Andrew Young proposed a functional model of face recognition that remains
influential. The pipeline has three stages:

**Structural encoding** — the face is perceived as a face and its structural features are
extracted. This is the FFA's job. It produces a representation of the face's configuration
independent of lighting, angle, expression.

**Face Recognition Units (FRUs)** — stored structural templates of known faces. When structural
encoding produces a representation that matches a stored template, a signal is generated: "I have
seen this face before." The FRU does not know whose face it is. It only signals familiarity.

**Person Identity Nodes (PINs)** — the convergence point. The PIN is where all knowledge about
a person is stored and accessed. It receives input from FRUs (face), but also from voice recognition
units, name recognition units, and contextual cues. Once a PIN is activated, everything known about
that person becomes available: biographical facts, emotional associations, the relationship to you,
their habits, what happened the last time you saw them.

**Name generation** — a separate, notably fragile step. Names are not stored at the PIN. They are
generated after PIN activation via a separate route. This is why the "tip of the tongue" phenomenon
is asymmetric: you can often know everything about someone — what they look like, where they work,
how you know them — while their name remains momentarily inaccessible. The PIN activated; the name
generation step didn't fire.

---

## What the PIN actually is

The PIN is not the face, the name, the voice, or any other perceptual representation. It is the
**abstract convergence point** for multiple recognition routes.

Multiple routes → single PIN → all associated knowledge.

This architecture solves an important problem: the same person can be encountered in many ways.
You might see their face, hear their voice, read their name, or be told something about them by a
third party. All of these should activate the same knowledge. Without a convergence point, every
recognition route would need its own copy of the person's knowledge — and updating one copy
wouldn't update the others. The PIN solves this by separating recognition (multiple routes) from
knowledge (one place).

---

## Person knowledge in the anterior temporal lobes

The PIN as a functional concept needs a neural substrate. Research increasingly localises
**semantic person knowledge** — facts about individuals that are independent of how you recognised
them — to the **anterior temporal lobes (ATL)**.

Damage to the ATL causes semantic dementia: the gradual erosion of knowledge about specific
individuals, objects, and concepts. People lose access to names and biographical facts about famous
people, then increasingly about anyone. In severe cases, familiar faces become structurally
recognisable (the FRU fires) but carry no meaning — the face is familiar, but nothing is known
about the person behind it.

The ATL is not exclusively for people. It handles knowledge about specific individuals of any kind:
people, places, objects, events. The semantic person knowledge system is a specific instance of a
more general **named-entity knowledge** system.

---

## The generalisation: from persons to any named thing

The PIN model describes a person-specific architecture, but the underlying logic generalises
completely.

Any named thing — a company, a city, a species of bird, a piece of music, a product that doesn't
exist yet — has the same structure:
- Multiple ways it might be encountered or referred to (its "recognition routes")
- A convergence point where all of those routes lead
- A body of associated knowledge that activates when the convergence point is reached

The "zungleblootfop" that has never appeared in training data has no stored knowledge yet. But the
moment it is first encountered and named, a node can be created. Subsequent encounters via different
routes (the brand name, a description, a URL) converge on the same node. Knowledge accumulates
there. Spreading activation propagates outward from it when the node is activated.

This is not a metaphor. It is the same architecture as the PIN, generalised from person-nodes to
concept-nodes. The ATL research supports the generalisation — the region handles specific knowledge
about any kind of named entity, not only people.

---

## What this means for memory architecture

The convergence-point structure maps directly onto a knowledge node:

```
kg_nodes:    the concept node — person, place, thing, event, whatever
kg_aliases:  the multiple recognition routes — name variants, external IDs, voice signatures
kg_edges:    relationships between concept nodes — typed, with properties
kg_refs:     links from any memory record (observation, reflection, etc.) to a node
```

When Anima encounters "Drew" in a web UI message and "dangerworm" on Discord, both aliases point
to the same `kg_node`. Activation of either route activates the node. All associated memory records
— linked via `kg_refs` — become available for retrieval and spreading activation.

When Anima first reads about a zungleblootfop, she creates a node. As she encounters more
information about it across different conversations and sources, `kg_refs` accumulate on that node.
Querying "what do I know about zungleblootfops?" activates the node and traverses its refs.

The naming question — "what should we call the table?" — is answered by the neuroscience:
not "entities" (too person-specific), not "objects" (too physical), but **concept nodes**. Any
named thing Anima can have knowledge about.

---

## A note on temporal facts

Person Identity Nodes accumulate knowledge that is sometimes time-bounded. "Drew is going on
holiday" is true for a specific interval. "Drew prefers not to be contacted before 9am" may be a
long-standing fact. The PIN model doesn't specify how temporal facts are handled — that is a
separate concern addressed by bitemporal modeling.

But the connection is important: temporal facts about an entity should be stored in `kg_refs`
with `valid_from`/`valid_until` fields (or in a structured `temporal_context` field on the memory
record), so that queries can distinguish currently-valid facts from historical ones. The same
spreading activation that surfaces "Drew is going on holiday" should also surface how long ago
that was recorded and whether it's likely still true.

---

## Where to go deeper

- **Bruce, V. & Young, A. "Understanding Face Recognition" (1986)** — British Journal of
  Psychology; the foundational model; readable and clearly argued
- **Damasio, A.R. "The Brain Binds Entities and Events by Multiregional Activation from
  Convergence Zones" (1989)** — Damasio's convergence zone theory generalises the PIN concept
  to all knowledge; important predecessor to the ATL research
- **Patterson, K., Nestor, P.J., & Rogers, T.T. "Where do you know what you know? The
  representation of semantic knowledge in the human brain" (2007)** — Nature Reviews Neuroscience;
  comprehensive review of ATL and semantic knowledge systems
- **Hodges, J.R. & Patterson, K. "Semantic dementia: a unique clinicopathological syndrome"
  (2007)** — the clearest account of what happens when ATL knowledge systems degrade

---

## Relationship to other topics

- [Spreading Activation](spreading-activation.md) — the PIN is the node in the spreading activation
  network; activating a concept node propagates to all associated knowledge and related concepts
- [Autonoetic Consciousness & Episodic Memory](autonoetic-consciousness.md) — episodic memories
  are stored with temporal context; concept nodes are the anchors those memories attach to
- [Bitemporal Modeling](../technical/bitemporal-modeling.md) — temporal facts attached to concept
  nodes need valid-time tracking; the PIN model and bitemporality solve adjacent problems
- [Gärdenfors' Conceptual Spaces](../philosophy/gardenfors-conceptual-spaces.md) — conceptual
  spaces provide a continuous geometric account of concept structure; concept nodes are the
  discrete identities that exist within that space
